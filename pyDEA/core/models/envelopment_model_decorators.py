''' This module contains classes that implement VRS envelopment model,
    envelopment model with disposable variables and with various
    kind of weight restrictions.
'''
import pulp

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.data_processing.solution import SolutionWithVRS


class EnvelopmentModelVRSDecorator(EnvelopmentModelBase):
    ''' This class is a concrete implementation of VRS envelopment model.

        Attributes:
            _model_to_decorate (EnvelopmentModelBase): envelopment model.

        Args:
            model_to_decorate (EnvelopmentModelBase): envelopment model
                that needs to be decorated with VRS constraint.
    '''
    def __init__(self, model_to_decorate):
        self._model_to_decorate = model_to_decorate

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model
        variables = [self._model_to_decorate._variables[dmu_code] for dmu_code
                     in self.input_data.DMU_codes]

        self._model_to_decorate.lp_model += (pulp.lpSum(variables) == 1,
                                             'VRS_constraint')
        self.lp_model = self._model_to_decorate.lp_model

    def _create_solution(self):
        ''' Creates SolutionWithVRS instead of usual Solution in order to
            add extra information about VRS dual variable.

            Returns:
                SolutionWithVRS: solution that is able to store extra
                    information about VRS dual variable.
        '''
        basic_solution = super()._create_solution()
        return SolutionWithVRS(basic_solution)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Adds value of dual variable corresponding to VRS constraint to
            model_solution.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)
        model_solution.add_VRS_dual(
            dmu_code, self.lp_model.constraints['VRS_constraint'].pi)

    def _update_lp(self, dmu_code):
        ''' Updates LP with coefficients corresponding to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._update_lp(dmu_code)

    def _add_constraints_for_outputs(self, variables, dmu_code,
                                     obj_variable):
        ''' Adds constraints for outputs to linear program.

            Args:
                variables (dict of str to pulp.LpVariable): a dictionary
                    that maps DMU codes to pulp.LpVariable, created with
                    pulp.LpVariable.dicts.
                dmu_code (str): DMU code for which LP is being created.
                obj_variable (pulp.LpVariable): LP variable that is optimised
                    (either efficiency score or inverse of efficiency score).
        '''
        self._model_to_decorate._add_constraints_for_outputs(variables,
                                                             dmu_code,
                                                             obj_variable)

    def _add_constraints_for_inputs(self, variables,
                                    dmu_code, obj_variable):
        ''' Adds constraints for inputs to LP.

            Args:
                variables (dict of {str: pulp.LpVariable}): a dictionary that
                    maps DMU codes to pulp.LpVariable, created with
                    pulp.LpVariable.dicts.
                dmu_code (str): DMU code for which LP is being created.
                obj_variable (pulp.LpVariable): LP variable that is optimised
                    (either efficiency score or inverse of efficiency score).
        '''
        self._model_to_decorate._add_constraints_for_inputs(variables,
                                                            dmu_code,
                                                            obj_variable)

    def _process_duals(self, dmu_code, categories, func):
        ''' Helper function that adds duals to solution using given method func.
            Helps to avoid code duplication.

            Args:
                dmu_code (str): DMU code under consideration.
                categories (list of str): list of either input or output
                    categories.
                func (function): a function that accepts DMU code, category and
                    dual variable value and adds it to solution.
        '''
        self._model_to_decorate._process_duals(dmu_code, categories, func)


class DefaultConstraintCreator(object):
    ''' This is a helper class that creates constraints for envelopment model
        with strongly disposable categories.
    '''
    def create(self, lhs, rhs, category):
        ''' By default all categories are strongly disposable.
            Hence all constraints have the form lhs >= rhs.

            Args:
                lhs (pulp.LpAffineExpression): left hand side of the constraint.
                rhs (pulp.LpAffineExpression): right hand side of the
                    constraint.
                category(str): input or output category (it is not used by
                    this class).
        '''
        return lhs >= rhs


class DisposableVarsConstraintCreator(object):
    ''' This is a helper class that creates constraints for envelopment model
        with weakly disposable categories.

        Attributes:
            weakly_disposable_categories (set of str): list of weakly
                disposable categories.

        Args:
            weakly_disposable_categories (list of str): list of weakly
                disposable categories.
    '''
    def __init__(self, weakly_disposable_categories):
        assert(weakly_disposable_categories)
        self.weakly_disposable_categories = weakly_disposable_categories

    def create(self, lhs, rhs, category):
        ''' If category is weakly disposable, returns constraint of the form
            lhs == rhs, otherwise: lhs >= rhs.

            Args:
                lhs (pulp.LpAffineExpression): left hand side of the constraint.
                rhs (pulp.LpAffineExpression): right hand side of the
                    constraint.
                category (str): input or output category.
        '''
        if category in self.weakly_disposable_categories:
            return lhs == rhs
        return lhs >= rhs


class EnvelopmentModelWithAbsoluteWeightRestrictions(EnvelopmentModelBase):
    ''' This class implements envelopment model with absolute weight
        restrictions.

        Attributes:
            model (EnvelopmentModelBase): envelopment model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
            new_vars_lb (dict of str to pulp.LpVariable): dictionary that maps
                category name to a pulp variable.
            new_vars_ub (dict of str to pulp.LpVariable): dictionary that maps
                category name to a pulp variable.

        Args:
            model_to_decorate (EnvelopmentModelBase): envelopment model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
    '''
    def __init__(self, model_to_decorate, bounds):
        self.model = model_to_decorate
        self.bounds = bounds
        self.new_vars_lb = dict()
        self.new_vars_ub = dict()
        self._multiplier = None

    def __getattr__(self, name):
        return getattr(self.model, name)

    def _create_lp(self):
        ''' See base class.
        '''
        self.model._create_lp()
        self.lp_model = self.model.lp_model
        self.new_vars_lb.clear()
        self.new_vars_ub.clear()
        for elem in self.input_data.DMU_codes:
            dmu_code = elem
            break

        if self._concrete_model.get_orientation() == 'input': 
            self._multiplier = 1
        else:
            self._multiplier = -1

        # make objective variable unrestricted 
        self._variables['obj_var'].lowBound = None
        self._variables['obj_var'].upBound = None

        for category, (lower_bound, upper_bound) in self.bounds.items():
            if lower_bound:
                variable = pulp.LpVariable(
                    '{0}_category_{1}_lb'.format(
                        self._get_var_name(), category),
                    None, 0, pulp.LpContinuous)
                self.new_vars_lb[category] = variable
                name = self.model._constraints[category]
                self.lp_model.constraints[name].addterm(variable, 1)
                self.lp_model.objective += (self._get_multiplier(
                                            dmu_code, category) *
                                            lower_bound * variable)

            if upper_bound:
                variable = pulp.LpVariable(
                    '{0}_category_{1}_ub'.format(self._get_var_name(),
                                                 category),
                    0, None, pulp.LpContinuous)
                self.new_vars_ub[category] = variable
                name = self.model._constraints[category]
                self.lp_model.constraints[name].addterm(variable, 1)
                self.lp_model.objective += (self._get_multiplier(
                                            dmu_code, category) *
                                            upper_bound * variable)
        #if self._multiplier == -1:
            # add constraint that objective function is >= 1 for
            # output-oriented model
         #   self.lp_model += self.lp_model.objective >= 1


    def _update_lp(self, dmu_code):
        ''' See base class.
        '''
        self.model._update_lp(dmu_code)
        for category, (lower_bound, upper_bound) in self.bounds.items():
            if lower_bound:
                variable = self.new_vars_lb[category]
                self.lp_model.objective[variable] = (self._get_multiplier(
                                                     dmu_code, category) *
                                                     lower_bound)

            if upper_bound:
                variable = self.new_vars_ub[category]
                self.lp_model.objective[variable] = (self._get_multiplier(
                                                     dmu_code, category) *
                                                     upper_bound)

    def _create_solution(self):
        ''' See base class.
        '''
        return self.model._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' See base class.
        '''
        self.model._fill_solution(dmu_code, model_solution)

    def _get_multiplier(self, dmu_code, category):
        ''' Returns a multiplier used in the model objective function.

            Args:
                dmu_code (str): DMU code.
                category (str): category name.
        '''
        return self._multiplier

    def _get_var_name(self):
        ''' Returns base for a variable name.

            Returns:
                str: base for a variable name.
        '''
        return 'abs'

    def _add_constraints_for_outputs(self, variables, dmu_code,
                                     obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_outputs(variables, dmu_code,
                                                obj_variable)

    def _add_constraints_for_inputs(self, variables,
                                    dmu_code, obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_inputs(variables, dmu_code,
                                               obj_variable)

    def _process_duals(self, dmu_code, categories, func):
        ''' See base class.
        '''
        self.model._process_duals(dmu_code, categories, func)


class EnvelopmentModelWithVirtualWeightRestrictions(
        EnvelopmentModelWithAbsoluteWeightRestrictions):
    ''' This class implements envelopment model with virtual weight
        restrictions.
    '''
    def _get_multiplier(self, dmu_code, category):
        ''' Returns a multiplier used in the model objective function.

            Args:
                dmu_code (str): DMU code.
                category (str): category name.
        '''
        return self._multiplier / self.model.input_data.coefficients[dmu_code, category]

    def _get_var_name(self):
        ''' Returns base for a variable name.

            Returns:
                str: base for a variable name.
        '''
        return 'virtual'


class EnvelopmentModelWithPriceRatioConstraints(EnvelopmentModelBase):
    ''' This class implements envelopment model with price ratio weight
        restrictions.

        Attributes:
            model (EnvelopmentModelBase): envelopment model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
        Args:
            model_to_decorate (EnvelopmentModelBase): envelopment model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
    '''
    def __init__(self, model_to_decorate, bounds):
        self.model = model_to_decorate
        self.bounds = bounds

    def __getattr__(self, name):
        return getattr(self.model, name)

    def _create_lp(self):
        ''' See base class.
        '''
        self.model._create_lp()
        self.lp_model = self.model.lp_model

        # create varibales
        for (category_in_nom, category_in_denom), (lower_bound, upper_bound) in self.bounds.items():
            if lower_bound:
                variable = pulp.LpVariable(
                    'price_ratio_category_{0}_{1}_lb'.format(
                        category_in_nom, category_in_denom),
                    0, None, pulp.LpContinuous)
                name = self.model._constraints[category_in_nom]
                self.lp_model.constraints[name].addterm(variable, -1)
                name = self.model._constraints[category_in_denom]
                self.lp_model.constraints[name].addterm(variable, lower_bound)

            if upper_bound:
                variable = pulp.LpVariable(
                    'price_ratio_category_{0}_{1}_ub'.format(
                        category_in_nom, category_in_denom),
                    0, None, pulp.LpContinuous)
                name = self.model._constraints[category_in_nom]
                self.lp_model.constraints[name].addterm(variable, 1)
                name = self.model._constraints[category_in_denom]
                self.lp_model.constraints[name].addterm(variable, -upper_bound)

    def _create_solution(self):
        ''' See base class.
        '''
        return self.model._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' See base class.
        '''
        self.model._fill_solution(dmu_code, model_solution)

    def _update_lp(self, dmu_code):
        ''' See base class.
        '''
        self.model._update_lp(dmu_code)

    def _add_constraints_for_outputs(self, variables, dmu_code,
                                     obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_outputs(variables, dmu_code,
                                                obj_variable)

    def _add_constraints_for_inputs(self, variables,
                                    dmu_code, obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_inputs(variables, dmu_code,
                                               obj_variable)

    def _process_duals(self, dmu_code, categories, func):
        ''' See base class.
        '''
        self.model._process_duals(dmu_code, categories, func)
