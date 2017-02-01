import pytest
import os

import pyDEA.core.data_processing.parameters as parameters


def test_extract_comment():
    assert parameters.extract_comment('some line') == 'some line'
    assert (parameters.extract_comment(
            'line with comment # here comes comment') ==
            'line with comment ')
    assert parameters.extract_comment('# only comment is present') == ''


def test_validate_string():
    assert parameters.validate_string('', parameters.VALID_PARAM_NAME) is False
    assert parameters.validate_string(
        'abc', parameters.VALID_PARAM_NAME) is True
    assert (parameters.validate_string('abc something',
            parameters.VALID_PARAM_NAME)
            is True)
    assert parameters.validate_string(
        ' space', parameters.VALID_PARAM_NAME) is False
    assert parameters.validate_string(
        '     ', parameters.VALID_PARAM_NAME) is False
    assert (parameters.validate_string(r'\home\path\file.txt  ',
                                       parameters.VALID_PARAM_VALUE) is True)
    assert (parameters.validate_string(r' \home\path\file.txt  ',
                                       parameters.VALID_PARAM_VALUE) is False)
    assert (parameters.validate_string(r'some random chars:\\/.&8?!',
                                       parameters.VALID_PARAM_VALUE) is True)
    assert (parameters.validate_string(r'',
                                       parameters.VALID_PARAM_VALUE) is True)
    assert (parameters.validate_string(r'new value',
                                       parameters.VALID_PARAM_VALUE) is True)
    assert (parameters.validate_string(r'some > name',
                                       parameters.VALID_PARAM_NAME) is False)
    assert (parameters.validate_string(r'some = name',
                                       parameters.VALID_PARAM_NAME) is False)
    assert (parameters.validate_string(r'some < name',
                                       parameters.VALID_PARAM_NAME) is False)
    assert (parameters.validate_string(r'some / name',
                                       parameters.VALID_PARAM_NAME) is False)


def test_parameters_update_parameter():
    p = parameters.Parameters()
    p.update_parameter('DEA_FORM', 'value1')
    assert p.get_parameter_value('DEA_FORM') == 'value1'
    p.update_parameter('INPUT_CATEGORIES', 'new value')
    assert p.get_parameter_value('INPUT_CATEGORIES') == 'new value'
    p.update_parameter('INPUT_CATEGORIES', '')
    assert p.get_parameter_value('INPUT_CATEGORIES') == ''
    with pytest.raises(KeyError) as excinfo:
        p.update_parameter('param2', 'value2')
    assert str(excinfo.value) == ("'Parameter param2 does not exists in"
                                  " the dictionary'")
    with pytest.raises(ValueError) as excinfo:
        p.update_parameter('INPUT_CATEGORIES', '   ')
    assert str(excinfo.value) == ('Trying to update parameter '
                                  '<INPUT_CATEGORIES> with not valid '
                                  'value <   >')


def test_parameters_get_parameter_value():
    allParams = parameters.Parameters()
    allParams.update_parameter('INPUT_CATEGORIES', 'value1')
    assert allParams.get_parameter_value('INPUT_CATEGORIES') == 'value1'
    with pytest.raises(KeyError) as excinfo:
        allParams.get_parameter_value('Param2')
    assert str(excinfo.value) == "'Param2'"


def test_file_write_and_read_valid_parameters():
    p = parameters.Parameters()
    p.update_parameter('DEA_FORM', 'value1')
    p.update_parameter('INPUT_CATEGORIES', 'some long value')
    p.update_parameter('OUTPUT_CATEGORIES', 'some/linux/type/path/file.txt')
    p.update_parameter('DATA_FILE', '\some\Windows\like\path\p.txt')
    filename = 'test_valid_params.params'
    parameters.write_parameters_to_file(p, filename)
    paramsFromFile = parameters.parse_parameters_from_file(filename)
    for key, value in p.params.items():
        assert key in paramsFromFile.params
        assert paramsFromFile.params[key] == value
    os.remove(filename)


def check_one_invalid_parameter(param_and_value):
    filename = 'test_invalid_params.params'
    file_with_params = open(filename, 'w')
    file_with_params.write(param_and_value + '\n')
    file_with_params.close()
    with pytest.raises(ValueError) as excinfo:
        parameters.parse_parameters_from_file(filename)
    assert str(excinfo.value) == ('File {filename} does not contain any valid'
                                  ' parameter values'.format(filename=filename))
    os.remove(filename)


def test_file_read_not_valid_parameters():
    check_one_invalid_parameter('< not valid name> {aha}')
    check_one_invalid_parameter('<param1> {    }')
    check_one_invalid_parameter('<param1> {   not valid value }')
    check_one_invalid_parameter('<param1> {\t % _\//}')


def test_file_read_comments():
    filename = 'test_params_with_comments.params'
    file_with_params = open(filename, 'w')
    file_with_params.write('#<tricky> {one}\n')
    file_with_params.write('<DATA_FILE>{value1}#<tricky> {one}\n')
    file_with_params.write('<DEA_FORM> {value2} #<tricky> {one}\n')
    file_with_params.write('   <INPUT_CATEGORIES>     \t {long one with spaces} \t'
                           ' # <tricky> {one}\n')
    file_with_params.write('\n')
    file_with_params.write('#<param1>{value1}#<tricky> {one}\n')
    file_with_params.write('<OUTPUT_CATEGORIES>{aha} #\n')
    file_with_params.write('<RETURN_TO_SCALE>{} #\n')
    file_with_params.write('#\n')
    file_with_params.close()
    p = parameters.parse_parameters_from_file(filename)
    # assert len(p.params) == 5
    assert 'DATA_FILE' in p.params
    assert p.params['DATA_FILE'] == 'value1'
    assert 'DEA_FORM' in p.params
    assert p.params['DEA_FORM'] == 'value2'
    assert 'INPUT_CATEGORIES' in p.params
    assert p.params['INPUT_CATEGORIES'] == 'long one with spaces'
    assert 'OUTPUT_CATEGORIES' in p.params
    assert p.params['OUTPUT_CATEGORIES'] == 'aha'
    assert p.params['RETURN_TO_SCALE'] == ''

    os.remove(filename)


def test_get_set_of_parameters():
    p = parameters.Parameters()
    p.update_parameter('INPUT_CATEGORIES', 'i1; i2; i3')
    s = p.get_set_of_parameters('INPUT_CATEGORIES')
    assert len(s) == 3
    assert 'i1' in s
    assert 'i2' in s
    assert 'i3' in s
    p.update_parameter('OUTPUT_CATEGORIES',
                       'i1;   i  2  ; ;  i3;    ;;;;;;;;;;')
    s = p.get_set_of_parameters('OUTPUT_CATEGORIES')
    assert len(s) == 3
    assert 'i1' in s
    assert 'i  2' in s
    assert 'i3' in s
    p.update_parameter('INPUT_CATEGORIES', 'i1')
    s = p.get_set_of_parameters('INPUT_CATEGORIES')
    assert len(s) == 1
    assert 'i1' in s
    p.update_parameter('OUTPUT_CATEGORIES', '')
    s = p.get_set_of_parameters('OUTPUT_CATEGORIES')
    assert len(s) == 0


def test_change_category_name():
    p = parameters.Parameters()
    p.update_parameter('INPUT_CATEGORIES', 'i1; i2; i3')
    p.change_category_name('i1', 'newInput')
    assert 'newInput' in p.get_set_of_parameters('INPUT_CATEGORIES')
    assert 'i1' not in p.get_set_of_parameters('INPUT_CATEGORIES')

    p.update_parameter('INPUT_CATEGORIES', 'i1; i2; i3')
    p.update_parameter('ABS_WEIGHT_RESTRICTIONS', 'i1 <= 9; i2 >= 7; 0 <= i3')
    p.change_category_name('i1', 'newInput')
    assert 'newInput' in p.get_set_of_parameters('INPUT_CATEGORIES')
    assert 'i1' not in p.get_set_of_parameters('INPUT_CATEGORIES')
    assert 'newInput <= 9' in p.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert 'i1 <= 9' not in p.get_set_of_parameters('ABS_WEIGHT_RESTRICTIONS')

    p.update_parameter('INPUT_CATEGORIES', 'i1; i2; i3')
    p.update_parameter('ABS_WEIGHT_RESTRICTIONS', 'i1 <= 9; i2 >= 7; 0 <= i3')
    p.update_parameter('PRICE_RATIO_RESTRICTIONS', 'i1/i2 >= 2; r/  i1 <= 7')
    p.update_parameter('CATEGORICAL_CATEGORY', 'category')
    p.change_category_name('i1', 'newInput')
    assert 'newInput' in p.get_set_of_parameters('INPUT_CATEGORIES')
    assert 'i1' not in p.get_set_of_parameters('INPUT_CATEGORIES')
    assert 'newInput <= 9' in p.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert 'i1 <= 9' not in p.get_set_of_parameters('ABS_WEIGHT_RESTRICTIONS')
    assert 'newInput/i2 >= 2' in p.get_set_of_parameters(
        'PRICE_RATIO_RESTRICTIONS')
    assert 'i1/i2 >= 2' not in p.get_set_of_parameters(
        'PRICE_RATIO_RESTRICTIONS')
    assert 'r/newInput <= 7' in p.get_set_of_parameters(
        'PRICE_RATIO_RESTRICTIONS')
    assert 'r/  i1 <= 7' not in p.get_set_of_parameters(
        'PRICE_RATIO_RESTRICTIONS')
    assert p.get_parameter_value('CATEGORICAL_CATEGORY') == 'category'
