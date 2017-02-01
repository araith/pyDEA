from tkinter import Tk, DISABLED, NORMAL
import pytest

from pyDEA.core.gui_modules.options_frame_gui import OptionsFrame
from pyDEA.core.data_processing.parameters import Parameters

from tests.test_gui_data_tab_frame import CategoryFrameMock


class OptionsFrameMock(OptionsFrame):

    def __init__(self, parent, params, current_categories,
                 input_categories_frame,
                 output_categories_frame, name='Options', *args, **kw):
        super().__init__(parent, params, current_categories,
                         input_categories_frame,
                         output_categories_frame, name, *args, **kw)
        self.warning_was_called = False
        self.count_warning = 0
        self.combobox_warning_called = False
        self.multi_tol_warning_called = False

    def _show_warning(self, param_name):
        self.warning_was_called = True
        self.count_warning += 1

    def _show_warning_combobox(self, categorical_param):
        self.combobox_warning_called = True

    def _show_multi_tol_warning(self, tol_str):
        self.multi_tol_warning_called = True


@pytest.fixture
def options_frame(request):
    parent = Tk()
    params = Parameters()
    current_categories = []
    options_frame = OptionsFrameMock(parent, params, current_categories,
                                     CategoryFrameMock(),
                                     CategoryFrameMock())
    request.addfinalizer(parent.destroy)
    return options_frame


def test_creation(options_frame):
    assert options_frame.options['MAXIMIZE_SLACKS'].get() == 0
    assert options_frame.options['USE_SUPER_EFFICIENCY'].get() == 0
    assert options_frame.options['PEEL_THE_ONION'].get() == 0
    assert options_frame.options['RETURN_TO_SCALE'].get() == 1
    assert options_frame.options['ORIENTATION'].get() == 1
    assert options_frame.options['DEA_FORM'].get() == 1


def test_radio_btn_change(options_frame):
    options_frame.options['RETURN_TO_SCALE'].set(2)
    options_frame.radio_btn_change('RETURN_TO_SCALE')
    assert options_frame.options['RETURN_TO_SCALE'].get() == 2
    assert options_frame.params.get_parameter_value('RETURN_TO_SCALE') == 'CRS'
    options_frame.options['RETURN_TO_SCALE'].set(1)
    options_frame.radio_btn_change('RETURN_TO_SCALE')
    assert options_frame.options['RETURN_TO_SCALE'].get() == 1
    assert options_frame.params.get_parameter_value('RETURN_TO_SCALE') == 'VRS'


def test_radio_btn_change_with_max_slack_on(options_frame):
    options_frame.options['MAXIMIZE_SLACKS'].set(1)
    options_frame.on_check_box_click(
        options_frame.options['MAXIMIZE_SLACKS'], 'MAXIMIZE_SLACKS')
    assert options_frame.params.get_parameter_value('MAXIMIZE_SLACKS') == 'yes'
    options_frame.options['DEA_FORM'].set(2)
    options_frame.radio_btn_change('DEA_FORM')
    assert options_frame.params.get_parameter_value('MAXIMIZE_SLACKS') == ''
    assert options_frame.params.get_parameter_value('DEA_FORM') == 'multi'
    assert str(options_frame.max_slack_box.cget('state')) == DISABLED
    options_frame.options['DEA_FORM'].set(1)
    options_frame.radio_btn_change('DEA_FORM')
    assert options_frame.params.get_parameter_value('MAXIMIZE_SLACKS') == 'yes'
    assert options_frame.params.get_parameter_value('DEA_FORM') == 'env'
    assert str(options_frame.max_slack_box.cget('state')) == NORMAL


def _set_categories(options_frame):
    options_frame.current_categories.extend(['I1', 'I2', 'I3', 'O1', 'O2'])
    options_frame.input_categories_frame.category_objects['I1'] = None
    options_frame.input_categories_frame.category_objects['O1'] = None


def test_change_categorical_box(options_frame):
    _set_categories(options_frame)
    options_frame.change_categorical_box()
    values = options_frame.categorical_box.cget('values')
    assert len(values) == 4
    assert 'I2' in values and 'I3' in values and 'O2' in values and '' in values


def test_on_categorical_box_change(options_frame):
    category = 'categorical'
    options_frame.combobox_text_var.set(category)
    assert options_frame.params.get_parameter_value(
        'CATEGORICAL_CATEGORY') == category
    options_frame.combobox_text_var.set('')
    assert options_frame.params.get_parameter_value(
        'CATEGORICAL_CATEGORY') == ''


def test_set_radio_btns_valid_values(options_frame):
    options_frame.params.update_parameter('RETURN_TO_SCALE', 'CRS')
    options_frame.params.update_parameter('ORIENTATION', 'input')
    options_frame.params.update_parameter('DEA_FORM', 'multi')
    options_frame.set_radio_btns()
    assert options_frame.warning_was_called is False
    assert options_frame.options['RETURN_TO_SCALE'].get() == 2
    assert options_frame.options['ORIENTATION'].get() == 1
    assert options_frame.options['DEA_FORM'].get() == 2


def test_set_radio_btns_both(options_frame):
    options_frame.params.update_parameter('RETURN_TO_SCALE', 'both')
    options_frame.params.update_parameter('ORIENTATION', 'both')
    options_frame.params.update_parameter('DEA_FORM', 'env')
    options_frame.set_radio_btns()
    assert options_frame.warning_was_called is False
    assert options_frame.options['RETURN_TO_SCALE'].get() == 3
    assert options_frame.options['ORIENTATION'].get() == 3
    assert options_frame.options['DEA_FORM'].get() == 1


def test_set_radio_btns_invalid_values(options_frame):
    options_frame.params.update_parameter('RETURN_TO_SCALE', 'haha')
    options_frame.params.update_parameter('ORIENTATION', 'both')
    options_frame.params.update_parameter('DEA_FORM', '')
    options_frame.set_radio_btns()
    assert options_frame.warning_was_called is True
    assert options_frame.count_warning == 2
    assert options_frame.options['RETURN_TO_SCALE'].get() == 1
    assert options_frame.options['ORIENTATION'].get() == 3
    assert options_frame.options['DEA_FORM'].get() == 1


def test_set_check_btns(options_frame):
    options_frame.params.update_parameter('MAXIMIZE_SLACKS', 'yes')
    options_frame.params.update_parameter('PEEL_THE_ONION', 'yes')
    options_frame.set_check_btns()
    assert options_frame.options['MAXIMIZE_SLACKS'].get() == 1
    assert options_frame.options['PEEL_THE_ONION'].get() == 1
    assert options_frame.options['USE_SUPER_EFFICIENCY'].get() == 0


def test_set_categorical_box(options_frame):
    _set_categories(options_frame)
    options_frame.change_categorical_box()
    options_frame.set_categorical_box('I2')
    assert options_frame.params.get_parameter_value(
        'CATEGORICAL_CATEGORY') == 'I2'
    assert options_frame.combobox_text_var.get() == 'I2'


def test_set_categorical_box_invalid_value(options_frame):
    _set_categories(options_frame)
    options_frame.change_categorical_box()
    options_frame.set_categorical_box('I1')
    assert options_frame.params.get_parameter_value(
        'CATEGORICAL_CATEGORY') == ''
    assert options_frame.combobox_text_var.get() == ''
    assert options_frame.combobox_warning_called is True


def test_set_multi_tol(options_frame):
    options_frame.params.update_parameter(
        'MULTIPLIER_MODEL_TOLERANCE', '0.001')
    options_frame.set_multi_tol()
    assert options_frame.multi_tol_strvar.get() == '0.001'
    options_frame.params.update_parameter(
        'MULTIPLIER_MODEL_TOLERANCE', '-0.001')
    options_frame.set_multi_tol()
    assert options_frame.multi_tol_strvar.get() == '0'
    assert options_frame.multi_tol_warning_called is True
    options_frame.multi_tol_warning_called = False
    options_frame.params.update_parameter('MULTIPLIER_MODEL_TOLERANCE', 'abc')
    options_frame.set_multi_tol()
    assert options_frame.multi_tol_strvar.get() == '0'
    assert options_frame.multi_tol_warning_called is True
    options_frame.multi_tol_warning_called = False
    options_frame.params.update_parameter(
        'MULTIPLIER_MODEL_TOLERANCE', '1e-10')
    options_frame.set_multi_tol()
    assert options_frame.multi_tol_strvar.get() == '1e-10'
    assert options_frame.multi_tol_warning_called is False
    options_frame.multi_tol_warning_called = False
    options_frame.params.update_parameter('MULTIPLIER_MODEL_TOLERANCE', '1E-2')
    options_frame.set_multi_tol()
    assert options_frame.multi_tol_strvar.get() == '1E-2'
    assert options_frame.multi_tol_warning_called is False


def test_on_multi_tol_change(options_frame):
    options_frame.multi_tol_strvar.set('0.001')
    assert options_frame.params.get_parameter_value(
        'MULTIPLIER_MODEL_TOLERANCE') == '0.001'
    options_frame.multi_tol_strvar.set('abc')
    assert options_frame.params.get_parameter_value(
        'MULTIPLIER_MODEL_TOLERANCE') == 'abc'


def test_on_check_box_click(options_frame):
    options_frame.options['PEEL_THE_ONION'].set(1)
    options_frame.on_check_box_click(
        options_frame.options['PEEL_THE_ONION'], 'PEEL_THE_ONION')
    assert options_frame.params.get_parameter_value('PEEL_THE_ONION') == 'yes'
    options_frame.options['PEEL_THE_ONION'].set(0)
    options_frame.on_check_box_click(
        options_frame.options['PEEL_THE_ONION'], 'PEEL_THE_ONION')
    assert options_frame.params.get_parameter_value('PEEL_THE_ONION') == ''


def test_set_params_values(options_frame):
    _set_categories(options_frame)
    options_frame.change_categorical_box()
    options_frame.params.update_parameter('RETURN_TO_SCALE', 'CRS')
    options_frame.params.update_parameter('ORIENTATION', 'both')
    options_frame.params.update_parameter('DEA_FORM', 'env')
    options_frame.params.update_parameter('PEEL_THE_ONION', 'yes')
    options_frame.params.update_parameter('MULTIPLIER_MODEL_TOLERANCE', '0.01')
    options_frame.params.update_parameter('CATEGORICAL_CATEGORY', 'I2')
    options_frame.set_params_values()
    assert options_frame.options['RETURN_TO_SCALE'].get() == 2
    assert options_frame.options['ORIENTATION'].get() == 3
    assert options_frame.options['DEA_FORM'].get() == 1
    assert options_frame.options['PEEL_THE_ONION'].get() == 1
    assert options_frame.options['MAXIMIZE_SLACKS'].get() == 0
    assert options_frame.options['USE_SUPER_EFFICIENCY'].get() == 0
    assert options_frame.multi_tol_strvar.get() == '0.01'
    assert options_frame.combobox_text_var.get() == 'I2'
