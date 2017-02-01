from tkinter import Tk, StringVar, END
import pytest

from pyDEA.core.gui_modules.weight_frame_gui import WeightFrame
from pyDEA.core.data_processing.parameters import Parameters

from tests.test_gui_data_tab_frame import ParamsFrameMock


@pytest.fixture
def weight_frame(request):
    parent = Tk()
    current_categories = ['I1', 'I2', 'I3']
    params = ParamsFrameMock(parent)
    weight_frame = WeightFrame(
        params, current_categories, Parameters(), StringVar(master=parent))
    request.addfinalizer(parent.destroy)
    return weight_frame


def test_add_given_weights(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'ABS_WEIGHT_RESTRICTIONS', 'I1 >= 0.1; 0.5 >= I2')
    weight_frame._add_given_weights(
        weight_frame.abs_weights, 'ABS_WEIGHT_RESTRICTIONS')
    assert weight_frame.parent.weight_frame_name == 'Weights editor*'
    text = weight_frame.abs_weights.text.get('1.0', END)
    assert 'I1 >= 0.1' in text and '0.5 >= I2' in text
    assert weight_frame.virtual_weights.text.get('1.0', END) == '\n'
    assert weight_frame.price_ratio_weights.text.get('1.0', END) == '\n'


def test_add_given_weights_invalid(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'VIRTUAL_WEIGHT_RESTRICTIONS', 'I1 = 0.1; 0.5 >= I2')
    weight_frame._add_given_weights(
        weight_frame.virtual_weights, 'VIRTUAL_WEIGHT_RESTRICTIONS')
    assert weight_frame.parent.weight_frame_name == 'Weights editor*'
    text = weight_frame.virtual_weights.text.get('1.0', END)
    assert 'I1 = 0.1' not in text and '0.5 >= I2' in text
    assert weight_frame.abs_weights.text.get('1.0', END) == '\n'
    assert weight_frame.price_ratio_weights.text.get('1.0', END) == '\n'


def test_add_given_weights_all_invalid(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'VIRTUAL_WEIGHT_RESTRICTIONS', 'I1 = 0.1; 0.5 >= O2')
    assert weight_frame.virtual_weights.text.get('1.0', END) == '\n'
    assert weight_frame.abs_weights.text.get('1.0', END) == '\n'
    assert weight_frame.price_ratio_weights.text.get('1.0', END) == '\n'


def test_add_weights(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'ABS_WEIGHT_RESTRICTIONS', 'I1 >= 0.1; 0.5 >= I2')
    weight_frame.params.update_parameter(
        'VIRTUAL_WEIGHT_RESTRICTIONS', 'I1 = 0.1; 0.5 >= I2')
    weight_frame.params.update_parameter(
        'PRICE_RATIO_RESTRICTIONS', 'I1/I2 <=2')
    weight_frame.add_weights()
    assert weight_frame.parent.weight_frame_name == 'Weights editor*'
    abs_text = weight_frame.abs_weights.text.get('1.0', END)
    assert 'I1 >= 0.1' in abs_text and '0.5 >= I2' in abs_text
    vir_text = weight_frame.virtual_weights.text.get('1.0', END)
    assert '0.5 >= I2' in vir_text
    pr_text = weight_frame.price_ratio_weights.text.get('1.0', END)
    assert 'I1/I2 <=2' in pr_text


def test_remove_all_weights(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'ABS_WEIGHT_RESTRICTIONS', 'I1 >= 0.1; 0.5 >= I2')
    weight_frame.params.update_parameter(
        'VIRTUAL_WEIGHT_RESTRICTIONS', 'I1 = 0.1; 0.5 >= I2')
    weight_frame.params.update_parameter(
        'PRICE_RATIO_RESTRICTIONS', 'I1/I2 <=2')
    weight_frame.remove_all_weights()
    assert weight_frame.parent.weight_frame_name == 'Weights editor'
    assert weight_frame.virtual_weights.text.get('1.0', END) == '\n'
    assert weight_frame.abs_weights.text.get('1.0', END) == '\n'
    assert weight_frame.price_ratio_weights.text.get('1.0', END) == '\n'
    # parameters are not updated by weight_frame
    assert weight_frame.params.get_parameter_value(
        'ABS_WEIGHT_RESTRICTIONS') == 'I1 >= 0.1; 0.5 >= I2'
    assert weight_frame.params.get_parameter_value(
        'VIRTUAL_WEIGHT_RESTRICTIONS') == 'I1 = 0.1; 0.5 >= I2'
    assert weight_frame.params.get_parameter_value(
        'PRICE_RATIO_RESTRICTIONS') == 'I1/I2 <=2'
    # parameters are updated on validation
    weight_frame.on_validate_weights()
    assert weight_frame.params.get_parameter_value(
        'ABS_WEIGHT_RESTRICTIONS') == ''
    assert weight_frame.params.get_parameter_value(
        'VIRTUAL_WEIGHT_RESTRICTIONS') == ''
    assert weight_frame.params.get_parameter_value(
        'PRICE_RATIO_RESTRICTIONS') == ''


def test_on_validate_weights(weight_frame):
    weight_frame.params.update_parameter('INPUT_CATEGORIES', 'I1; I2; I3')
    weight_frame.params.update_parameter(
        'VIRTUAL_WEIGHT_RESTRICTIONS', 'I1 = 0.1; 0.5 >= I2')
    weight_frame.add_weights()
    weight_frame.on_validate_weights()
    assert weight_frame.params.get_parameter_value(
        'VIRTUAL_WEIGHT_RESTRICTIONS') == '0.5 >= I2'
    assert weight_frame.parent.weight_frame_name == 'Weights editor*'
    assert weight_frame.weights_status_str.get() == ''
    weight_frame.abs_weights.insert_weight('I2 == 0')
    weight_frame.on_validate_weights()
    assert weight_frame.weights_status_str.get(
    ) == 'Some of the weight restrictions cannot be parsed. \nFor error details, see Weights editor tab.'
    weight_frame.abs_weights.text.delete(1.0, END)
    weight_frame.on_validate_weights()
    assert weight_frame.weights_status_str.get() == ''
