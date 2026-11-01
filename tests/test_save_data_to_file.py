import os
import shutil
import pytest
from openpyxl import load_workbook

from pyDEA.core.data_processing.save_data_to_file import save_data_to_xlsx
from pyDEA.core.data_processing.read_data import read_data


@pytest.fixture
def raw_data(request):
    return read_data('tests/DEA_example2_data.xlsx')


def compare_files(raw_data, data_file, sheet_name, categories):
    categories_file, xls_data, dmu_name_file, sheet_name_file = read_data(
        data_file, sheet_name)
    assert dmu_name_file == raw_data[2]
    assert sheet_name_file == sheet_name
    assert categories_file == raw_data[0]
    assert xls_data == raw_data[1]


def sheet_values(filename):
    workbook = load_workbook(filename)
    try:
        return {sheet.title: list(sheet.values) for sheet in workbook}
    finally:
        workbook.close()


def get_categories(raw_data):
    categories = [raw_data[2]]
    categories.extend(raw_data[0])
    return categories


def test_save_data_to_new_file(raw_data):
    categories = get_categories(raw_data)
    data_file = 'tests/test_data_save.xlsx'
    save_data_to_xlsx(data_file, categories, raw_data[1])
    assert os.path.isfile(data_file)
    compare_files(raw_data, data_file, 'Data', categories)
    os.remove(data_file)


def test_save_data_to_existing_file(raw_data, tmp_path):
    categories = get_categories(raw_data)
    data_file = tmp_path / 'test_file_for_data_save.xlsx'
    shutil.copy('tests/test_file_for_data_save.xlsx', data_file)
    before = sheet_values(data_file)
    sheet_name = 'SheetWithData'
    save_data_to_xlsx(str(data_file), categories, raw_data[1], sheet_name)
    assert os.path.isfile(data_file)
    compare_files(raw_data, str(data_file), sheet_name, categories)
    after = sheet_values(data_file)
    assert set(after) == set(before)
    for name in before:
        if name != sheet_name:
            assert after[name] == before[name]


def test_save_data_to_file_wrong_sheet_name():
    with pytest.raises(ValueError) as excinfo:
        save_data_to_xlsx('test.xlsx', [], [], '')
    assert str(excinfo.value) == 'Sheet name is not specified'


def test_save_data_to_existing_file_new_sheet_name(raw_data, tmp_path):
    categories = get_categories(raw_data)
    data_file = tmp_path / 'test_file_for_data_save.xlsx'
    shutil.copy('tests/test_file_for_data_save.xlsx', data_file)
    before = sheet_values(data_file)
    sheet_name = 'NewSheetName'
    # Force the branch that adds a genuinely new sheet, independently of
    # whether an earlier legacy run already put this sheet in the fixture.
    workbook = load_workbook(data_file)
    if sheet_name in workbook.sheetnames:
        del workbook[sheet_name]
    workbook.save(data_file)
    workbook.close()
    before.pop(sheet_name, None)
    save_data_to_xlsx(str(data_file), categories, raw_data[1], sheet_name)
    assert os.path.isfile(data_file)
    compare_files(raw_data, str(data_file), sheet_name, categories)
    after = sheet_values(data_file)
    assert set(after) == set(before) | {sheet_name}
    for name in before:
        assert after[name] == before[name]


def test_save_preserves_numeric_categories(tmp_path):
    data_file = str(tmp_path / 'numeric_categories.xlsx')
    save_data_to_xlsx(data_file, ['DMUs', 5, ' x2 '], [['A', 1, 2]])
    categories, values, dmu_name, sheet_name = read_data(data_file)
    assert categories == [5, 'x2']
    assert values == [['A', 1, 2]]
    assert dmu_name == 'DMUs'
    assert sheet_name == 'Data'
