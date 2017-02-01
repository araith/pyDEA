from tkinter import END
import pytest

from pyDEA.core.gui_modules.text_for_weights_gui import TextForWeights
from pyDEA.core.data_processing.parameters import Parameters


@pytest.fixture
def text_frame(request):
    categories = ['I1', 'I2', 'O1', 'O2']
    text_frame = TextForWeights(None, 'Absolute', 'Input <= 0.5', categories,
                                Parameters(), 'ABS_WEIGHT_RESTRICTIONS')
    request.addfinalizer(text_frame.destroy)
    return text_frame


@pytest.fixture
def text_frame_price_ratio(request):
    categories = ['I1', 'I2', 'O1', 'O2']
    text_frame = TextForWeights(None, 'price ratio', 'Input <= 0.5', categories,
                                Parameters(), 'PRICE_RATIO_RESTRICTIONS', True)
    request.addfinalizer(text_frame.destroy)
    return text_frame    


def test_insert_weight(text_frame):
    text_frame.insert_weight('I1 <= 0.8')
    text_frame.insert_weight('I2 >= 0.01')
    for line in text_frame.text.get('1.0', 'end-1c').splitlines():
        assert line == 'I1 <= 0.8' or line == 'I2 >= 0.01'


def test_delete_weights(text_frame):
    text_frame.insert_weight('I1 <= 0.8')
    text_frame.insert_weight('I2 >= 0.01')
    text_frame.delete_weights()
    assert text_frame.error_tag_exists is False
    assert text_frame.text.get(1.0, END) == '\n'


def test_validate_weights_ok(text_frame):
    weights = ['I1 <= 0.8', 'I2 >= 0.01', 'O1 <= 4', 'O2 >= 0.1']
    for weight in weights:
        text_frame.insert_weight(weight)
    assert text_frame.validate_weights() is True
    assert text_frame.error_tag_exists is False
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    for weight in weights:
        assert weight in param_vals


def test_validate_weights_wrong_categories(text_frame):
    text_frame.insert_weight('I1 <= 0.8')
    text_frame.insert_weight('I2 >= 0.01')
    text_frame.insert_weight('wrongCategory1 <= 4')
    assert text_frame.validate_weights() is True
    assert text_frame.error_tag_exists is True
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert 'I1 <= 0.8' in param_vals
    assert 'I2 >= 0.01' in param_vals


def test_validate_weights_invalid_expression(text_frame):
    text_frame.insert_weight('I1 <= 0.8')
    text_frame.insert_weight('I2 == 0.01')
    assert text_frame.validate_weights() is True
    assert text_frame.error_tag_exists is True
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert 'I1 <= 0.8' in param_vals


def test_validate_weights_only_invalid_expressions(text_frame):
    text_frame.insert_weight('I1 0.8')
    text_frame.insert_weight('I2 == 0.01')
    assert text_frame.validate_weights() is False
    assert text_frame.error_tag_exists is True
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert param_vals == set()
    text_frame.insert_weight('O2 >= 0.0003')
    assert text_frame.validate_weights() is True
    assert text_frame.error_tag_exists is True
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert 'O2 >= 0.0003' in param_vals


def test_validate_weights_wrong_constraint_type(text_frame):
    text_frame.insert_weight('I1/I2 >= 2')
    assert text_frame.validate_weights() is False
    assert text_frame.error_tag_exists is True
    param_vals = text_frame.params.get_set_of_parameters(
        'ABS_WEIGHT_RESTRICTIONS')
    assert param_vals == set()


def test_validate_weights_wrong_constraint_type_price_ratio(text_frame_price_ratio):
    text_frame_price_ratio.insert_weight('I1 >= 2')
    assert text_frame_price_ratio.validate_weights() is False
    assert text_frame_price_ratio.error_tag_exists is True
    param_vals = text_frame_price_ratio.params.get_set_of_parameters(
        'PRICE_RATIO_RESTRICTIONS')
    assert param_vals == set()
