''' This module contains classes responsible for creating a
    proper DEA model.
'''


from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOriented
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOrientedWithNonDiscVars
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOrientedWithNonDiscVars
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelVRSDecorator
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import DisposableVarsConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelWithAbsoluteWeightRestrictions
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelWithVirtualWeightRestrictions
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelWithPriceRatioConstraints
from pyDEA.core.models.multiplier_model import MultiplierInputOrientedModel
from pyDEA.core.models.multiplier_model import MultiplierOutputOrientedModel
from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelVRSDecorator
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithDisposableCategories
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithAbsoluteWeightRestrictions
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithVirtualWeightRestrictions
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithPriceRatioConstraints
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelInputOrientedWithNonDiscVars
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelOutputOrientedWithNonDiscVars
from pyDEA.core.models.bound_generators import generate_supper_efficiency_upper_bound
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.models.bound_generators import generate_supper_efficiency_lower_bound
from pyDEA.core.models.bound_generators import generate_lower_bound_for_efficiency_score
from pyDEA.core.models.super_efficiency_model import SupperEfficiencyModel
from pyDEA.core.models.maximize_slacks import MaximizeSlacksModel
from pyDEA.core.models.categorical_dmus import ModelWithCategoricalDMUs
import pyDEA.core.utils.dea_utils as dea_utils


def add_input_and_output_categories(params, model_input):
    ''' Adds input and output categories specified in parameters
        to a given InputData object.

        Args:
            params (Parameters): model parameters.
            model_input (InputData): object that stores input data.

        Raises:
            ValueError: if input or output (or both) categories
                are missing.
    '''
    input_categories = params.get_set_of_parameters('INPUT_CATEGORIES')
    for category in input_categories:
        model_input.add_input_category(category)
    output_categories = params.get_set_of_parameters('OUTPUT_CATEGORIES')
    for category in output_categories:
        model_input.add_output_category(category)
    if (len(model_input.input_categories) == 0 or
            len(model_input.output_categories) == 0):
        raise ValueError('Both input and output categories must be specified')


class ModelFactoryBase(object):
    ''' Abstract base class for factory classes responsible for creating
        a DEA model.
    '''
    @classmethod
    def create_model(cls, params, model_input):
        ''' Allocated a proper DEA model given parameters and input data.

            Args:
                params (Parameters): model parameters.
                model_input (InputData): object that stores input data.

            Returns:
                ModelBase: allocated DEA model.
        '''
        orientation = params.get_parameter_value('ORIENTATION')
        non_discr_categories = params.get_set_of_parameters(
            'NON_DISCRETIONARY_CATEGORIES')
        weakly_disposal_categories = params.get_set_of_parameters(
            'WEAKLY_DISPOSAL_CATEGORIES')
        if weakly_disposal_categories:
            dea_utils.check_categories(weakly_disposal_categories,
                                       model_input.categories)
        use_super_efficiency = params.get_parameter_value(
            'USE_SUPER_EFFICIENCY')

        if orientation == 'input':
            if non_discr_categories:
                dea_utils.check_categories(non_discr_categories,
                                           model_input.input_categories,
                                           'For input-oriented model only'
                                           ' input categories can be'
                                           ' non-discretionary')
            concrete_model = cls.get_input_oriented_model(
                use_super_efficiency, non_discr_categories)
        elif orientation == 'output':
            if non_discr_categories:
                dea_utils.check_categories(non_discr_categories,
                                           model_input.output_categories,
                                           'For output-oriented model only'
                                           ' output categories can be'
                                           ' non-discretionary')
            concrete_model = cls.get_output_oriented_model(
                use_super_efficiency, non_discr_categories)
        else:
            raise ValueError('Unexpected value of parameter <ORIENTATION>')

        model = cls.get_basic_model(model_input, concrete_model,
                                    weakly_disposal_categories, params)
        model = cls.add_extra(model, weakly_disposal_categories,
                              non_discr_categories, orientation)

        # add decorators if needed
        return_to_scale = params.get_parameter_value('RETURN_TO_SCALE')
        if return_to_scale == 'VRS':
            model = cls.get_VRS_model(model)

        abs_restrictions = params.get_set_of_parameters(
            'ABS_WEIGHT_RESTRICTIONS')
        if abs_restrictions:
            bounds = dea_utils.create_bounds(abs_restrictions,
                                             model_input.categories)
            model = cls.get_abs_restriction_model(model, bounds)

        virtual_restrictions = params.get_set_of_parameters(
            'VIRTUAL_WEIGHT_RESTRICTIONS')
        if virtual_restrictions:
            bounds = dea_utils.create_bounds(virtual_restrictions,
                                             model_input.categories)
            model = cls.get_virtual_restriction_model(model, bounds)

        price_ratio_restrictions = params.get_set_of_parameters(
            'PRICE_RATIO_RESTRICTIONS')
        if price_ratio_restrictions:
            bounds = dea_utils.create_bounds(price_ratio_restrictions,
                                             model_input.categories)
            model = cls.get_price_ratio_model(model, bounds)

        if use_super_efficiency:
            model = SupperEfficiencyModel(model)

        # It is important to create max slack model after duper efficiency,
        # otherwise wrong type of solution is created
        maximize_slacks = params.get_parameter_value('MAXIMIZE_SLACKS')
        if maximize_slacks:
            if params.get_parameter_value('DEA_FORM') == 'multi':
                raise ValueError(
                    "Two phase model doesn't work with multiplier model")
            model = MaximizeSlacksModel(model, weakly_disposal_categories)

        categorical_category = params.get_parameter_value(
            'CATEGORICAL_CATEGORY')
        if categorical_category:
            model = ModelWithCategoricalDMUs(model, categorical_category)

        return model

    @classmethod
    def get_input_oriented_model(cls, use_super_efficiency,
                                 non_discr_categories):
        ''' Returns input-oriented model used in ModelBase.

            Args:
                use_super_efficiency (bool): true if super efficiency model
                    should be created, false otherwise.
                non_discr_categories (list of str): list of non-discretionary
                    categories. If empty, all categories are considered
                    discretionary.

            Returns:
                InputOrientedModel: allocated input-oriented model.
        '''
        raise NotImplementedError()

    @classmethod
    def get_output_oriented_model(cls, use_super_efficiency,
                                  non_discr_categories):
        ''' Returns output-oriented model used in ModelBase.

            Args:
                use_super_efficiency (bool): true if super efficiency model
                    should be created, false otherwise.
                non_discr_categories (list of str): list of non-discretionary
                    categories. If empty, all categories are considered
                    discretionary.

            Returns:
                OutputOrientedModel: allocated output-oriented model.
        '''
        raise NotImplementedError()

    @classmethod
    def get_basic_model(cls, model_input, concrete_model,
                        weakly_disposal_categories, params):
        ''' Returns allocated basic CRS DEA model.

            Args:
                model_input (InputData): object that stores input data.
                concrete_model (InputOrientedModel or OutputOrientedModel):
                    input- or output-oriented model used in ModelBase.
                weakly_disposal_categories (list of str): list of weakly
                    disposal categories. If empty, all categories are considered
                    strongly disposal.
                params (Parameters): model parameters.

            Returns:
                ModelBase: allocated DEA model.
        '''
        raise NotImplementedError()

    @classmethod
    def get_VRS_model(cls, model):
        ''' Decorates a given model with VRS constraints or variables.

            Args:
                model (ModelBase): model to decorate.

            Returns:
                ModelBase: decorated VRS DEA model.
        '''
        raise NotImplementedError()

    @classmethod
    def get_abs_restriction_model(cls, model, bounds):
        ''' Decorates a given model with absolute weight restrictions.

            Args:
                model (ModelBase): model to decorate.
                bounds (dict of str to tuple of double, double or dict of tuple of str, str to tuple of double, double): dictionary with
                        parsed values of constraints.

            Returns:
                ModelBase: decorated DEA model with absolute weight
                    restrictions.
        '''
        raise NotImplementedError()

    @classmethod
    def get_virtual_restriction_model(cls, model, bounds):
        ''' Decorates a given model with virtual weight restrictions.

            Args:
                model (ModelBase): model to decorate.
                bounds (dict of str to tuple of double, double or dict of tuple of str, str to tuple of double, double): dictionary with
                    parsed values of constraints.

            Returns:
                ModelBase: decorated DEA model with virtual weight
                    restrictions.
        '''
        raise NotImplementedError()

    @classmethod
    def get_price_ratio_model(cls, model, bounds):
        ''' Decorates a given model with price ratio weight restrictions.

            Args:
                model (ModelBase): model to decorate.
                bounds (dict of str to tuple of double, double or dict of tuple of str, str to tuple of double, double): dictionary with
                    parsed values of constraints.

            Returns:
                ModelBase: decorated DEA model with price ratio weight
                    restrictions.
        '''
        raise NotImplementedError()

    @classmethod
    def add_extra(cls, model, weakly_disposal_categories,
                  non_discr_categories, orientation):
        ''' Helper method that is called after get_basic_model.

            Args:
                model (ModelBase): model to decorate.
                weakly_disposal_categories (list of str): list of weakly
                    disposal categories. If empty, all categories are considered
                    strongly disposal.
                non_discr_categories (list of str): list of non-discretionary
                    categories. If empty, all categories are considered
                    discretionary.
                orientation (str): string that describes orientation of the
                    model. Possible values: "input" or "output".

            Returns:
                ModelBased: decorated DEA model.
        '''
        raise NotImplementedError()


class EnvelopmentModelFactory(ModelFactoryBase):

    ''' A factory class responsible for creating envelopment model.
    '''
    @staticmethod
    def get_upper_bound_generator_for_env_model(use_super_efficiency):
        ''' Returns a function for upper bound generation for
            envelopment model.

            Args:
                use_super_efficiency (bool): true if super efficiency model
                    should be created, false otherwise.

            Returns:
                func: function for upper bound generation.
        '''
        if use_super_efficiency:
            return generate_supper_efficiency_upper_bound
        else:
            return generate_upper_bound_for_efficiency_score

    @staticmethod
    def get_lower_bound_generator(use_super_efficiency):
        ''' Returns a function for lower bound generation for
            envelopment model.

            Args:
                use_super_efficiency (bool): true if super efficiency model
                    should be created, false otherwise.

            Returns:
                func: function for lower bound generation.
        '''
        if use_super_efficiency:
            return generate_supper_efficiency_lower_bound
        else:
            return generate_lower_bound_for_efficiency_score

    @classmethod
    def get_input_oriented_model(cls, use_super_efficiency,
                                 non_discr_categories):
        ''' See base class.
        '''
        upper_bound_generator = cls.get_upper_bound_generator_for_env_model(
            use_super_efficiency)
        if non_discr_categories:
            return EnvelopmentModelInputOrientedWithNonDiscVars(
                non_discr_categories, upper_bound_generator)
        return EnvelopmentModelInputOriented(upper_bound_generator)

    @classmethod
    def get_output_oriented_model(cls, use_super_efficiency,
                                  non_discr_categories):
        ''' See base class.
        '''
        lower_bound_generator = cls.get_lower_bound_generator(
            use_super_efficiency)
        if non_discr_categories:
            return EnvelopmentModelOutputOrientedWithNonDiscVars(
                non_discr_categories, lower_bound_generator)
        return EnvelopmentModelOutputOriented(lower_bound_generator)

    @classmethod
    def get_basic_model(cls, model_input, concrete_model,
                        weakly_disposal_categories, params):
        ''' See base class.
        '''
        if weakly_disposal_categories:
            constraint_creator = DisposableVarsConstraintCreator(
                weakly_disposal_categories)
        else:
            constraint_creator = DefaultConstraintCreator()
        return EnvelopmentModelBase(model_input, concrete_model,
                                    constraint_creator)

    @classmethod
    def get_VRS_model(cls, model):
        ''' See base class.
        '''
        return EnvelopmentModelVRSDecorator(model)

    @classmethod
    def get_abs_restriction_model(cls, model, bounds):
        ''' See base class.
        '''
        return EnvelopmentModelWithAbsoluteWeightRestrictions(model, bounds)

    @classmethod
    def get_virtual_restriction_model(cls, model, bounds):
        ''' See base class.
        '''
        return EnvelopmentModelWithVirtualWeightRestrictions(model, bounds)

    @classmethod
    def get_price_ratio_model(cls, model, bounds):
        ''' See base class.
        '''
        return EnvelopmentModelWithPriceRatioConstraints(model, bounds)

    @classmethod
    def add_extra(cls, model, weakly_disposal_categories,
                  non_discr_categories, orientation):
        ''' See base class.
        '''
        return model


class MultiplierModelFactory(ModelFactoryBase):
    ''' A factory class responsible for creating multiplier model.
    '''
    @classmethod
    def get_input_oriented_model(cls, use_super_efficiency,
                                 non_discr_categories):
        ''' See base class.
        '''
        return MultiplierInputOrientedModel()

    @classmethod
    def get_output_oriented_model(cls, use_super_efficiency,
                                  non_discr_categories):
        ''' See base class.
        '''
        return MultiplierOutputOrientedModel()

    @classmethod
    def get_basic_model(cls, model_input, concrete_model,
                        weakly_disposal_categories, params):
        ''' See base class.
        '''
        tolerance = float(params.get_parameter_value(
            'MULTIPLIER_MODEL_TOLERANCE'))
        return MultiplierModelBase(model_input, tolerance, concrete_model)

    @classmethod
    def get_VRS_model(cls, model):
        ''' See base class.
        '''
        return MultiplierModelVRSDecorator(model)

    @classmethod
    def get_abs_restriction_model(cls, model, bounds):
        ''' See base class.
        '''
        return MultiplierModelWithAbsoluteWeightRestrictions(model, bounds)

    @classmethod
    def get_virtual_restriction_model(cls, model, bounds):
        ''' See base class.
        '''
        return MultiplierModelWithVirtualWeightRestrictions(model, bounds)

    @classmethod
    def get_price_ratio_model(cls, model, bounds):
        ''' See base class.
        '''
        return MultiplierModelWithPriceRatioConstraints(model, bounds)

    @classmethod
    def add_extra(cls, model, weakly_disposal_categories,
                  non_discr_categories, orientation):
        ''' See base class.
        '''
        new_model = model
        if weakly_disposal_categories:
            new_model = MultiplierModelWithDisposableCategories(
                model, weakly_disposal_categories)

        if non_discr_categories:
            if orientation == 'input':
                new_model = MultiplierModelInputOrientedWithNonDiscVars(
                    new_model, non_discr_categories)
            else:
                new_model = MultiplierModelOutputOrientedWithNonDiscVars(
                    new_model, non_discr_categories)
        return new_model


def create_model(params, model_input):
        ''' Allocates a proper DEA model based on given parameters and
            input data. This function must be used for creating DEA model.
            It calls appropriate factory class.

            Args:
                params (Parameters): model parameters.
                model_input (InputData): object that stores input data.

            Raises:
                ValueError: if DEA form parameter has invalid value.
                    Allowed values are env and multi.

            Returns:
                ModelBase: allocated DEA model.
        '''
        dea_form = params.get_parameter_value('DEA_FORM')
        if dea_form == 'env':
            return EnvelopmentModelFactory.create_model(params, model_input)
        elif dea_form == 'multi':
            return MultiplierModelFactory.create_model(params, model_input)
        else:
            raise ValueError('Invalid value of parameter <DEA_FORM>')
