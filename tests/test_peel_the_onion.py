import xlwt
import datetime

from pyDEA.core.models.peel_the_onion import peel_the_onion_method
from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.parameters import Parameters, parse_parameters_from_file
from pyDEA.core.models.multiplier_model_decorators import MultiplierModelVRSDecorator
from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierInputOrientedModel
from pyDEA.core.data_processing.read_data_from_xls import read_data, construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data, convert_to_dictionary
import pyDEA.core.utils.model_factory as model_factory
from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.categorical_dmus import ModelWithCategoricalDMUs
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

import tests.utils_for_tests as utils_for_tests
from tests.utils_for_tests import DEA_example2_data
from tests.utils_for_tests import categorical_data
from tests.utils_for_tests import categorical_from_book
from tests.test_CRS_env_input_oriented_model import _create_large_model
from tests.test_CRS_env_input_oriented_model import _check_large_model
from tests.test_CRS_multi_output_oriented_model import _create_large_model_CRS_multi_output_oriented_with_non_discretionary
from tests.test_CRS_multi_output_oriented_model import _check_large_model_CRS_multi_output_oriented_with_non_discretionary


def test_peel_the_onion_CRS_env_input_oriented(DEA_example2_data):

    model = _create_large_model(DEA_example2_data)

    solution, ranks, state = peel_the_onion_method(model)

    _check_large_model(solution, model.input_data)

    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    expected_ranks = [1, 3, 2, 1, 3, 1, 1, 2, 1, 2, 1]
    utils_for_tests.check_onion_ranks(
        model.input_data, dmus, expected_ranks, ranks)


def test_peel_the_onion_CRS_multi_output_oriented(DEA_example2_data):
    model = _create_large_model_CRS_multi_output_oriented_with_non_discretionary(
        DEA_example2_data)
    start_time = datetime.datetime.now()
    solution, ranks, state = peel_the_onion_method(model)
    end_time = datetime.datetime.now()
    _check_large_model_CRS_multi_output_oriented_with_non_discretionary(
        solution, model.input_data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    expected_ranks = [1, 3, 2, 1, 3, 1, 1, 2, 1, 2, 1]
    utils_for_tests.check_onion_ranks(
        model.input_data, dmus, expected_ranks, ranks)

    work_book = xlwt.Workbook()
    ranks_as_list = []
    ranks_as_list.append(ranks)
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds(),
                       ranks=ranks_as_list)
    writer.write_data(solution)
    work_book.save('tests/test_peel_the_onion.xls')


def test_peel_the_onion_VRS_multi(categorical_data):
    categorical_data.add_input_category('rein')
    categorical_data.add_output_category('aus')
    model = MultiplierModelVRSDecorator(
        MultiplierModelBase(categorical_data, 0,
                            MultiplierInputOrientedModel()))

    solution, ranks, state = peel_the_onion_method(model)
    utils_for_tests.check_optimal_solution_status_and_sizes(
        solution, categorical_data)
    dmus = ['B', 'C', 'D', 'E', 'F', 'G']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.5, 1, 0.99999998,
                                                   0.75, 0.50000001],
                                            solution, categorical_data, 1e-7)

    expected_ranks = [1, 2, 1, 1, 2, 2]
    utils_for_tests.check_onion_ranks(
        model.input_data, dmus, expected_ranks, ranks)


def test_peel_the_onion_unbounded():
    params = parse_parameters_from_file('tests/params_for_linux.txt')

    categories, xls_data, dmu_name, sheet_name = read_data(
        params.get_parameter_value('DATA_FILE'))
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    model_input = construct_input_data_instance(categories, coefficients)

    model_factory.add_input_and_output_categories(params, model_input)

    model = model_factory.create_model(params, model_input)

    ranks = None
    model_solution, ranks, state = peel_the_onion_method(model)
    assert state is False
    clean_up_pickled_files()


def test_peel_the_onion_and_categorical(categorical_from_book):
    model = EnvelopmentModelBase(categorical_from_book,
                                 EnvelopmentModelInputOriented(
                                     generate_upper_bound_for_efficiency_score),
                                 DefaultConstraintCreator())
    model = ModelWithCategoricalDMUs(model, 'Category')
    model_solution, ranks, state = peel_the_onion_method(model)
    assert state is True
    clean_up_pickled_files()
