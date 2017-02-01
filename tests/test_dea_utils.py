import pytest
import os

import pyDEA.core.utils.dea_utils as dea_utils
from pyDEA.core.data_processing.parameters import Parameters
from pyDEA.core.utils.dea_utils import VALID_COEFF, WARNING_COEFF
from pyDEA.core.utils.dea_utils import NOT_VALID_COEFF, TMP_FOLDER

from tests.utils_for_tests import DEA_example_data


def test_format_data():
    assert dea_utils.format_data('test') == 'test'
    assert dea_utils.format_data('0.05') == '0.050000'
    assert dea_utils.format_data(0.123456789) == '0.123457'
    assert dea_utils.format_data(0.1234500000) == '0.123450'


def test_check_categories():
    dea_utils.check_categories(set(['I1', 'I2']), set(['I1', 'I2', 'I3']))
    with pytest.raises(ValueError) as excinfo:
        dea_utils.check_categories(set(['I1', 'O2']), set(['I1', 'I2', 'I3']))
    assert str(excinfo.value) == ('Category <O2> is not present in '
                                  'categories: {0}'.
                                  format(set(['I1', 'I2', 'I3'])))


def test_check_input_and_output_categories(DEA_example_data):
    DEA_example_data.input_categories = set(['I1'])
    DEA_example_data.output_categories = set(['I1'])
    dea_utils.check_input_and_output_categories(DEA_example_data)
    DEA_example_data.input_categories = set()
    with pytest.raises(ValueError) as excinfo:
        dea_utils.check_input_and_output_categories(DEA_example_data)
    assert str(
        excinfo.value) == 'Both input and output categories must be specified'


def test_parse_price_ratio():
    elem = 'I1/I2'
    value = '5'
    constraint = 'I1/I2 >= 5'
    categories = set(['I1', 'I2', 'O1', 'O2'])
    bounds_lb = dict()
    dea_utils.parse_price_ratio(elem, value, constraint, categories, bounds_lb)
    assert bounds_lb['I1', 'I2'] == 5
    elem = 'a/b/c'
    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_price_ratio(
            elem, value, constraint, categories, bounds_lb)
    assert str(excinfo.value) == 'Cannot parse constraint: I1/I2 >= 5'
    elem = 'I1'
    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_price_ratio(
            elem, value, constraint, categories, bounds_lb)
    assert str(excinfo.value) == 'Cannot parse constraint: I1/I2 >= 5'
    elem = '/'
    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_price_ratio(
            elem, value, constraint, categories, bounds_lb)
    assert str(
        excinfo.value) == 'Incorrect constraint, category does not exist: I1/I2 >= 5'


def test_parse_constraint():
    constraint = 'I1 >= 5'
    split_str = '>='
    new_bounds_lb = dict()
    new_bounds_ub = dict()
    categories = set(['I1', 'I2', 'O1', 'O2'])
    dea_utils.parse_constraint(constraint, split_str, new_bounds_lb,
                               new_bounds_ub,
                               categories)
    assert new_bounds_lb['I1'] == 5
    assert len(new_bounds_ub) == 0
    constraint = 'I2 <= 10'
    dea_utils.parse_constraint(constraint, '<=', new_bounds_lb, new_bounds_ub,
                               categories)
    assert new_bounds_ub['I2'] == 10
    assert len(new_bounds_lb) == 1
    assert dea_utils.parse_constraint(constraint, '>=', new_bounds_lb,
                                      new_bounds_ub,
                                      categories) is False

    constraint = 'I2 / I1 <= 10'
    dea_utils.parse_constraint(constraint, '<=', new_bounds_lb, new_bounds_ub,
                               categories)
    assert new_bounds_ub['I2', 'I1'] == 10
    assert len(new_bounds_lb) == 1

    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_constraint('I1 = 3', '=', new_bounds_lb, new_bounds_ub,
                                   categories)
    assert str(
        excinfo.value) == 'Unexpected constraint type, supported types >= and <='
    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_constraint('0 <= I1 <= 5', '<=', new_bounds_lb,
                                   new_bounds_ub,
                                   categories)
    assert str(excinfo.value) == 'Cannot parse constraint: 0 <= I1 <= 5'
    with pytest.raises(ValueError) as excinfo:
        dea_utils.parse_constraint('0 <= I3', '<=', new_bounds_lb,
                                   new_bounds_ub,
                                   categories)
    assert str(
        excinfo.value) == 'Incorrect constraint, category does not exist: 0 <= I3'


def test_create_bounds():
    bounds = ['I1 <= 10', 'I1 >= 2', 'O1 >= 3', 'O2 <= 7']
    categories = set(['I1', 'I2', 'O1', 'O2'])
    parsed_bounds = dea_utils.create_bounds(bounds, categories)
    assert parsed_bounds['I1'] == (2, 10)
    assert parsed_bounds['O1'] == (3, None)
    assert parsed_bounds['O2'] == (None, 7)

    ratio_bounds = ['I1/I2 <= 10', 'I1/I2 >= 1',
                    'O2/O1 >= 0.2', 'O1/O2 <= 0.5']
    parsed_bounds = dea_utils.create_bounds(ratio_bounds, categories)
    assert parsed_bounds['I1', 'I2'] == (1, 10)
    assert parsed_bounds['O2', 'O1'] == (0.2, None)
    assert parsed_bounds['O1', 'O2'] == (None, 0.5)

    invalid_bounds = ['I1/I2 <= 10', 'I1/I2 >= 1', 'I2 >= O1']
    with pytest.raises(ValueError) as excinfo:
        parsed_bounds = dea_utils.create_bounds(invalid_bounds, categories)
    assert str(excinfo.value) == "could not convert string to float: 'I2'"


def test_get_price_ratio_categories():
    category1, category2 = dea_utils.get_price_ratio_categories('I1/ I2')
    assert category1 == 'I1' and category2 == 'I2'
    category1, category2 = dea_utils.get_price_ratio_categories(
        '   I1   /  I2  ')
    assert category1 == 'I1' and category2 == 'I2'
    category1, category2 = dea_utils.get_price_ratio_categories(
        '  name with spaces / I2')
    assert category1 == 'name with spaces' and category2 == 'I2'


def test_find_category_name_in_restrictions():
    category, index = dea_utils.find_category_name_in_restrictions('I1 <= 7')
    assert category == 'I1' and index == 0
    category, index = dea_utils.find_category_name_in_restrictions(
        '  I1  <=  7.8 ')
    assert category == 'I1' and index == 0
    category, index = dea_utils.find_category_name_in_restrictions(
        '  category name with spaces  <=  7.8 ')
    assert category == 'category name with spaces' and index == 0
    category, index = dea_utils.find_category_name_in_restrictions('7.8 >= I2')
    assert category == 'I2' and index == 7
    category, index = dea_utils.find_category_name_in_restrictions(
        '7.8 >=       I2')
    assert category == 'I2' and index == 13
    category, index = dea_utils.find_category_name_in_restrictions(
        'I1/O2 >= 0.5')
    assert category == 'I1/O2' and index == 0


def test_create_params_str():
    params = Parameters()
    params.update_parameter('ORIENTATION', 'input')
    params.update_parameter('RETURN_TO_SCALE', 'VRS')
    assert dea_utils.create_params_str(params) == 'input orientation, VRS'
    params.update_parameter('RETURN_TO_SCALE', 'CRS')
    assert dea_utils.create_params_str(params) == 'input orientation, CRS'


def test_is_valid_coeff():
    assert dea_utils.is_valid_coeff(0.5) == VALID_COEFF
    assert dea_utils.is_valid_coeff(-0.5) == NOT_VALID_COEFF
    assert dea_utils.is_valid_coeff(1.5) == VALID_COEFF
    assert dea_utils.is_valid_coeff('dhfkjfdhbkfd') == NOT_VALID_COEFF
    assert dea_utils.is_valid_coeff('5.35') == VALID_COEFF
    assert dea_utils.is_valid_coeff('0') == WARNING_COEFF


def test_change_to_unique_name_if_needed():
    non_exisiting_file = 'haha_new_file.csv'
    assert dea_utils.change_to_unique_name_if_needed(
        non_exisiting_file) == non_exisiting_file
    file_name = 'tmp.txt'
    with open(file_name, 'w'):
        pass
    assert dea_utils.change_to_unique_name_if_needed(file_name) == 'tmp_1.txt'
    file_name2 = 'tmp_1.txt'
    with open(file_name2, 'w'):
        pass
    assert dea_utils.change_to_unique_name_if_needed(file_name) == 'tmp_2.txt'
    os.remove(file_name)
    os.remove(file_name2)


def test_clean_up_pickled_files():
    file_name = 'tmp.mps'
    with open(file_name, 'w'):
        pass
    if not os.path.exists(dea_utils.TMP_FOLDER):
        os.makedirs(TMP_FOLDER)
    for i in range(5):
        file_name2 = 'tmp_{0}.p'.format(i)
        with open(os.path.join(dea_utils.TMP_FOLDER, file_name2), 'w'):
            pass
    dea_utils.clean_up_pickled_files()
    assert os.path.exists(file_name) is False
    for i in range(5):
        file_name2 = 'tmp_{0}.p'.format(i)
        assert os.path.exists(os.path.join(
            dea_utils.TMP_FOLDER, file_name2)) is False


def test_auto_name_if_needed():
    params = Parameters()
    file_name = 'out.txt'
    params.update_parameter('OUTPUT_FILE', file_name)
    assert dea_utils.auto_name_if_needed(params, 'txt') == file_name
    params.update_parameter('OUTPUT_FILE', '')
    data_file_name = 'dataFileForAutoName.xls'
    params.update_parameter('DATA_FILE', data_file_name)
    assert dea_utils.auto_name_if_needed(
        params, 'csv') == 'dataFileForAutoName_result.csv'
    params.update_parameter('OUTPUT_FILE', 'auto')
    assert dea_utils.auto_name_if_needed(
        params, 'xls') == 'dataFileForAutoName_result.xls'
    with pytest.raises(ValueError) as excinfo:
        dea_utils.auto_name_if_needed(params, 'haha')
    assert str(excinfo.value) == 'haha is not supported output format'


def test_calculate_nb_pages():
    assert dea_utils.calculate_nb_pages(100, 10) == 12
    assert dea_utils.calculate_nb_pages(25, 20) == 2
    assert dea_utils.calculate_nb_pages(100, 0) == 0
    assert dea_utils.calculate_nb_pages(10, 100) == 1
    assert dea_utils.calculate_nb_pages(0, 100) == 1


def test_calculate_start_row_index():
    assert dea_utils.calculate_start_row_index(1, 10) == 0
    assert dea_utils.calculate_start_row_index(2, 10) == 9
    assert dea_utils.calculate_start_row_index(2, 23) == 22
    assert dea_utils.calculate_start_row_index(3, 23) == 44
    assert dea_utils.calculate_start_row_index(0, 10) == 0


def test_validate_category_name():
    assert dea_utils.validate_category_name(
        'I1new', 0, ['I1new', 'I2', 'O2', 'O3']) == 'I1new'
    assert dea_utils.validate_category_name(
        '2.5', 0, ['2.5', 'I2', 'O2', 'O3']) == ''
    assert dea_utils.validate_category_name(
        'I1new', 0, ['I1new', 'I2', 'I1new', 'O3']) == ''
    assert dea_utils.validate_category_name(
        'I1new;', 0, ['I1new;', 'I2', 'P', 'O3']) == ''
