from tkinter import Tk, StringVar, END
import os
import pytest

from pyDEA.core.gui_modules.params_frame_gui import ParamsFrame, TEXT_FOR_PARAMS_LBL
from pyDEA.core.utils.dea_utils import ObserverStringVar
from pyDEA.core.data_processing.parameters import CATEGORICAL_AND_DATA_FIELDS


class ParamsFrameMock(ParamsFrame):

    def __init__(self, parent, current_categories, data_from_params_file,
                 str_var_for_input_output_boxes,
                 weights_status_str, *args, **kw):
        super().__init__(parent, current_categories, data_from_params_file,
                         str_var_for_input_output_boxes, weights_status_str,
                         *args, **kw)
        self.file_name_to_load = ''
        self.file_name_to_save = ''
        self.warning_set = False

    def _get_filename_for_load(self):
        return self.file_name_to_load

    def _show_warning(self, norm_data_path):
        self.warning_set = True

    def _get_file_name_to_save(self):
        return self.file_name_to_save


@pytest.fixture
def params_frame(request):
    parent = Tk()
    current_categories = []
    data_from_params_file = StringVar(master=parent)
    weights_status_str = StringVar(master=parent)
    str_var_for_input_output_boxes = ObserverStringVar(master=parent)
    params_frame = ParamsFrameMock(parent, current_categories,
                                   data_from_params_file,
                                   str_var_for_input_output_boxes,
                                   weights_status_str)
    request.addfinalizer(parent.destroy)
    return params_frame


def _check_params(params, other_params_dict=None):
    params_to_check = {'DATA_FILE': 'tests/DEA_example2_data.xls',
                       'INPUT_CATEGORIES': 'I1; I2; I3',
                       'OUTPUT_CATEGORIES': 'O1; O2',
                       'DEA_FORM': 'env',
                       'RETURN_TO_SCALE': 'VRS',
                       'ORIENTATION': 'input',
                       'NON_DISCRETIONARY_CATEGORIES': '',
                       'WEAKLY_DISPOSAL_CATEGORIES': '',
                       'USE_SUPER_EFFICIENCY': '',
                       'ABS_WEIGHT_RESTRICTIONS': 'I1 <= 0.6; I1 >= 0.01',
                       'VIRTUAL_WEIGHT_RESTRICTIONS': 'I1 <= 0.6; I1 >= 0.01',
                       'PRICE_RATIO_RESTRICTIONS':
                       'I1/I2 <= 0.5; I1/I2 >= 0.02',
                       'MAXIMIZE_SLACKS': '',
                       'MULTIPLIER_MODEL_TOLERANCE': '0',
                       'CATEGORICAL_CATEGORY': '',
                       'PEEL_THE_ONION': ''
                       }
    if other_params_dict:
        params_to_check.update(other_params_dict)
    for key, value in params_to_check.items():
        assert params.get_parameter_value(key) == value


def _load_new_format_params(params_frame, categories=[]):
    params_frame.file_name_to_load = 'tests/params_new_format.txt'
    if not categories:
        categories = ['I1', 'I2', 'I3', 'O1', 'O2']
    params_frame.current_categories.extend(categories)  # we load
    # categories only if they are valid, i.e. they are present in
    # current_categories
    params_frame.load_file()


def test_change_weight_tab_name(params_frame):
    new_name = 'Haha'
    params_frame.change_weight_tab_name(new_name)
    assert params_frame.tab(1, option='text') == new_name


def test_load_file(params_frame):
    _load_new_format_params(params_frame)
    _check_params(params_frame.params)


def test_load_file_without_data(params_frame):
    params_frame.load_without_data.set(1)
    _load_new_format_params(params_frame)
    _check_params(params_frame.params, {'DATA_FILE': '',
                                        'INPUT_CATEGORIES': '',
                                        'OUTPUT_CATEGORIES': '',
                                        'ABS_WEIGHT_RESTRICTIONS': '',
                                        'VIRTUAL_WEIGHT_RESTRICTIONS': '',
                                        'PRICE_RATIO_RESTRICTIONS': ''})


def test_load_file_without_data_with_prev_values(params_frame):
    _load_new_format_params(params_frame)
    params_frame.load_without_data.set(1)
    params_frame.file_name_to_load = 'tests/params_for_linux.txt'
    params_frame.load_file()
    _check_params(params_frame.params, {'RETURN_TO_SCALE': 'CRS',
                                        'PEEL_THE_ONION': 'yes',
                                        'ORIENTATION': 'output'})


def test_load_file_invalid_data_file(params_frame):
    params_frame.file_name_to_load = 'tests/params_invalid.txt'
    params_frame.current_categories.extend(['I1', 'I2', 'I3', 'O1', 'O2'])
    params_frame.load_file()
    _check_params(params_frame.params, {'DATA_FILE': '',
                                        'INPUT_CATEGORIES': '',
                                        'OUTPUT_CATEGORIES': '',
                                        'ABS_WEIGHT_RESTRICTIONS': '',
                                        'VIRTUAL_WEIGHT_RESTRICTIONS': '',
                                        'PRICE_RATIO_RESTRICTIONS': '',
                                        'RETURN_TO_SCALE': 'CRS',
                                        'DEA_FORM': 'multi'})
    assert params_frame.warning_set is True


def test_add_categories(params_frame):
    _load_new_format_params(params_frame, categories=['I1', 'I2', 'O1', 'O2'])
    assert 'I1' in params_frame.str_var_for_input_output_boxes.input_categories
    assert 'I2' in params_frame.str_var_for_input_output_boxes.input_categories
    assert len(params_frame.str_var_for_input_output_boxes.input_categories) == 2
    input_categories = params_frame.params.get_set_of_parameters(
        'INPUT_CATEGORIES')
    assert len(input_categories) == 2
    assert 'I1' in input_categories
    assert 'I2' in input_categories


def test_clear_all(params_frame):
    _load_new_format_params(params_frame, categories=['I1', 'I2', 'O1', 'O2'])
    params_frame.clear_all()
    for param_name in CATEGORICAL_AND_DATA_FIELDS:
        assert params_frame.params.get_parameter_value(param_name) == ''
    assert params_frame.options_frame.combobox_text_var.get() == ''
    assert params_frame.params_from_file_lbl.cget('text') == ''
    assert len(params_frame.str_var_for_input_output_boxes.input_categories) == 0
    assert len(params_frame.str_var_for_input_output_boxes.output_categories) == 0
    assert len(params_frame.input_categories_frame.category_objects) == 0
    assert params_frame.input_categories_frame.nb_entries == 0
    assert len(params_frame.output_categories_frame.category_objects) == 0
    assert params_frame.output_categories_frame.nb_entries == 0
    assert params_frame.weight_tab.abs_weights.text.get(1.0, END) == '\n'
    assert params_frame.weight_tab.virtual_weights.text.get(1.0, END) == '\n'
    assert params_frame.weight_tab.price_ratio_weights.text.get(
        1.0, END) == '\n'


def _check_set_of_params(params, param_name, values):
    values_from_params = params.get_set_of_parameters(param_name)
    assert len(values_from_params) == len(values)
    for val in values:
        assert val in values_from_params


def test_change_category_name(params_frame):
    _load_new_format_params(params_frame)
    new_name = 'new name with spaces'
    params_frame.current_categories[2] = new_name
    params_frame.change_category_name('I1', new_name)
    _check_set_of_params(params_frame.params, 'INPUT_CATEGORIES', [
                         'I2', 'I3', new_name])
    weight1 = '{0} <= 0.6'.format(new_name)
    weight2 = '{0} >= 0.01'.format(new_name)
    _check_set_of_params(params_frame.params, 'ABS_WEIGHT_RESTRICTIONS',
                         [weight1, weight2])
    _check_set_of_params(params_frame.params, 'VIRTUAL_WEIGHT_RESTRICTIONS',
                         [weight1, weight2])
    weight3 = '{0}/I2 <= 0.5'.format(new_name)
    weight4 = '{0}/I2 >= 0.02'.format(new_name)
    _check_set_of_params(params_frame.params, 'PRICE_RATIO_RESTRICTIONS',
                         [weight3, weight4])
    assert params_frame.options_frame.combobox_text_var.get() == ''
    assert ('I1' in params_frame.weight_tab.abs_weights.text.get(1.0, END)) is False
    assert weight1 in params_frame.weight_tab.abs_weights.text.get(1.0, END)
    assert weight2 in params_frame.weight_tab.abs_weights.text.get(1.0, END)
    assert ('I1' in params_frame.weight_tab.virtual_weights.text.get(
        1.0, END)) is False
    assert weight1 in params_frame.weight_tab.virtual_weights.text.get(
        1.0, END)
    assert weight2 in params_frame.weight_tab.virtual_weights.text.get(
        1.0, END)
    assert ('I1' in params_frame.weight_tab.price_ratio_weights.text.get(
        1.0, END)) is False
    assert weight3 in params_frame.weight_tab.price_ratio_weights.text.get(
        1.0, END)
    assert weight4 in params_frame.weight_tab.price_ratio_weights.text.get(
        1.0, END)


def test_change_category_name_categorical_var(params_frame):
    params_frame.file_name_to_load = 'tests/params_categorical.txt'
    params_frame.current_categories.extend(['I1', 'I2', 'I3', 'O1', 'O2'])
    params_frame.load_file()
    assert params_frame.options_frame.combobox_text_var.get() == 'I3'
    new_name = 'I3 new'
    params_frame.current_categories[2] = new_name
    params_frame.change_category_name('I3', new_name)
    assert params_frame.options_frame.combobox_text_var.get() == new_name


def test_on_save_params(params_frame):
    _load_new_format_params(params_frame)
    params_frame.params.update_parameter('DEA_FORM', 'multi')
    file_name = '{0}tests/params_on_save.txt'.format(TEXT_FOR_PARAMS_LBL)
    params_frame.params_from_file_lbl.config(text=file_name)
    params_frame.on_save_params()
    params_frame.file_name_to_load = file_name[len(TEXT_FOR_PARAMS_LBL):]
    params_frame.load_file()
    _check_params(params_frame.params, {'DEA_FORM': 'multi'})
    os.remove(params_frame.file_name_to_load)


def test_on_save_params_another_name(params_frame):
    _load_new_format_params(params_frame)
    params_frame.params.update_parameter('DEA_FORM', 'multi')
    file_name = 'tests/params_on_save2.txt'
    params_frame.params_from_file_lbl.config(text=file_name)
    params_frame.on_save_params()
    params_frame.file_name_to_load = file_name
    params_frame.load_file()
    _check_params(params_frame.params, {'DEA_FORM': 'multi'})
    os.remove(file_name)


def test_on_save_params_empty_name(params_frame):
    params_frame.file_name_to_save = 'tests/params_on_save4.txt'
    params_frame.on_save_params()
    assert os.path.isfile(params_frame.file_name_to_save)
    os.remove(params_frame.file_name_to_save)


def test_on_save_params_as(params_frame):
    _load_new_format_params(params_frame)
    params_frame.params.update_parameter('RETURN_TO_SCALE', 'CRS')
    params_frame.file_name_to_save = 'tests/params_on_save3.txt'
    params_frame.on_save_params_as()
    params_frame.file_name_to_load = params_frame.file_name_to_save
    params_frame.load_file()
    _check_params(params_frame.params, {'RETURN_TO_SCALE': 'CRS'})
    os.remove(params_frame.file_name_to_save)
