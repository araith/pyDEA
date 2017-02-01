import pytest

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOriented
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOrientedWithNonDiscVars
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelVRSDecorator
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import DisposableVarsConstraintCreator
from pyDEA.core.data_processing.read_data_from_xls import read_data
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data, convert_to_dictionary
from pyDEA.core.models.bound_generators import generate_lower_bound_for_efficiency_score
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = EnvelopmentModelVRSDecorator(
        EnvelopmentModelBase(data,
                             EnvelopmentModelOutputOriented(
                             generate_lower_bound_for_efficiency_score),
                             DefaultConstraintCreator()))
    return model


def test_VRS_env_output_oriented_small(model, data):
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

    utils_for_tests.check_categories_for_dmu(
        'A', ['x1', 'x2', 'q'], [0.25, 0, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'C', ['x1', 'x2', 'q'], [0, 0, 0.33333333], model_solution, data)
    utils_for_tests.check_categories_for_dmu(
        'D', ['x1', 'x2', 'q'], [0.33333333, 0.66666667, 1], model_solution,
        data)
    utils_for_tests.check_categories_for_dmu(
        'E', ['x1', 'x2', 'q'], [0, 0.125, 0.5], model_solution, data)

    # B does not return the same value
    utils_for_tests.check_VRS_duals(
        ['A', 'C', 'D', 'E'], [1.5, 1, -1.3333333, 0.75], model_solution, data)


def test_VRS_env_output_oriented_non_disc_vars():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_output_category('ND1')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelVRSDecorator(
        EnvelopmentModelBase(
            data,
            EnvelopmentModelOutputOrientedWithNonDiscVars(
                set(['ND1']),
                generate_lower_bound_for_efficiency_score),
            DefaultConstraintCreator()))

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 1, 1, 1, 1 / 2.211395, 1,
                                                   1, 1, 1, 1 / 1.1168902, 1],
                                            model_solution, data)
    clean_up_pickled_files()


def test_VRS_env_output_oriented_weakly_disposable_vars():
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
        EnvelopmentModelBase(
            data,
            EnvelopmentModelOutputOriented(
                generate_lower_bound_for_efficiency_score),
            DisposableVarsConstraintCreator(set(['I3', 'O1']))))

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 1 / 1.4107143, 1, 1,
                                                   1 / 1.821256,
                                                   1, 1, 1, 1, 1 / 1.1407407,
                                                   1], model_solution, data)
    clean_up_pickled_files()
