from pyDEA.core.utils.model_builder import build_models
from pyDEA.core.data_processing.parameters import parse_parameters_from_file
from pyDEA.core.data_processing.read_data_from_xls import construct_input_data_instance
from pyDEA.core.data_processing.read_data_from_xls import read_data, convert_to_dictionary


def _construct_params_and_input():
    filename = 'tests/params_new_format.txt'
    params = parse_parameters_from_file(filename)
    categories, data, dmu_name, sheet_name = read_data(
        params.get_parameter_value('DATA_FILE'))
    coefficients, has_same_dmus = convert_to_dictionary(data)
    model_input = construct_input_data_instance(categories, coefficients)
    return params, model_input


def _check_params_are_the_same(params_to_check, params, except_params):
    for key, value in params.params.items():
        if key not in except_params:
            assert value == params_to_check.params[key]


def test_build_models_one_model():
    params, model_input = _construct_params_and_input()
    models, all_params = build_models(params, model_input)
    assert len(models) == 1 and len(all_params) == 1
    _check_params_are_the_same(all_params[0], params, [])


def test_build_models_two_models():
    params, model_input = _construct_params_and_input()
    params.update_parameter('RETURN_TO_SCALE', 'both')
    models, all_params = build_models(params, model_input)
    assert len(models) == 2 and len(all_params) == 2
    assert (all_params[0].get_parameter_value('RETURN_TO_SCALE') == 'VRS' or
            all_params[1].get_parameter_value('RETURN_TO_SCALE') == 'VRS')
    assert (all_params[0].get_parameter_value('RETURN_TO_SCALE') == 'CRS' or
            all_params[1].get_parameter_value('RETURN_TO_SCALE') == 'CRS')
    _check_params_are_the_same(all_params[0], params, ['RETURN_TO_SCALE'])
    _check_params_are_the_same(all_params[1], params, ['RETURN_TO_SCALE'])


def test_build_models_four_models():
    params, model_input = _construct_params_and_input()
    params.update_parameter('RETURN_TO_SCALE', 'both')
    params.update_parameter('ORIENTATION', 'both')
    models, all_params = build_models(params, model_input)
    assert len(models) == 4 and len(all_params) == 4
    assert (all_params[0].get_parameter_value('RETURN_TO_SCALE') == 'VRS' or
            all_params[1].get_parameter_value('RETURN_TO_SCALE') == 'VRS')
    assert (all_params[0].get_parameter_value('RETURN_TO_SCALE') == 'CRS' or
            all_params[1].get_parameter_value('RETURN_TO_SCALE') == 'CRS')
    assert (all_params[0].get_parameter_value('ORIENTATION') == 'input' or
            all_params[1].get_parameter_value('ORIENTATION') == 'input')
    assert (all_params[0].get_parameter_value('ORIENTATION') == 'output' or
            all_params[1].get_parameter_value('ORIENTATION') == 'output')
    for params_to_check in all_params:
        _check_params_are_the_same(params_to_check, params, [
                                   'RETURN_TO_SCALE', 'ORIENTATION'])
