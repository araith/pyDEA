from openpyxl import Workbook
import datetime

from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.parameters import Parameters

from tests.test_CRS_env_input_oriented_model import data
from tests.test_CRS_env_input_oriented_model import model


def test_write_data_xls(model):
    start_time = datetime.datetime.now()
    model_solution = model.run()
    end_time = datetime.datetime.now()
    work_book = Workbook()
    params = Parameters()
    writer = XLSWriter(params, work_book, datetime.datetime.today(),
                       (end_time - start_time).total_seconds())
    writer.write_data(model_solution)
    work_book.save('tests/test_output.xls')
