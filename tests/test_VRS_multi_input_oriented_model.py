import pytest

from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierInputOrientedModel
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelVRSDecorator
from pyDEA.core.data_processing.read_data_from_xls import read_data
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = MultiplierModelVRSDecorator(
        MultiplierModelBase(data, 0,
                            MultiplierInputOrientedModel()))
    return model


def test_VRS_multi_input_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)

    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [1, 1, 1, 1, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'A', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'C', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'D', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [0.5, 0, 0], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'B', ['x1', 'x2', 'q'], [0.25, 0.125, 0], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.055555556, 0.11111111,
                                             0.44444444],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'D', ['x1', 'x2', 'q'], [0.25, 0.125, 0], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0, 0.5, 0], model_solution, data)

    utils_for_tests.check_VRS_duals(
        dmus, [1, 1, -0.33333333, 1, 1], model_solution, data)
