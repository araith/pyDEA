from openpyxl import Workbook
import datetime

from pyDEA.core.models.super_efficiency_model import SupperEfficiencyModel
from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.peel_the_onion import peel_the_onion_method
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.envelopment_model_decorators import DefaultConstraintCreator
from pyDEA.core.models.envelopment_model_decorators import EnvelopmentModelVRSDecorator
from pyDEA.core.models.bound_generators import generate_supper_efficiency_upper_bound
from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.parameters import Parameters

import tests.utils_for_tests as utils_for_tests
from tests.utils_for_tests import DEA_example2_data
from tests.utils_for_tests import categorical_data


def test_super_efficiency_medium(DEA_example2_data):
    data = DEA_example2_data
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('I3')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelBase(
        data,
        EnvelopmentModelInputOriented(generate_supper_efficiency_upper_bound),
        DefaultConstraintCreator())
    super_efficiency_model = SupperEfficiencyModel(model)
    start_time = datetime.datetime.now()
    solution = super_efficiency_model.run()
    end_time = datetime.datetime.now()
    utils_for_tests.check_optimal_solution_status_and_sizes(solution, data)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(
        dmus,
        [1.652173892, 0.6485875732, 0.909247759,
         1.116838534, 0.5490716156, 2.485294106,
         1.244945494, 0.824120607, 2.299898658,
         0.6267333816, 1.088235274],
        solution, data, 1e-6)
    work_book = Workbook()
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds())
    writer.write_data(solution)
    work_book.save('tests/test_super_efficiency_output.xls')


def test_super_efficiency_with_VRS(DEA_example2_data):
    data = DEA_example2_data
    data.add_input_category('I1')
    data.add_input_category('I2')
    data.add_input_category('I3')
    data.add_output_category('O1')
    data.add_output_category('O2')
    model = EnvelopmentModelBase(
        data,
        EnvelopmentModelInputOriented(generate_supper_efficiency_upper_bound),
        DefaultConstraintCreator())
    model = EnvelopmentModelVRSDecorator(model)
    super_efficiency_model = SupperEfficiencyModel(model)
    start_time = datetime.datetime.now()
    solution = super_efficiency_model.run()
    end_time = datetime.datetime.now()
    work_book = Workbook()
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds())
    writer.write_data(solution)
    work_book.save('tests/test_super_efficiency_with_VRS.xls')


def test_superefficiency_and_peel_the_onion(categorical_data):
    categorical_data.add_input_category('rein')
    categorical_data.add_output_category('aus')
    model = EnvelopmentModelBase(
        categorical_data,
        EnvelopmentModelInputOriented(generate_supper_efficiency_upper_bound),
        DefaultConstraintCreator())
    super_efficiency_model = SupperEfficiencyModel(model)
    model_solution, ranks, state = peel_the_onion_method(
        super_efficiency_model)
