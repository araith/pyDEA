from openpyxl import Workbook
import datetime

from pyDEA.core.models.maximize_slacks import MaximizeSlacksModel
from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.data_processing.read_data_from_xls import read_data, convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import DisposableVarsConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelVRSDecorator
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.parameters import Parameters
from pyDEA.core.utils.dea_utils import clean_up_pickled_files

import tests.utils_for_tests as utils_for_tests


def test_maximize_slacks_usual():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelBase(data,
                                 EnvelopmentModelInputOriented(
                                     generate_upper_bound_for_efficiency_score),
                                 DefaultConstraintCreator())
    model = MaximizeSlacksModel(model)

    start_time = datetime.datetime.now()
    model_solution = model.run()
    end_time = datetime.datetime.now()

    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.62939304, 0.85479694,
                                                   1, 0.42106749,
                                                   1, 1, 0.75766909,
                                                   0.82539683, 0.5, 1],
                                            model_solution, data)

    work_book = Workbook()
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds())
    writer.write_data(model_solution)
    work_book.save('tests/test_max_slacks_output.xls')
    clean_up_pickled_files()


def test_maximize_slacks_usual_weakly_disposable_vars():
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
    model = MaximizeSlacksModel(model)
    start_time = datetime.datetime.now()
    model_solution = model.run()
    end_time = datetime.datetime.now()
    utils_for_tests.check_optimal_solution_status_and_sizes(
        model_solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.86998617, 1, 1, 1, 1,
                                                   1, 1, 1, 0.6386574, 1],
                                            model_solution, data)
    work_book = Workbook()
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds())
    writer.write_data(model_solution)
    work_book.save('tests/test_max_slacks_weakly_disp_vars_output.xls')
    clean_up_pickled_files()
