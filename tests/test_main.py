import os
import shutil

from pyDEA.main import main
from pyDEA.core.data_processing.parameters import parse_parameters_from_file
from pyDEA.core.utils.dea_utils import auto_name_if_needed


def test_main_correct_params():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    main(filename)
    assert os.path.exists(auto_name) is True
    os.remove(auto_name)


def test_main_output_format():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xls')
    main(filename, output_format='xls')
    assert os.path.exists(auto_name) is True
    os.remove(auto_name)


def test_main_output_dir():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xls')
    output_dir = 'tests'
    main(filename, output_format='xls', output_dir=output_dir)
    output_name = os.path.join(output_dir, auto_name)
    assert os.path.exists(output_name) is True
    os.remove(output_name)


def test_main_different_sheet():
    filename = 'tests/params_to_test_main.txt'
    main(filename, output_format='', sheet_name_usr='Sheet2')
    assert os.path.exists('haha') is True
    shutil.rmtree('haha')


def test_main_csv():
    filename = 'tests/params_to_test_main_csv.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    main(filename, sheet_name_usr='haha')
    assert os.path.exists(auto_name) is True
    os.remove(auto_name)
