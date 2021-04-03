import pytest
from openpyxl import Workbook
import datetime

from pyDEA.core.models.categorical_dmus import ModelWithCategoricalDMUs
from pyDEA.core.models.categorical_dmus import get_dmus_with_fixed_hierarchical_category
from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model import MultiplierInputOrientedModel
from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.parameters import Parameters

from tests.test_CRS_env_input_oriented_model import data
import tests.utils_for_tests as utils_for_tests
from tests.utils_for_tests import categorical_from_book


def test_get_dmus_with_fixed_hierarchical_category(data):
    dmus = get_dmus_with_fixed_hierarchical_category(
        data.coefficients, 1, 'x1', data.DMU_codes)
    assert len(dmus) == 0
    dmus = get_dmus_with_fixed_hierarchical_category(
        data.coefficients, 2, 'x1', data.DMU_codes)
    assert data._DMU_user_name_to_code['A'] in dmus
    assert data._DMU_user_name_to_code['B'] in dmus


def test_run_with_categorical_dmus(categorical_from_book):
    data = categorical_from_book
    model = MultiplierModelBase(data, 0,
                                MultiplierInputOrientedModel())
    categorical_model = ModelWithCategoricalDMUs(model, 'Category')
    start_time = datetime.datetime.now()
    solution = categorical_model.run()
    end_time = datetime.datetime.now()
    dmus = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'L10',
            'L11', 'L12',
            'L13', 'L14', 'L15', 'L16', 'L17', 'L18', 'L19', 'L20',
            'L21', 'L22', 'L23']
    utils_for_tests.check_efficiency_scores(dmus, [0.377, 0.879, 0.936, 1, 1, 1,
                                                   0.743, 0.648, 1, 0.815,
                                                   0.646,
                                                   0.835, 0.794, 0.835, 1,
                                                   0.687, 1, 0.787, 1,
                                                   0.849, 0.787, 0.681, 1],
                                            solution, data, 1e-3)
    work_book = Workbook()
    writer = XLSWriter(Parameters(), work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds(),
                       categorical='Category')
    writer.write_data(solution)
    work_book.save('tests/test_categorical_output.xls')


def test_run_with_categorical_dmus_invalid_data(categorical_from_book):
    data = categorical_from_book
    model = MultiplierModelBase(data, 0,
                                MultiplierInputOrientedModel())
    with pytest.raises(ValueError) as excinfo:
        categorical_model = ModelWithCategoricalDMUs(model, 'Non-existant')
    assert str(excinfo.value) == 'Category <Non-existant> does not exist'
