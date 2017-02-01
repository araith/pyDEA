import pytest

from pyDEA.core.data_processing.targets_and_slacks import calculate_target
from pyDEA.core.data_processing.targets_and_slacks import calculate_radial_reduction
from pyDEA.core.data_processing.targets_and_slacks import calculate_non_radial_reduction
from pyDEA.core.data_processing.input_data import InputData


@pytest.fixture
def data(request):
    data = InputData()
    data.add_coefficient('dmu1', 'x1', 2.4)
    data.add_coefficient('dmu1', 'x2', 5)
    data.add_coefficient('dmu1', 'q', 12)
    data.add_coefficient('dmu2', 'x1', 3)
    data.add_coefficient('dmu2', 'x2', 7)
    data.add_coefficient('dmu2', 'q', 1.5)
    data.add_input_category('x1')
    data.add_input_category('x2')
    data.add_output_category('q')
    return data


def test_calculate_target():
    category = 'I1'
    lambda_vars = {'dmu_0': 0.5, 'dmu_1': 0.23, 'dmu_2': 0.27}
    coefficients = {('dmu_0', 'I1'): 2, ('dmu_1', 'I1'): 5, ('dmu_2', 'I1'): 4}
    target = calculate_target(category, lambda_vars, coefficients)
    assert target == 0.5 * 2 + 0.23 * 5 + 0.27 * 4


def test_calculate_radial_reduction(data):
    dmu_code = data._DMU_user_name_to_code['dmu1']
    category = 'x1'
    efficiency_score = 0.5
    orientation = 'input'
    rad_reduction = calculate_radial_reduction(dmu_code, category, data,
                                               efficiency_score, orientation)
    assert rad_reduction == (0.5 - 1) * 2.4
    orientation = 'output'
    rad_reduction = calculate_radial_reduction(dmu_code, category, data,
                                               efficiency_score, orientation)
    assert rad_reduction == 0
    orientation = 'output'
    category = 'q'
    rad_reduction = calculate_radial_reduction(dmu_code, category, data,
                                               efficiency_score, orientation)
    assert rad_reduction == (1 / 0.5 - 1) * 12
    orientation = 'input'
    rad_reduction = calculate_radial_reduction(dmu_code, category, data,
                                               efficiency_score, orientation)
    assert rad_reduction == 0


def test_calculate_non_radial_reduction():
    assert calculate_non_radial_reduction(5, 0, 5) == 0
    assert calculate_non_radial_reduction(10.37740112, -5.62259888, 16) == 0
    assert (abs(calculate_non_radial_reduction(15.51468918, 0, 13) -
                2.51468918) <= 1e-8)
