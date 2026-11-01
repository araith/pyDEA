'''Regression tests for finite, feasible multiplier solutions and their peers.'''
import pytest
import pulp

from pyDEA.core.data_processing.input_data import InputData
from pyDEA.core.models.multiplier_model import MultiplierOutputOrientedModel
from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.models.multiplier_model_decorators import (
    MultiplierModelVRSDecorator, MultiplierModelWithDisposableCategories)
from tests.test_CRS_env_input_oriented_model import data
from tests.utils_for_tests import check_output_multiplier_solution


@pytest.fixture(params=[(False, ()), (False, ('x1',)),
                        (True, ()), (True, ('q',))])
def multiplier_solution(data, request):
    vrs, weak = request.param
    model = MultiplierModelBase(data, 1e-12, MultiplierOutputOrientedModel())
    if weak:
        model = MultiplierModelWithDisposableCategories(model, set(weak))
    if vrs:
        model = MultiplierModelVRSDecorator(model)
    return model.run(), data, weak, vrs


def test_output_multiplier_primal_dual_validity(multiplier_solution):
    solution, data, weak, vrs = multiplier_solution
    check_output_multiplier_solution(solution, data, weak, vrs)


@pytest.mark.parametrize('corruption', ['negative_input', 'nan_output',
                                        'wrong_objective', 'negative_peer'])
def test_validity_check_rejects_corrupted_solution(multiplier_solution,
                                                  corruption):
    solution, data, weak, vrs = multiplier_solution
    code = data._DMU_user_name_to_code['E']
    if corruption == 'negative_input':
        solution.input_duals[code]['x2'] = -1
    elif corruption == 'nan_output':
        solution.output_duals[code]['q'] = float('nan')
    elif corruption == 'wrong_objective':
        solution.efficiency_scores[code] = 0.1
    else:
        solution.add_lambda_variables(code, {code: -1})
    with pytest.raises(AssertionError):
        check_output_multiplier_solution(solution, data, weak, vrs)


def test_validity_check_accepts_alternative_optimal_vrs_weights(data):
    model = MultiplierModelVRSDecorator(
        MultiplierModelBase(data, 0, MultiplierOutputOrientedModel()))
    solution = model.run()
    code = data._DMU_user_name_to_code['E']
    solution.input_duals[code].update(x1=0.1, x2=0.2)
    solution.add_VRS_dual(code, 0)
    check_output_multiplier_solution(solution, data, vrs=True)


def test_cbc_retry_does_not_change_default_solver(data):
    solver = pulp.LpSolverDefault
    options = list(solver.options)
    model = MultiplierModelWithDisposableCategories(
        MultiplierModelBase(data, 1e-12, MultiplierOutputOrientedModel()),
        {'x1'})
    check_output_multiplier_solution(model.run(), data, {'x1'})
    assert pulp.LpSolverDefault is solver
    assert solver.options == options
    assert model.lp_model.solver is solver


def test_cbc_retry_preserves_precision_for_large_output_coefficients():
    # Eight significant digits in CBC's solution file produce a row
    # violation of 1.476e-6, although the internal solution is feasible.
    data = InputData()
    for name, inputs, outputs in [('A', 1, 1456),
                                  ('B', 37.58, 18080),
                                  ('C', 2, 423)]:
        data.add_coefficient(name, 'x', inputs)
        data.add_coefficient(name, 'y', outputs)
    data.add_input_category('x')
    data.add_output_category('y')
    base = MultiplierModelBase(data, 0, MultiplierOutputOrientedModel())
    model = MultiplierModelVRSDecorator(base)
    solution = model.run()
    code = data._DMU_user_name_to_code['C']
    expected_expansion = (1456 + (18080 - 1456) / (37.58 - 1)) / 423
    assert solution.efficiency_scores[code] == pytest.approx(
        1 / expected_expansion, abs=1e-8)
    model._update_lp(code)
    base._solve_lp()
    assert base.lp_model.valid(1e-6)
    assert base._has_consistent_cbc_solution()


def test_cbc_check_rejects_large_cancelling_weights(data):
    model = MultiplierModelBase(data, 0, MultiplierOutputOrientedModel())
    model.lp_model = pulp.LpProblem('unstable_weights')
    weight = model.lp_model.add_variable('weight', lowBound=0)
    intercept = model.lp_model.add_variable('intercept', lowBound=None)
    model.lp_model += weight + intercept + 1 <= 0, 'dmu'
    weight.varValue = 176421420000000.0
    intercept.varValue = -176421420000000.0
    model.lp_model.get_constraint_by_name('dmu').pi = 0
    assert not model._has_consistent_cbc_solution()


def test_cbc_rejects_inconsistent_weights_after_retry(data, monkeypatch):
    calls = []
    original_solve = pulp.COIN_CMD.actualSolve

    def corrupted_solve(solver, lp, **kwargs):
        calls.append(list(solver.options))
        status = original_solve(solver, lp, **kwargs)
        lp.variables()[0].varValue = float('nan')
        return status

    monkeypatch.setattr(pulp.COIN_CMD, 'actualSolve', corrupted_solve)
    model = MultiplierModelBase(data, 0, MultiplierOutputOrientedModel())
    with pytest.raises(ArithmeticError, match='inconsistent multiplier weights'):
        model.run()
    assert len(calls) == 2
    assert calls[1] == calls[0] + [
        'primalSimplex', 'scaling off', 'precisionOutput %.17g']