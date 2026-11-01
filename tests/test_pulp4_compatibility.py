'''Regression tests for PuLP 4's ownership, result and CBC export APIs.'''
import math

import pulp
import pytest

from pyDEA.core.models.model_base import solve_problem
from pyDEA.core.models.maximize_slacks import MaximizeSlacksModel
from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase
from pyDEA.core.models.envelopment_model import EnvelopmentModelInputOriented
from pyDEA.core.models.envelopment_model_decorators import (
    DefaultConstraintCreator, EnvelopmentModelVRSDecorator)
from pyDEA.core.models.bound_generators import generate_upper_bound_for_efficiency_score
from tests.test_CRS_env_input_oriented_model import data
from tests.utils_for_tests import check_dea_solution


@pytest.mark.parametrize('sense, bound, expected_dual', [
    (pulp.LpMaximize, 2, 1), (pulp.LpMinimize, 1, 1)])
def test_cbc_duals_follow_original_objective_sense(sense, bound, expected_dual):
    problem = pulp.LpProblem('dual_sign', sense)
    variable = problem.add_variable('x', 0)
    problem += variable
    problem += variable <= 2, 'upper'
    problem += variable >= 1, 'lower'
    stats = solve_problem(problem, pulp.COIN_CMD(msg=False))
    assert stats.status == pulp.LpSolveStatus.Optimal
    assert variable.varValue == pytest.approx(bound)
    name = 'upper' if sense == pulp.LpMaximize else 'lower'
    assert problem.get_constraint_by_name(name).pi == expected_dual


@pytest.mark.parametrize('vrs', [False, True])
def test_two_phase_uses_independent_feasible_problems(data, vrs):
    base = EnvelopmentModelBase(
        data, EnvelopmentModelInputOriented(
            generate_upper_bound_for_efficiency_score),
        DefaultConstraintCreator())
    if vrs:
        base = EnvelopmentModelVRSDecorator(base)
    model = MaximizeSlacksModel(base)
    solution = model.run()
    check_dea_solution(solution, data, vrs=vrs)
    second = model._slack_model
    assert second.lp_model is not base.lp_model
    assert model.second_solution.efficiency_scores == solution.efficiency_scores
    for dmu in data.DMU_codes:
        assert model.second_solution.lp_status[dmu] == pulp.LpSolveStatus.Optimal
        peers = model.second_solution.get_lambda_variables(dmu)
        score = solution.efficiency_scores[dmu]
        for cat in data.input_categories | data.output_categories:
            projected = math.fsum(value * data.coefficients[peer, cat]
                                  for peer, value in peers.items())
            target = data.coefficients[dmu, cat]
            if cat in data.input_categories:
                assert projected <= target * score + 1e-6
            else:
                assert projected >= target - 1e-6
    assert second.lp_model.valid(1e-6)
    # Rebuilding must not reuse Rust handles from either previous problem.
    repeated = model.run()
    assert repeated.efficiency_scores == solution.efficiency_scores