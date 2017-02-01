from pulp import LpStatusOptimal
import pytest

from pyDEA.core.data_processing.read_data_from_xls import read_data
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import validate_data
from pyDEA.core.data_processing.read_data_from_xls import convert_to_dictionary
from pyDEA.core.utils.dea_utils import clean_up_pickled_files


EQ_TOLERANCE = 1e-10
WEIGHT_RESTRICTION_TOLERANCE = 1e-7


@pytest.fixture
def DEA_example2_data(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/DEA_example2_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    request.addfinalizer(clean_up_pickled_files)
    return construct_input_data_instance(categories, coefficients)


@pytest.fixture
def categorical_from_book(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/categorical_test_from_book.xls')
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
        'tests/DEA_example_data.xls')
    coefficients, has_same_dmus = convert_to_dictionary(xls_data)
    assert has_same_dmus is False
    assert validate_data(categories, coefficients) is True
    request.addfinalizer(clean_up_pickled_files)
    return construct_input_data_instance(categories, coefficients)


@pytest.fixture
def categorical_data(request):
    categories, xls_data, dmu_name, sheet_name = read_data(
        'tests/categorical_test.xls')
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
