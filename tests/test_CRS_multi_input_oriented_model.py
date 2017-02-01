import pytest

from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierInputOrientedModel
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithDisposableCategories
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelInputOrientedWithNonDiscVars
from pyDEA.core.data_processing.read_data_from_xls import read_data, convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = MultiplierModelBase(data, 1e-12,
                                MultiplierInputOrientedModel())
    return model


def test_CRS_multi_input_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 0.83333334, 0.71428571, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 0.5, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'E', 0.5, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'D', 'B', 0.21428571, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'D', 'E', 0.28571429, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [0.5, 0, 0.5], model_solution, data)
    # not the same in Python3
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.055555556, 0.11111111,
                                             0.27777778],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu('D', ['x1', 'x2', 'q'], [
                                             0.14285714, 0.28571429,
                                             0.71428571],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0, 0.5, 0.5], model_solution, data)


def test_CRS_multi_input_oriented_with_weakly_disposable_vars_small(data):
    model = MultiplierModelWithDisposableCategories(
        MultiplierModelBase(data, 1e-12,
                            MultiplierInputOrientedModel()), ['x1', 'q'])
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 0.83333334, 0.71428571, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 0.5, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'E', 0.5, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'D', 'B', 0.21428571, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'D', 'E', 0.28571429, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [0.5, 0, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'B', ['x1', 'x2', 'q'], [0.5, 0, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.055555556, 0.11111111,
                                             0.27777778], model_solution,
                                             data)
    utils_for_tests.check_categories_for_dmu('D', ['x1', 'x2', 'q'], [
                                             0.14285714, 0.28571429,
                                             0.71428571], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)


def test_CRS_multi_input_oriented_with_non_discretionary_vars(data):
    model = MultiplierModelInputOrientedWithNonDiscVars(
        MultiplierModelBase(data, 1e-12,
                            MultiplierInputOrientedModel()), set(['x1']))

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.3, 1, 0.750000012, 0.5, 1], model_solution, data)

    utils_for_tests.check_lambda_variables(
        'A', 'B', 0.25, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'A', 'E', 0.25, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'C', 'B', 0.75, model_solution, data)
    utils_for_tests.check_lambda_variables(
        'C', 'E', 0.75, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'E', 0.5, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'B', ['x1', 'x2', 'q'], [0.125, 0.25, 0.625], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.083333333, 0.16666667,
                                             0.41666667], model_solution,
                                             data)
    utils_for_tests.check_categories_for_dmu(
        'D', ['x1', 'x2', 'q'], [0, 0.5, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0, 0.5, 0.5], model_solution, data)


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
                                MultiplierInputOrientedModel())
    model_solution = model.run()
    clean_up_pickled_files()
