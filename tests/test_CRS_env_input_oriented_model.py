import pytest

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOrientedWithNonDiscVars
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.data_processing.input_data import InputData
from pyDEA.core.data_processing.read_data_from_xls import read_data
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

import tests.utils_for_tests as utils_for_tests
from tests.utils_for_tests import DEA_example2_data
from tests.utils_for_tests import DEA_example_data


@pytest.fixture
def data(request):
    data = InputData()
    data.add_coefficient('A', 'x1', 2)
    data.add_coefficient('A', 'x2', 5)
    data.add_coefficient('A', 'q', 1)
    data.add_coefficient('B', 'x1', 2)
    data.add_coefficient('B', 'x2', 4)
    data.add_coefficient('B', 'q', 2)
    data.add_coefficient('C', 'x1', 6)
    data.add_coefficient('C', 'x2', 6)
    data.add_coefficient('C', 'q', 3)
    data.add_coefficient('D', 'x1', 3)
    data.add_coefficient('D', 'x2', 2)
    data.add_coefficient('D', 'q', 1)
    data.add_coefficient('E', 'x1', 6)
    data.add_coefficient('E', 'x2', 2)
    data.add_coefficient('E', 'q', 2)
    data.add_input_category('x1')
    data.add_input_category('x2')
    data.add_output_category('q')
    request.addfinalizer(clean_up_pickled_files)
    return data

@pytest.fixture
def model(request, data):
    model = EnvelopmentModelBase(data,
                                 EnvelopmentModelInputOriented(
                                     generate_upper_bound_for_efficiency_score),
                                 DefaultConstraintCreator())
    return model


def test_CRS_env_input_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [0.5, 1, 0.83333333, 0.71428571, 1], model_solution, data)

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
        'B', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'], [
                                             0.055555556, 0.11111111,
                                             0.27777778],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu('D', ['x1', 'x2', 'q'], [
                                             0.14285714, 0.28571429,
                                             0.71428571],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0.1, 0.2, 0.5], model_solution, data)


def _create_large_model(data):
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('I3')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelBase(data,
                                 EnvelopmentModelInputOriented(
                                     generate_upper_bound_for_efficiency_score),
                                 DefaultConstraintCreator())
    return model


def _check_large_model(model_solution, data):
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)

    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.64858757,
                                                   0.90924776, 1,
                                                   0.54907162, 1, 1,
                                                   0.8241206, 1,
                                                   0.62673338, 1],
                                            model_solution, data)


def test_CRS_env_input_oriented_large(DEA_example2_data):

    model = _create_large_model(DEA_example2_data)

    model_solution = model.run()

    _check_large_model(model_solution, model.input_data)


def test_CRS_env_input_oriented_non_disc_vars(DEA_example_data):
    data = DEA_example_data
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('ND1')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelBase(
        data,
        EnvelopmentModelInputOrientedWithNonDiscVars(
            set(['ND1']),
            generate_upper_bound_for_efficiency_score),
        DefaultConstraintCreator())

    model_solution = model.run()

    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.62939304, 0.95095971,
                                                   1, 0.42525889,
                                                   1, 1, 0.82672274, 1,
                                                   0.53385106, 1],
                                            model_solution, data)
