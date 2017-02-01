import os
import pytest

from pyDEA.core.data_processing.save_data_to_file import save_data_to_xls
from pyDEA.core.data_processing.read_data_from_xls import read_data


@pytest.fixture
def raw_data(request):
    return read_data('tests/DEA_example2_data.xls')


def compare_files(raw_data, data_file, sheet_name, categories):
    categories_file, xls_data, dmu_name_file, sheet_name_file = read_data(
        data_file, sheet_name)
    assert dmu_name_file == raw_data[2]
    assert sheet_name_file == sheet_name
    for category in categories_file:
        assert category in categories
    data = raw_data[1]
    for row in range(len(xls_data)):
        for col, val in enumerate(xls_data[row]):
            assert val == data[row][col]


def get_categories(raw_data):
    categories = [raw_data[2]]
    categories.extend(raw_data[0])
    return categories


def test_save_data_to_new_file(raw_data):
    categories = get_categories(raw_data)
    data_file = 'tests/test_data_save.xls'
    save_data_to_xls(data_file, categories, raw_data[1])
    assert os.path.isfile(data_file)
    compare_files(raw_data, data_file, 'Data', categories)
    os.remove(data_file)


def test_save_data_to_existing_file(raw_data):
    categories = get_categories(raw_data)
    data_file = 'tests/test_file_for_data_save.xls'
    sheet_name = 'SheetWithData'
    save_data_to_xls(data_file, categories, raw_data[1], sheet_name)
    assert os.path.isfile(data_file)
    compare_files(raw_data, data_file, sheet_name, categories)


def test_save_data_to_file_wrong_sheet_name():
    with pytest.raises(ValueError) as excinfo:
        save_data_to_xls('test.xls', [], [], '')
    assert str(excinfo.value) == 'Sheet name is not specified'


def test_save_data_to_existing_file_new_sheet_name(raw_data):
    categories = get_categories(raw_data)
    data_file = 'tests/test_file_for_data_save.xls'
    sheet_name = 'NewSheetName'
    save_data_to_xls(data_file, categories, raw_data[1], sheet_name)
    assert os.path.isfile(data_file)
    compare_files(raw_data, data_file, sheet_name, categories)
