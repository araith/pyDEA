import xlrd

from pyDEA.core.data_processing.read_data_from_xls import read_data, XLSReader
from pyDEA.core.data_processing.read_data_from_xls import has_non_empty_cells
from pyDEA.core.data_processing.read_data_from_xls import extract_categories
from pyDEA.core.data_processing.read_data_from_xls import extract_coefficients
from pyDEA.core.data_processing.read_data_from_xls import validate_data, convert_to_dictionary
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance


def test_has_non_empty_cells():
    row = []
    reader = XLSReader()
    assert has_non_empty_cells(reader, []) is False
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_BLANK, ''))
    assert has_non_empty_cells(reader, row) is False
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'x1'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'input with space'))
    assert has_non_empty_cells(reader, row) is True
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 10))
    assert has_non_empty_cells(reader, row) is True
    row = []
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 10))
    assert has_non_empty_cells(reader, row) is True


def test_extract_categories():
    row = []
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'x1'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'x2'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'input with space'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'output starts with space'))
    reader = XLSReader()
    categories, indexes = extract_categories(reader, row)
    assert categories == ['x1', 'x2',
                          'input with space', 'output starts with space']


def test_extract_numeric_categories():
    row = []
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 5))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 15))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, -100))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'x1'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    reader = XLSReader()
    categories, indexes = extract_categories(reader, row)
    assert categories == [5, 15, -100, 'x1']


def test_extract_coefficients():
    row = []
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u'dmu1'))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 10))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 25))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 45))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 0))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 7.9))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    reader = XLSReader()
    (dmu, coefficients, dmu_name) = extract_coefficients(
        reader, row, [4, 5, 7, 8, 10])
    assert dmu == 'dmu1'
    assert coefficients == [10, 25, 45, 0, 7.9]


def test_extract_coefficients_with_numeric_dmu():
    row = []
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 0))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 10))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 25))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 45))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 0))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 7.9))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, u' aha '))
    row.append(xlrd.sheet.Cell(xlrd.XL_CELL_EMPTY, ''))
    reader = XLSReader()
    (dmu, coefficients, dmu_name) = extract_coefficients(
        reader, row, [3, 4, 5, 6, 7, 8, 9])
    assert dmu == 0
    assert coefficients == [10, 25, 45, 0, 7.9, '', 'aha']


def check_coefficients(input_data, dmu, categories, coefficients):
    dmu_code = input_data._DMU_user_name_to_code[dmu]
    for (count, category) in enumerate(categories):
        assert input_data.coefficients[
            dmu_code, category] == coefficients[count]


def test_validate_data():
    categories = ['x1', 'x2', 'q']
    coefficients = {'dmu1': [1, 3, 10], 'dmu2': [1.2, 5.5, 14]}
    assert validate_data(categories, coefficients) is True
    coefficients = {'dmu1': [1, 3, 10], 'dmu2': [1.2, 5.5]}
    assert validate_data(categories, coefficients) is False
    coefficients = {'dmu1': [1, 3, 0], 'dmu2': [1.2, 5.5, 14]}
    # we allow zeros, but give a warning to a user
    assert validate_data(categories, coefficients) is True
    coefficients = {'dmu1': [1, 3, 10], 'dmu2': [1.2, 'a', 14]}
    assert validate_data(categories, coefficients) is False
    assert validate_data([], dict()) is False


def helper_func(filename):
    categories, data, dmu_name, sheet_name = read_data(filename)
    coefficients, has_same_dmus = convert_to_dictionary(data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    input_data = construct_input_data_instance(categories, coefficients)
    assert len(input_data.DMU_codes) == 4
    assert len(input_data.categories) == 4
    categories = ['x1', 'x2', 'input with space', 'output starts with space']
    for category in categories:
        assert category in input_data.categories
    assert len(input_data.input_categories) == 0
    assert len(input_data.output_categories) == 0
    dmus = ['dmu1', 'dmu2', 'dmu with space', 'space in the beginning']
    for dmu in dmus:
        assert dmu in input_data._DMU_user_name_to_code

    check_coefficients(input_data, 'dmu1', categories, [1, 4, 7, 1])
    check_coefficients(input_data, 'dmu2', categories, [9, 5, 7, 7])
    check_coefficients(input_data, 'dmu with space',
                       categories, [5.5, 1, 8, 8])
    check_coefficients(input_data, 'space in the beginning',
                       categories, [45, 9, 10, 7.55])


def test_read_data_from_xls():
    helper_func('tests/dataForTestingReadXLS.xls')
    helper_func('tests/dataForTestingReadXLStheSame.xlsx')


def test_read_data_from_xls_larger_example():

    categories, data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    input_data = construct_input_data_instance(categories, coefficients)
    assert len(input_data.DMU_codes) == 11
    assert len(input_data.categories) == 5
    categories = ['I1', 'I2', 'I3', 'O1', 'O2']
    for category in categories:
        assert category in input_data.categories
    assert len(input_data.input_categories) == 0
    assert len(input_data.output_categories) == 0
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for dmu in dmus:
        assert dmu in input_data._DMU_user_name_to_code

    check_coefficients(input_data, 'A', categories, [5, 13, 1, 12, 34])
    check_coefficients(input_data, 'B', categories, [16, 12, 2, 14, 13])
    check_coefficients(input_data, 'C', categories, [16, 26,  2,  25,  56])
    check_coefficients(input_data, 'D', categories, [17, 15,  3,   26,  23])
    check_coefficients(input_data, 'E', categories, [18, 14, 1,   8,   18])
    check_coefficients(input_data, 'F', categories, [23, 6,   2,   9,   39])
    check_coefficients(input_data, 'G', categories, [25, 10,  2,   27,  21])
    check_coefficients(input_data, 'H', categories, [27, 22,  3,   30,  10])
    check_coefficients(input_data, 'I', categories, [37, 14,  1,   31,  25])
    check_coefficients(input_data, 'J', categories,
                       [42, 25,  2,   26.5,    17])
    check_coefficients(input_data, 'K', categories, [5,  17,  3,   12,  37])


def test_read_data_from_xls_numeric_dmus():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/dataForTestingReadXLS_withNumericDMU.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    input_data = construct_input_data_instance(categories, coefficients)
    assert len(input_data.DMU_codes) == 3
    assert len(input_data.categories) == 3
    categories = [0, 5, 2]
    for category in categories:
        assert category in input_data.categories
    assert len(input_data.input_categories) == 0
    assert len(input_data.output_categories) == 0
    dmus = [0, 1, 2]
    for dmu in dmus:
        assert dmu in input_data._DMU_user_name_to_code

    check_coefficients(input_data, 0, categories, [10, 1, 2])
    check_coefficients(input_data, 1, categories, [4, 5, 20])
    check_coefficients(input_data, 2, categories, [1, 1, 1])


def test_order_of_dmus():
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/categorical_test_from_book.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    data = construct_input_data_instance(categories, coefficients)
    dmus = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9',
            'L10', 'L11', 'L12',
            'L13', 'L14', 'L15', 'L16', 'L17', 'L18', 'L19', 'L20',
            'L21', 'L22', 'L23']
    for count, dmu in enumerate(dmus):
        assert data.DMU_codes_in_added_order[
            count] == data._DMU_user_name_to_code[dmu]


def _validate_csv(categories, coefficients):
    input_data = construct_input_data_instance(categories, coefficients)
    assert len(input_data.DMU_codes) == 11
    assert len(input_data.categories) == 5
    categories = ['I1', 'I2', 'I3', 'O1', 'O2']
    for category in categories:
        assert category in input_data.categories
    assert len(input_data.input_categories) == 0
    assert len(input_data.output_categories) == 0
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for dmu in dmus:
        assert dmu in input_data._DMU_user_name_to_code

    check_coefficients(input_data, 'A', categories, [5, 13, 1, 12, 34])
    check_coefficients(input_data, 'B', categories, [16, 12, 2, 14, 13])
    check_coefficients(input_data, 'C', categories, [16, 26,  2,  25,  56])
    check_coefficients(input_data, 'D', categories, [17, 15,  3,   26,  23])
    check_coefficients(input_data, 'E', categories, [18, 14, 1,   8,   18])
    check_coefficients(input_data, 'F', categories, [23, 6,   2,   9,   39])
    check_coefficients(input_data, 'G', categories, [25, 10,  2,   27,  21])
    check_coefficients(input_data, 'H', categories, [27, 22,  3,   30,  10])
    check_coefficients(input_data, 'I', categories, [37, 14,  1,   31,  25])
    check_coefficients(input_data, 'J', categories,
                       [42, 25,  2,   26.5,    17])
    check_coefficients(input_data, 'K', categories, [5,  17,  3,   12,  37])


def test_csv_reader():
    categories, data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data.csv')
    coefficients, has_same_dmus = convert_to_dictionary(data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    _validate_csv(categories, coefficients)


def test_csv_reader_with_header():
    categories, data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data_with_header.csv')
    coefficients, has_same_dmus = convert_to_dictionary(data)
    assert dmu_name == 'TestName'
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    _validate_csv(categories, coefficients)
