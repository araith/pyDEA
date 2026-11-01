import os
import shutil
import csv
import math
from openpyxl import load_workbook

from pyDEA.main import main
from pyDEA.core.data_processing.parameters import parse_parameters_from_file
from pyDEA.core.utils.dea_utils import auto_name_if_needed


def check_result_workbook(filename):
    workbook = load_workbook(filename, data_only=True)
    try:
        assert {'EfficiencyScores', 'Peers', 'InputOutputWeights',
                'Targets', 'Parameters'} <= set(workbook.sheetnames)
        rows = list(workbook['EfficiencyScores'].values)
        assert rows[1][:2] == ('DMU', 'Efficiency')
        results = rows[2:]
        assert len(results) == 11
        assert {row[0] for row in results} == set('ABCDEFGHIJK')
        for row in results:
            assert isinstance(row[1], (int, float))
            assert math.isfinite(row[1]) and 0 < row[1] <= 1 + 1e-7
    finally:
        workbook.close()


def test_main_correct_params():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    main(filename)
    assert os.path.exists(auto_name) is True
    check_result_workbook(auto_name)
    os.remove(auto_name)


def test_main_output_format():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    main(filename, output_format='xlsx')
    assert os.path.exists(auto_name) is True
    check_result_workbook(auto_name)
    os.remove(auto_name)


def test_main_output_dir():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    output_dir = 'tests'
    main(filename, output_format='xlsx', output_dir=output_dir)
    output_name = os.path.join(output_dir, auto_name)
    assert os.path.exists(output_name) is True
    check_result_workbook(output_name)
    os.remove(output_name)


def test_main_different_sheet():
    filename = 'tests/params_to_test_main.txt'
    main(filename, output_format='', sheet_name_usr='Sheet2')
    assert os.path.exists('haha') is True
    with open('haha/EfficiencyScores.csv', newline='') as stream:
        rows = [row for row in csv.reader(stream) if row]
    assert [value.strip() for value in rows[0]] == ['input orientation', 'VRS']
    assert rows[1][:2] == ['DMU', 'Efficiency']
    assert len(rows[2:]) == 5
    assert {row[0] for row in rows[2:]} == set('abcde')
    assert all(float(row[1]) == 1 for row in rows[2:])
    shutil.rmtree('haha')


def test_main_csv():
    filename = 'tests/params_to_test_main_csv.txt'
    params = parse_parameters_from_file(filename)
    auto_name = auto_name_if_needed(params, 'xlsx')
    main(filename, sheet_name_usr='haha')
    assert os.path.exists(auto_name) is True
    check_result_workbook(auto_name)
    os.remove(auto_name)
