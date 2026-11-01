from pulp import LpSolveStatus

LpStatusOptimal = LpSolveStatus.Optimal
import math
import pytest

from pyDEA.core.data_processing.read_data import read_data
from pyDEA.core.data_processing.read_data import construct_input_data_instance
from pyDEA.core.data_processing.read_data import validate_data
from pyDEA.core.data_processing.read_data import convert_to_dictionary
from pyDEA.core.utils.dea_utils import clean_up_pickled_files


EQ_TOLERANCE = 1e-10
WEIGHT_RESTRICTION_TOLERANCE = 1e-7


@pytest.fixture
def DEA_example2_data(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data.xlsx')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    request.addfinalizer(clean_up_pickled_files)
    return construct_input_data_instance(categories, coefficients)


@pytest.fixture
def categorical_from_book(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/categorical_test_from_book.xlsx')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    data = construct_input_data_instance(categories, coefficients)
    data.add_input_category('Area')
    data.add_input_category('Books')
    data.add_input_category('Staff')
    data.add_output_category('Regist')
    data.add_output_category('Borrow')
    request.addfinalizer(clean_up_pickled_files)
    return data


@pytest.fixture
def DEA_example_data(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example_data.xlsx')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    request.addfinalizer(clean_up_pickled_files)
    return construct_input_data_instance(categories, coefficients)


@pytest.fixture
def categorical_data(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/categorical_test.xlsx')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    request.addfinalizer(clean_up_pickled_files)
    return construct_input_data_instance(categories, coefficients)


def check_onion_ranks(input_data, dmus, expected_ranks, ranks):
    for count, dmu in enumerate(dmus):
        print('dmu', dmu, 'rank', ranks[input_data._DMU_user_name_to_code[dmu]],
              'expected_ranks', expected_ranks[count])
        assert ranks[input_data._DMU_user_name_to_code[
            dmu]] == expected_ranks[count]


def check_lambda_variables(dmu1, dmu2, value, model_solution, data):
    ''' (str, str, double, Solution, InputData) -> NoneType
    '''
    dmu1_code = data._DMU_user_name_to_code[dmu1]
    dmu2_code = data._DMU_user_name_to_code[dmu2]
    lambda_var = model_solution.get_lambda_variables(
        dmu1_code).get(dmu2_code, 0)
    assert abs(lambda_var - value) <= EQ_TOLERANCE


def check_categories_for_dmu(dmu, categories, expected_values,
                             model_solution, data):
    dmu_code = data._DMU_user_name_to_code[dmu]
    for count, category in enumerate(categories):
        if category in data.input_categories:
            dual_var = model_solution.get_input_dual(dmu_code, category)
        elif category in data.output_categories:
            dual_var = model_solution.get_output_dual(dmu_code, category)
        assert abs(dual_var - expected_values[count]) <= EQ_TOLERANCE


def check_efficiency_scores(dmus, expected_scores, model_solution,
                            data, tolerance=EQ_TOLERANCE):
    for count, dmu in enumerate(dmus):
        dmu_code = data._DMU_user_name_to_code[dmu]
        print('DMU: {0}, score: {1}'.format(
            dmu, model_solution.efficiency_scores[dmu_code]))
        assert abs(model_solution.efficiency_scores[
                   dmu_code] - expected_scores[count]) <= tolerance


def check_optimal_solution_status_and_sizes(model_solution, data):
    for dmu_code in data.DMU_codes:
        assert model_solution.lp_status[dmu_code] == LpStatusOptimal
        assert len(model_solution.input_duals[dmu_code]) == len(
            data.input_categories)
        assert len(model_solution.output_duals[dmu_code]) == len(
            data.output_categories)


def check_VRS_duals(dmus, expected_values, model_solution, data):
    for count, dmu in enumerate(dmus):
        assert model_solution.get_VRS_dual(data._DMU_user_name_to_code[
                                           dmu]) == expected_values[count]


def check_output_multiplier_solution(model_solution, data,
                                     weakly_disposable=(), vrs=False,
                                     lower_bound=0.0, tolerance=1e-7):
    '''Check the returned weights and peers, not just the solver status.

    CBC writes rounded solution values, so use an absolute residual tolerance
    rather than a relative tolerance that would accept cancellation at 1e10.
    Alternative optimal weights are allowed only if both DEA formulations
    are feasible and their objectives agree (strong duality).
    '''
    check_optimal_solution_status_and_sizes(model_solution, data)
    for dmu in data.DMU_codes:
        inputs = model_solution.input_duals[dmu]
        outputs = model_solution.output_duals[dmu]
        intercept = model_solution.get_VRS_dual(dmu) if vrs else 0
        score = model_solution.efficiency_scores[dmu]
        assert math.isfinite(score) and score > 0
        assert math.isfinite(intercept)
        for category, weight in list(inputs.items()) + list(outputs.items()):
            assert math.isfinite(weight), (dmu, category, weight)
            if category not in weakly_disposable:
                assert weight >= lower_bound - tolerance, (dmu, category, weight)

        normalization = math.fsum(data.coefficients[dmu, cat] * weight
                                  for cat, weight in outputs.items())
        assert normalization == pytest.approx(1, abs=tolerance, rel=0)
        objective = math.fsum(
            [data.coefficients[dmu, cat] * weight
             for cat, weight in inputs.items()] + [intercept])
        assert objective == pytest.approx(1 / score, abs=tolerance, rel=0)

        peers = model_solution.get_lambda_variables(dmu)
        for peer, value in peers.items():
            assert peer in data.DMU_codes
            assert math.isfinite(value) and value >= -tolerance
        if vrs:
            assert math.fsum(peers.values()) == pytest.approx(
                1, abs=tolerance, rel=0)

        for peer in data.DMU_codes:
            residual = math.fsum(
                [data.coefficients[peer, cat] * weight
                 for cat, weight in outputs.items()] +
                [-data.coefficients[peer, cat] * weight
                 for cat, weight in inputs.items()] + [-intercept])
            assert residual <= tolerance, (dmu, peer, residual)
            assert abs(peers.get(peer, 0) * residual) <= tolerance

        for category in data.input_categories | data.output_categories:
            projected = math.fsum(value * data.coefficients[peer, category]
                                  for peer, value in peers.items())
            target = data.coefficients[dmu, category]
            if category in data.output_categories:
                target /= score
            residual = projected - target
            if category in weakly_disposable:
                assert abs(residual) <= tolerance, (dmu, category, residual)
            elif category in data.input_categories:
                assert residual <= tolerance, (dmu, category, residual)
            else:
                assert residual >= -tolerance, (dmu, category, residual)


def check_dea_solution(solution, data, weakly_disposable=(), vrs=False,
                       non_discretionary=(), tolerance=1e-7):
    '''Accept alternative optima only with primal/dual feasibility and equality.

    Unlike fixed-weight assertions this is independent of the simplex basis.
    Absolute tolerances deliberately reject huge rounded, cancelling weights.
    '''
    check_optimal_solution_status_and_sizes(solution, data)
    input_oriented = solution.orientation == 'input'
    for dmu in data.DMU_codes:
        inputs = solution.input_duals[dmu]
        outputs = solution.output_duals[dmu]
        intercept = solution.get_VRS_dual(dmu) if vrs else 0
        score = solution.efficiency_scores[dmu]
        assert math.isfinite(score) and score > 0
        assert math.isfinite(intercept)
        weights = dict(inputs, **outputs)
        for category, weight in weights.items():
            assert math.isfinite(weight), (dmu, category, weight)
            if category not in weakly_disposable:
                assert weight >= -tolerance, (dmu, category, weight)

        normalized = inputs if input_oriented else outputs
        objective_weights = outputs if input_oriented else inputs
        normalization = math.fsum(
            data.coefficients[dmu, cat] * weight
            for cat, weight in normalized.items()
            if cat not in non_discretionary)
        assert normalization == pytest.approx(1, abs=tolerance, rel=0)
        objective = math.fsum(
            [data.coefficients[dmu, cat] * weight
             for cat, weight in objective_weights.items()] +
            [-data.coefficients[dmu, cat] * weight
             for cat, weight in normalized.items()
             if cat in non_discretionary] + [intercept])
        radial = score if input_oriented else 1 / score
        assert objective == pytest.approx(radial, abs=tolerance, rel=0)

        peers = solution.get_lambda_variables(dmu)
        for peer, value in peers.items():
            assert peer in data.DMU_codes
            assert math.isfinite(value) and value >= -tolerance
        if vrs:
            assert math.fsum(peers.values()) == pytest.approx(
                1, abs=tolerance, rel=0)
        for peer in data.DMU_codes:
            residual = math.fsum(
                [data.coefficients[peer, cat] * w for cat, w in outputs.items()] +
                [-data.coefficients[peer, cat] * w for cat, w in inputs.items()] +
                [intercept if input_oriented else -intercept])
            assert residual <= tolerance, (dmu, peer, residual)
            assert abs(peers.get(peer, 0) * residual) <= tolerance
        for category in weights:
            projected = math.fsum(value * data.coefficients[peer, category]
                                  for peer, value in peers.items())
            target = data.coefficients[dmu, category]
            oriented = (category in inputs) == input_oriented
            if oriented and category not in non_discretionary:
                target *= radial
            residual = projected - target
            if category in weakly_disposable:
                assert abs(residual) <= tolerance, (dmu, category, residual)
            elif category in inputs:
                assert residual <= tolerance, (dmu, category, residual)
            else:
                assert residual >= -tolerance, (dmu, category, residual)


def _check_lower_bound(dual_value, lower_bound):
    assert dual_value + WEIGHT_RESTRICTION_TOLERANCE >= lower_bound


def _check_upper_bound(dual_value, upper_bound):
    assert dual_value - WEIGHT_RESTRICTION_TOLERANCE <= upper_bound


def _helper_function_for_checking_limits(category, model_solution,
                                         categories, bound, get_dual_func,
                                         bool_func,
                                         process_bound):
    if category in categories:
        for dmu_code in model_solution._input_data.DMU_codes:
            if model_solution.lp_status[dmu_code] == LpStatusOptimal:
                dual_value = get_dual_func(dmu_code, category)
                coeff = model_solution._input_data.coefficients[
                    dmu_code, category]
                bool_func(dual_value, process_bound(bound, coeff))


def _check_if_category_is_within_limits(model_solution, bounds, process_bound):
    for category, (lower_bound, upper_bound) in bounds.items():
        if lower_bound:
            _helper_function_for_checking_limits(
                category, model_solution,
                model_solution._input_data.input_categories,
                lower_bound, model_solution.get_input_dual,
                _check_lower_bound, process_bound)

            _helper_function_for_checking_limits(
                category, model_solution,
                model_solution._input_data.output_categories,
                lower_bound, model_solution.get_output_dual,
                _check_lower_bound, process_bound)

        if upper_bound:
            _helper_function_for_checking_limits(
                category, model_solution,
                model_solution._input_data.input_categories,
                upper_bound, model_solution.get_input_dual,
                _check_upper_bound, process_bound)

            _helper_function_for_checking_limits(
                category, model_solution,
                model_solution._input_data.output_categories,
                upper_bound, model_solution.get_output_dual,
                _check_upper_bound, process_bound)


def _process_abs_bounds(bound, coeff):
    return bound


def check_if_category_is_within_abs_limits(model_solution, bounds):
    _check_if_category_is_within_limits(
        model_solution, bounds, _process_abs_bounds)


def _process_virtual_bounds(bound, coeff):
    return bound / coeff


def check_if_category_is_within_virtual_limits(model_solution, bounds):
    _check_if_category_is_within_limits(
        model_solution, bounds, _process_virtual_bounds)


def _get_proper_dual(category, model_solution, dmu_code):
    if category in model_solution._input_data.input_categories:
        return model_solution.get_input_dual(dmu_code, category)
    elif category in model_solution._input_data.output_categories:
        return model_solution.get_output_dual(dmu_code, category)
    return None


def check_if_category_is_within_price_ratio_constraints(model_solution, bounds):
    for (category_in_nom, category_in_denom), (lower_bound, upper_bound) in bounds.items():
        if lower_bound:
            for dmu_code in model_solution._input_data.DMU_codes:
                if model_solution.lp_status[dmu_code] == LpStatusOptimal:
                    dual_value = _get_proper_dual(
                        category_in_nom, model_solution, dmu_code)
                    dual_value_denom = _get_proper_dual(
                        category_in_denom, model_solution, dmu_code)
                    assert dual_value + WEIGHT_RESTRICTION_TOLERANCE >= lower_bound * dual_value_denom

        if upper_bound:
            for dmu_code in model_solution._input_data.DMU_codes:
                if model_solution.lp_status[dmu_code] == LpStatusOptimal:
                    dual_value = _get_proper_dual(
                        category_in_nom, model_solution, dmu_code)
                    dual_value_denom = _get_proper_dual(
                        category_in_denom, model_solution, dmu_code)
                    assert dual_value - WEIGHT_RESTRICTION_TOLERANCE <= upper_bound * dual_value_denom
