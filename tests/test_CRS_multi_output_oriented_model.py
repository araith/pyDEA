import pytest


from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierOutputOrientedModel
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithDisposableCategories
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelOutputOrientedWithNonDiscVars
from pyDEA.core.data_processing.read_data_from_xls import read_data, convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests
from tests.utils_for_tests import DEA_example2_data


@pytest.fixture
def model(request, data):
    model = MultiplierModelBase(data, 1e-12,
                                MultiplierOutputOrientedModel())
    return model


def test_CRS_multi_output_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 1 / 1.199999982, 1 / 1.4, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'B', 1.2, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'E', 0.6, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'B', 0.3, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'E', 0.4, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [1, 0, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'B', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.066666667,  0.13333333,
                                             0.33333333],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'D', ['x1', 'x2', 'q'], [0.2, 0.4, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)


def test_CRS_multi_output_oriented_with_weakly_disposable_vars_small(data):
    model = MultiplierModelWithDisposableCategories(
        MultiplierModelBase(data, 1e-12,
                            MultiplierOutputOrientedModel()), set(['x1']))
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 0.8333333458, 0.7142857143, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'B', 1.2, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'E', 0.6, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'B', 0.3, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'E', 0.4, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [1, 0, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'B', ['x1', 'x2', 'q'], [0.5, 0, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.066666667, 0.13333333,
                                             0.33333333], model_solution,
                                             data)
    utils_for_tests.check_categories_for_dmu(
        'D', ['x1', 'x2', 'q'], [0.2, 0.4, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)


def test_CRS_multi_output_oriented_with_non_discretionary_vars_with_error(data):
    with pytest.raises(ValueError) as excinfo:
        model = MultiplierModelOutputOrientedWithNonDiscVars(
            MultiplierModelBase(data, 1e-12,
                                MultiplierOutputOrientedModel()), set(['q']))

    assert str(
        excinfo.value) == ('Too many non-discretionary categories. At least'
                          ' one output must be discretionary')


def _create_large_model_CRS_multi_output_oriented_with_non_discretionary(
        DEA_example2_data):
    DEA_example2_data.add_input_category('I1')
    DEA_example2_data.add_input_category('I2')
    DEA_example2_data.add_input_category('I3')
    DEA_example2_data.add_output_category('O1')
    DEA_example2_data.add_output_category('O2')
    model = MultiplierModelOutputOrientedWithNonDiscVars(
        MultiplierModelBase(DEA_example2_data, 1e-12,
                            MultiplierOutputOrientedModel()), set(['O1']))
    return model


def _check_large_model_CRS_multi_output_oriented_with_non_discretionary(
        model_solution, data):
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.3085412442,
                                                   0.8305229413,
                                                   1, 0.5294117616,
                                                   1, 1, 0.1538535738, 1,
                                                   0.2627956766, 1],
                                            model_solution, data)


def test_CRS_multi_output_oriented_with_non_discretionary_vars(
        DEA_example2_data):
    model = _create_large_model_CRS_multi_output_oriented_with_non_discretionary(
        DEA_example2_data)
    model_solution = model.run()
    _check_large_model_CRS_multi_output_oriented_with_non_discretionary(
        model_solution, model.input_data)


def test_with_zero_data():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/with_zeros.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('rein')
    data.add_output_category('aus')
    model = MultiplierModelBase(data, 0,
                                MultiplierOutputOrientedModel())
    model_solution = model.run()
    clean_up_pickled_files()
