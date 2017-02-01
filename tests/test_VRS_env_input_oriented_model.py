import pytest

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOrientedWithNonDiscVars
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelVRSDecorator
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import DisposableVarsConstraintCreator
from pyDEA.core.data_processing.read_data_from_xls import read_data, convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.data_processing.parameters import parse_parameters_from_file
import pyDEA.core.utils.model_factory as model_factory
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = EnvelopmentModelVRSDecorator(
        EnvelopmentModelBase(data,
                             EnvelopmentModelInputOriented(
                             generate_upper_bound_for_efficiency_score),
                             DefaultConstraintCreator()))
    return model


def test_VRS_env_input_oriented_small(model, data):
    model_solution = model.run()

    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)

    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(
        dmus, [1, 1, 1, 1, 1], model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
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
        'E', ['x1', 'x2', 'q'], [0.1, 0.2, 0.3], model_solution, data)

    utils_for_tests.check_VRS_duals(
        dmus, [1, 1, -0.33333333, 1, 0.4], model_solution, data)


def test_VRS_env_input_oriented_non_disc_vars():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('ND1')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelVRSDecorator(
        EnvelopmentModelBase(
            data,
            EnvelopmentModelInputOrientedWithNonDiscVars(
                set(['ND1']),
                generate_upper_bound_for_efficiency_score),
            DefaultConstraintCreator()))

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.86998617, 1, 1,
                                                   0.76086957, 1,
                                                   1, 1, 1, 0.54161069, 1],
                                            model_solution, data)
    clean_up_pickled_files()


def test_VRS_env_input_oriented_weakly_disposable_vars():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('I3')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelVRSDecorator(
        EnvelopmentModelBase(data,
                             EnvelopmentModelInputOriented(
                             generate_upper_bound_for_efficiency_score),
                             DisposableVarsConstraintCreator(
                                set(['I2', 'O1']))))

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.86998617, 1, 1, 1, 1,
                                                   1, 1, 1, 0.6386574, 1],
                                            model_solution,
                                            data)
    clean_up_pickled_files()


def test_VRS_from_params_file():
    params = parse_parameters_from_file('tests/params_new_format.txt')

    categories, xls_data, dmu_name, sheet_name = read_data(
        params.get_parameter_value('DATA_FILE'))
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    model_input = construct_input_data_instance(categories, coefficients)

    model_factory.add_input_and_output_categories(params, model_input)

    model = model_factory.create_model(params, model_input)
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, model_input)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.86998617, 1, 0.95561335,
                                                   0.85,
                                                   1, 1, 0.84507042, 1,
                                                   0.524, 0.89058524],
                                            model_solution, model_input)
    clean_up_pickled_files()
