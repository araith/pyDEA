import pytest

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOriented
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model import EnvelopmentModelOutputOrientedWithNonDiscVars
from pyDEA.core.data_processing.read_data_from_xls import read_data
from pyDEA.core.data_processing.read_data_from_xls import convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.models.bound_generators import generate_lower_bound_for_efficiency_score
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def model(request, data):
    model = EnvelopmentModelBase(
        data,
        EnvelopmentModelOutputOriented(
            generate_lower_bound_for_efficiency_score),
        DefaultConstraintCreator())
    return model


def test_CRS_env_output_oriented_small(model, data):
    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E']
    utils_for_tests.check_efficiency_scores(dmus,
                                            [0.5, 1, 1 / 1.2, 1 / 1.4, 1],
                                            model_solution, data)

    utils_for_tests.check_lambda_variables('A', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('B', 'B', 1, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'B', 1.2, model_solution, data)
    utils_for_tests.check_lambda_variables('C', 'E', 0.6, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'B', 0.3, model_solution, data)
    utils_for_tests.check_lambda_variables('D', 'E', 0.4, model_solution, data)
    utils_for_tests.check_lambda_variables('E', 'E', 1, model_solution, data)

    utils_for_tests.check_categories_for_dmu('A', ['x1', 'x2', 'q'],
                                             [1, 0, 1], model_solution, data)
    utils_for_tests.check_categories_for_dmu('B', ['x1', 'x2', 'q'],
                                             [0.1, 0.2, 0.5], model_solution,
                                             data)
    utils_for_tests.check_categories_for_dmu('C', ['x1', 'x2', 'q'],
                                             [0.066666667, 0.13333333,
                                              0.33333333],
                                             model_solution, data)
    utils_for_tests.check_categories_for_dmu('D', ['x1', 'x2', 'q'],
                                             [0.2, 0.4, 1], model_solution,
                                             data)
    utils_for_tests.check_categories_for_dmu('E', ['x1', 'x2', 'q'],
                                             [0.1, 0.2, 0.5], model_solution,
                                             data)


def test_CRS_env_output_oriented_non_disc_vars():
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
    model = EnvelopmentModelBase(
        data,
        EnvelopmentModelOutputOrientedWithNonDiscVars(
            set(['ND1']),
            generate_lower_bound_for_efficiency_score),
        DefaultConstraintCreator())

    model_solution = model.run()
    utils_for_tests.check_optimal_solution_status_and_sizes(model_solution,
                                                            data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 1, 1 / 1.1698685, 1,
                                                   1 / 2.3749162, 1,
                                                   1, 1 / 1.3198374,
                                                   1 / 1.2115385,
                                                   0.5, 1], model_solution,
                                            data)
    clean_up_pickled_files()
