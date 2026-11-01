import pytest

from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierOutputOrientedModel
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelVRSDecorator
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelWithDisposableCategories
from pyDEA.core.data_processing.read_data import read_data
from pyDEA.core.data_processing.read_data import construct_input_data_instance
from pyDEA.core.data_processing.read_data import validate_data

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = MultiplierModelVRSDecorator(
        MultiplierModelBase(data, 0,
                            MultiplierOutputOrientedModel()))
    return model


def test_VRS_multi_output_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)

    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 1, 1, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'C', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'D', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    # VRS weights/intercepts need not be unique. Check every returned weight
    # and intercept through feasibility, normalization and strong duality.
    utils_for_tests.check_output_multiplier_solution(
        model_solution, data, vrs=True)


def test_VRS_multi_output_oriented_with_weakly_disposable_vars_small(data):
    model = MultiplierModelVRSDecorator(MultiplierModelWithDisposableCategories(
        MultiplierModelBase(data, 1e-12,
                            MultiplierOutputOrientedModel()), set(['q'])))
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 1, 1, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'C', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'D', 1, model_solution, data)

    # The same invariants apply with an unrestricted output multiplier.
    utils_for_tests.check_output_multiplier_solution(
        model_solution, data, weakly_disposable={'q'}, vrs=True,
        lower_bound=1e-12)
