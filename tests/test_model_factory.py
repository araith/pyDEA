import pytest

import pyDEA.core.utils.model_factory as factory
from pyDEA.core.data_processing.parameters import Parameters
from pyDEA.core.models.bound_generators import generate_supper_efficiency_upper_bound
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.models.bound_generators import generate_supper_efficiency_lower_bound
from pyDEA.core.models.bound_generators import generate_lower_bound_for_efficiency_score
from pyDEA.core.models.peel_the_onion import peel_the_onion_method

from tests.utils_for_tests import DEA_example_data


def test_add_input_and_output_categories(DEA_example_data):
    allParams = Parameters()
    allParams.update_parameter('INPUT_CATEGORIES', 'I1; I2')
    allParams.update_parameter('OUTPUT_CATEGORIES', 'O1; O2')
    factory.add_input_and_output_categories(allParams, DEA_example_data)
    assert 'I1' in DEA_example_data.input_categories
    assert 'I2' in DEA_example_data.input_categories
    assert 'O1' in DEA_example_data.output_categories
    assert 'O2' in DEA_example_data.output_categories


def test_add_empty_input_and_output_categories(DEA_example_data):
    allParams = Parameters()
    allParams.update_parameter('INPUT_CATEGORIES', '')
    allParams.update_parameter('OUTPUT_CATEGORIES', 'O1; O2')
    with pytest.raises(ValueError) as excinfo:
        factory.add_input_and_output_categories(allParams, DEA_example_data)
    assert str(
        excinfo.value) == 'Both input and output categories must be specified'


@pytest.fixture
def params(request):
    params = Parameters()
    params.update_parameter('INPUT_CATEGORIES', 'I1; I2')
    params.update_parameter('OUTPUT_CATEGORIES', 'O1; O2')
    params.update_parameter('DEA_FORM', 'env')
    params.update_parameter('RETURN_TO_SCALE', 'CRS')
    params.update_parameter('ORIENTATION', 'input')
    params.update_parameter('NON_DISCRETIONARY_CATEGORIES', '')
    params.update_parameter('WEAKLY_DISPOSAL_CATEGORIES', '')
    params.update_parameter('USE_SUPER_EFFICIENCY', '')
    params.update_parameter('ABS_WEIGHT_RESTRICTIONS', '')
    params.update_parameter('VIRTUAL_WEIGHT_RESTRICTIONS', '')
    params.update_parameter('PRICE_RATIO_RESTRICTIONS', '')
    params.update_parameter('MAXIMIZE_SLACKS', '')
    params.update_parameter('MULTIPLIER_MODEL_TOLERANCE', '0')
    params.update_parameter('CATEGORICAL_CATEGORY', '')
    params.update_parameter('PEEL_THE_ONION', '')

    return params


def test_create_model(params, DEA_example_data):
    factory.add_input_and_output_categories(params, DEA_example_data)
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'EnvelopmentModelBase'
    assert model._concrete_model.__class__.__name__ == 'EnvelopmentModelInputOriented'
    assert model._constraint_creator.__class__.__name__ == 'DefaultConstraintCreator'
    params.update_parameter('DEA_FORM', 'multi')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelBase'
    assert model._concrete_model.__class__.__name__ == 'MultiplierInputOrientedModel'


def test_create_model_VRS(params, DEA_example_data):
    params.update_parameter('RETURN_TO_SCALE', 'VRS')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'EnvelopmentModelVRSDecorator'
    params.update_parameter('DEA_FORM', 'multi')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelVRSDecorator'


def test_create_model_weigth_restrictions(params, DEA_example_data):
    params.update_parameter('ABS_WEIGHT_RESTRICTIONS',
                            'I1 >= 1; I2 <= 10; I1 <= 7')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'EnvelopmentModelWithAbsoluteWeightRestrictions'
    params.update_parameter('VIRTUAL_WEIGHT_RESTRICTIONS',
                            'I1 >= 1; I2 <= 10; I1 <= 7')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'EnvelopmentModelWithVirtualWeightRestrictions'
    assert model.model.__class__.__name__ == 'EnvelopmentModelWithAbsoluteWeightRestrictions'
    params.update_parameter('PRICE_RATIO_RESTRICTIONS',
                            'I1/I2 >= 1; I2/I1 <= 10; I1/I2 <= 7')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'EnvelopmentModelWithPriceRatioConstraints'
    assert model.model.__class__.__name__ == 'EnvelopmentModelWithVirtualWeightRestrictions'
    params.update_parameter('DEA_FORM', 'multi')
    params.update_parameter('VIRTUAL_WEIGHT_RESTRICTIONS', '')
    params.update_parameter('PRICE_RATIO_RESTRICTIONS', '')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelWithAbsoluteWeightRestrictions'
    params.update_parameter('VIRTUAL_WEIGHT_RESTRICTIONS',
                            'I1 >= 1; I2 <= 10; I1 <= 7')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelWithVirtualWeightRestrictions'
    assert model._model_to_decorate.__class__.__name__ == 'MultiplierModelWithAbsoluteWeightRestrictions'
    params.update_parameter('PRICE_RATIO_RESTRICTIONS',
                            'I1/I2 >= 1; I2/I1 <= 10; I1/I2 <= 7')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelWithPriceRatioConstraints'
    assert model._model_to_decorate.__class__.__name__ == 'MultiplierModelWithVirtualWeightRestrictions'


def test_orientation_and_non_disc_variables(params, DEA_example_data):
    factory.add_input_and_output_categories(params, DEA_example_data)
    params.update_parameter('ORIENTATION', 'output')
    model = factory.create_model(params, DEA_example_data)
    assert model._concrete_model.__class__.__name__ == 'EnvelopmentModelOutputOriented'
    params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'O1')
    model = factory.create_model(params, DEA_example_data)
    assert model._concrete_model.__class__.__name__ == 'EnvelopmentModelOutputOrientedWithNonDiscVars'
    params.update_parameter('ORIENTATION', 'input')
    params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'I2')
    model = factory.create_model(params, DEA_example_data)
    assert model._concrete_model.__class__.__name__ == 'EnvelopmentModelInputOrientedWithNonDiscVars'
    params.update_parameter('ORIENTATION', 'not valid value')
    with pytest.raises(ValueError) as excinfo:
        model = factory.create_model(params, DEA_example_data)
    assert str(excinfo.value) == 'Unexpected value of parameter <ORIENTATION>'


def test_orientation_and_non_disc_variables_multiplier_model(
        params, DEA_example_data):
    params.update_parameter('DEA_FORM', 'multi')
    factory.add_input_and_output_categories(params, DEA_example_data)
    params.update_parameter('ORIENTATION', 'output')
    model = factory.create_model(params, DEA_example_data)
    assert model._concrete_model.__class__.__name__ == 'MultiplierOutputOrientedModel'
    params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'O1')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelOutputOrientedWithNonDiscVars'
    params.update_parameter('ORIENTATION', 'input')
    params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'I2')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelInputOrientedWithNonDiscVars'
    params.update_parameter('ORIENTATION', 'not valid value')
    with pytest.raises(ValueError) as excinfo:
        model = factory.create_model(params, DEA_example_data)
    assert str(excinfo.value) == 'Unexpected value of parameter <ORIENTATION>'


def test_weakly_disposal_categories_creation(params, DEA_example_data):
    factory.add_input_and_output_categories(params, DEA_example_data)
    params.update_parameter('WEAKLY_DISPOSAL_CATEGORIES', 'I1; O2')
    model = factory.create_model(params, DEA_example_data)
    assert model._constraint_creator.__class__.__name__ == 'DisposableVarsConstraintCreator'
    params.update_parameter('DEA_FORM', 'multi')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MultiplierModelWithDisposableCategories'


def test_max_slacks_creation(params, DEA_example_data):
    params.update_parameter('MAXIMIZE_SLACKS', 'yes')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'MaximizeSlacksModel'


def test_super_efficiency_creation(params, DEA_example_data):
    params.update_parameter('USE_SUPER_EFFICIENCY', 'yes')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'SupperEfficiencyModel'


def test_invalid_dea_form(params, DEA_example_data):
    params.update_parameter('DEA_FORM', 'invalid')
    with pytest.raises(ValueError) as excinfo:
        model = factory.create_model(params, DEA_example_data)
    assert str(excinfo.value) == 'Invalid value of parameter <DEA_FORM>'


def test_categorical_model_creation(params, DEA_example_data):
    params.update_parameter('CATEGORICAL_CATEGORY', 'I1')
    model = factory.create_model(params, DEA_example_data)
    assert model.__class__.__name__ == 'ModelWithCategoricalDMUs'


def test_peel_the_onion_creation(params, DEA_example_data):
    params.update_parameter('PEEL_THE_ONION', 'yes')
    factory.add_input_and_output_categories(params, DEA_example_data)
    model = factory.create_model(params, DEA_example_data)
    peel_the_onion_method(model)
