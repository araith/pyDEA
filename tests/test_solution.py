import pytest
from pulp import LpStatusOptimal

from pyDEA.core.data_processing.solution import Solution, SolutionWithVRS, SolutionWithSuperEfficiency
from pyDEA.core.data_processing.input_data import InputData

from tests.test_input_data import data


def test_solution_add_efficiency_score(data):
    s = Solution(data)
    s.add_efficiency_score('dmu_1', 0.5)
    assert s.get_efficiency_score('dmu_1') == 0.5


def test_solution_add_invalid_efficiency_score(data):
    s = Solution(data)
    with pytest.raises(ValueError) as excinfo:
        s.add_efficiency_score('dmu_4', 2)
    assert str(excinfo.value) == 'Efficiency score must be within [0, 1]'


def test_solution_add_existing_efficiency_score(data):
    s = Solution(data)
    s.add_efficiency_score('dmu_1', 0.5)
    s.add_efficiency_score('dmu_1', 0.3)
    assert s.get_efficiency_score('dmu_1') == 0.3


def test_solution_add_efficiency_score_with_invalid_dmu_code(data):
    s = Solution(data)
    with pytest.raises(ValueError) as excinfo:
        s.add_efficiency_score('dmu_2', 0.4)
    assert str(excinfo.value) == 'DMU code dmu_2 does not exist'


def test_solution_get_not_existing_efficiency_score(data):
    s = Solution(data)
    with pytest.raises(KeyError) as excinfo:
        s.get_efficiency_score('dmu_1')
    assert str(excinfo.value) == "'dmu_1'"


def test_solution_add_lambda_variables(data):
    s = Solution(data)
    s.add_lp_status('dmu_1', LpStatusOptimal)
    s.add_lp_status('dmu_4', LpStatusOptimal)
    s.add_efficiency_score('dmu_1', 0.5)
    s.add_efficiency_score('dmu_4', 0.9999999)
    s.add_lambda_variables('dmu_1', {'dmu_1': 0, 'dmu_4': 1.5})
    assert s.is_efficient(data._DMU_user_name_to_code['dmu1']) is False
    s.add_lambda_variables('dmu_4', {'dmu_1': 0, 'dmu_4': 1.5})
    assert s.is_efficient(data._DMU_user_name_to_code['dmu2']) is True
    l_vars = s.get_lambda_variables('dmu_1')
    assert len(l_vars) == 2
    assert l_vars['dmu_1'] == 0
    assert l_vars['dmu_4'] == 1.5
    with pytest.raises(ValueError) as excinfo:
        s.add_lambda_variables('dmu_1', {'dmu_1': 0, 'dmu_3': 1.5})
    assert str(excinfo.value) == 'DMU code dmu_3 does not exist'


def test_solution_add_input_duals(data):
    data.add_input_category('x1')
    data.add_input_category('x2')
    s = Solution(data)
    s.add_input_dual('dmu_1', 'x1', 2.5)
    s.add_input_dual('dmu_1', 'x2', 0.1)
    assert len(s.input_duals['dmu_1']) == 2
    assert s.get_input_dual('dmu_1', 'x1') == 2.5
    assert s.get_input_dual('dmu_1', 'x2') == 0.1
    with pytest.raises(ValueError) as excinfo:
        s.add_input_dual('dmu_1', 'x3', 0)
    assert str(excinfo.value) == 'x3 is not a valid input category'
    with pytest.raises(ValueError) as excinfo:
        s.add_input_dual('dmu_3', 'x3', 0)
    assert str(excinfo.value) == 'DMU code dmu_3 does not exist'
    s.add_input_dual('dmu_1', 'x1', -5)
    # duals can be negative
    assert s.get_input_dual('dmu_1', 'x1') == -5
    s.add_input_dual('dmu_1', 'x1', 5)
    assert len(s.input_duals['dmu_1']) == 2
    assert s.get_input_dual('dmu_1', 'x1') == 5
    with pytest.raises(KeyError) as excinfo:
        s.get_input_dual('dmu_3', 'x1')
    assert str(excinfo.value) == "'dmu_3'"
    with pytest.raises(KeyError) as excinfo:
        s.get_input_dual('dmu_1', 'wwq')
    assert str(excinfo.value) == "'wwq'"


def test_solution_add_output_duals(data):
    data.add_output_category('q')
    s = Solution(data)
    s.add_output_dual('dmu_1', 'q', 10)
    assert len(s.output_duals['dmu_1']) == 1
    assert s.get_output_dual('dmu_1', 'q') == 10
    with pytest.raises(ValueError) as excinfo:
        s.add_output_dual('dmu_1', 'qq', 0)
    assert str(excinfo.value) == 'qq is not a valid output category'
    with pytest.raises(ValueError) as excinfo:
        s.add_output_dual('dmu_3', 'q', 0)
    assert str(excinfo.value) == 'DMU code dmu_3 does not exist'
    s.add_output_dual('dmu_1', 'q', -5)
    assert s.get_output_dual('dmu_1', 'q') == -5
    s.add_output_dual('dmu_1', 'q', 5)
    assert len(s.output_duals['dmu_1']) == 1
    assert s.get_output_dual('dmu_1', 'q') == 5
    with pytest.raises(KeyError) as excinfo:
        s.get_output_dual('dmu_3', 'q')
    assert str(excinfo.value) == "'dmu_3'"
    with pytest.raises(KeyError) as excinfo:
        s.get_output_dual('dmu_1', 'wwq')
    assert str(excinfo.value) == "'wwq'"


def test_solution_lp_status(data):
    s = Solution(data)
    s.add_lp_status('dmu_1', LpStatusOptimal)
    assert s.lp_status['dmu_1'] == LpStatusOptimal
    with pytest.raises(ValueError) as excinfo:
        s.add_lp_status('dmu_3', LpStatusOptimal)
    assert str(excinfo.value) == 'DMU code dmu_3 does not exist'
    s.add_lp_status('dmu_1', 'Something')
    assert s.lp_status['dmu_1'] == 'Something'


def test_solution_add_VRS_dual(data):
    basic_solution = Solution(data)
    s = SolutionWithVRS(basic_solution)
    s.add_VRS_dual('dmu_1', 0.5)
    assert s.get_VRS_dual('dmu_1') == 0.5
    s.add_VRS_dual('dmu_1', -5)
    assert s.get_VRS_dual('dmu_1') == -5
    with pytest.raises(KeyError) as excinfo:
        s.get_VRS_dual('dmu_3')
    assert str(excinfo.value) == "'dmu_3'"
    with pytest.raises(ValueError) as excinfo:
        s.add_VRS_dual('dmu_3', 0)
    assert str(excinfo.value) == 'DMU code dmu_3 does not exist'


def test_solution_with_super_efficiency(data):
    s = SolutionWithSuperEfficiency(data)
    s.add_efficiency_score('dmu_1', 0.5)
    assert s.get_efficiency_score('dmu_1') == 0.5
    s.add_efficiency_score('dmu_1', 1.2)
    assert s.get_efficiency_score('dmu_1') == 1.2
    with pytest.raises(ValueError) as excinfo:
        s.add_efficiency_score('dmu_1', -2)
    assert str(excinfo.value) == 'Efficiency score must be >= 0'
