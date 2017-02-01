from tkinter import StringVar, Tk
from tkinter.ttk import Frame
import os
import pytest

from pyDEA.core.gui_modules.data_tab_frame_gui import DataTabFrame
from pyDEA.core.utils.dea_utils import TEXT_FOR_PANEL
from pyDEA.core.data_processing.parameters import Parameters


class CategoryFrameMock(object):

    def __init__(self):
        self.add_category_called = False
        self.remove_category_called = False
        self.category_objects = dict()

    def reset(self):
        self.add_category_called = False
        self.remove_category_called = False

    def add_category(self, category_name):
        self.add_category_called = True

    def remove_category(self, category_name):
        self.remove_category_called = True


class OptionsFrameMock(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.combobox_text_var = StringVar(master=parent)


class ParamsFrameMock(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.options_frame = OptionsFrameMock(parent)
        self.input_categories_frame = CategoryFrameMock()
        self.output_categories_frame = CategoryFrameMock()
        self.clear_all_called = False
        self.weight_frame_name = ''
        self.params = Parameters()

    def clear_all(self):
        self.clear_all_called = True

    def change_category_name(self, old_name, new_name):
        pass

    def change_categorical_box(self):
        pass

    def set_categorical_box(self, categorical_param):
        pass

    def change_weight_tab_name(self, new_name):
        self.weight_frame_name = new_name


class DataTabFrameParentMock(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.reset_called = False

    def reset_progress_bar(self):
        self.reset_called = True


class DataTabFrameMock(DataTabFrame):

    def __init__(self, parent, sheet_name='Sheet1'):
        super().__init__(DataTabFrameParentMock(parent),
                         ParamsFrameMock(parent),
                         ['', '', ''], StringVar(master=parent),
                         StringVar(master=parent))
        self.file_to_save = 'tests/test_file_save_data_frame_tab.xls'
        self.file_to_load = ''
        self.my_sheet_name = sheet_name

    def call_dialog(self, names):
        return self.my_sheet_name

    def _call_file_save_as_dialog(self):
        return self.file_to_save

    def _call_open_file_dialogue(self):
        return self.file_to_load


@pytest.fixture
def data_tab(request):
    parent = Tk()
    data_tab = DataTabFrameMock(parent)
    request.addfinalizer(parent.destroy)
    return data_tab


def test_get_data_file_name(data_tab):
    new_name = 'new super file name.txt'
    data_tab.panel.config(text=TEXT_FOR_PANEL + new_name)
    assert data_tab.get_data_file_name() == new_name


def test_remove_star_from_panel(data_tab):
    data_tab.panel.config(text=TEXT_FOR_PANEL + 'file name.txt*')
    data_tab.remove_star_from_panel()
    assert data_tab.panel.cget('text') == TEXT_FOR_PANEL + 'file name.txt'
    data_tab.panel.config(text=TEXT_FOR_PANEL + 'file name without star.txt')
    data_tab.remove_star_from_panel()
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + 'file name without star.txt'


def test_on_data_modify(data_tab):
    new_text = TEXT_FOR_PANEL + 'new file name.txt'
    data_tab.panel.config(text=new_text)
    data_tab.if_text_modified_str.set('notify')
    assert data_tab.panel.cget('text') == new_text + '*'
    data_tab.if_text_modified_str.set('notify')
    data_tab.if_text_modified_str.set('notify')
    data_tab.if_text_modified_str.set('notify')
    # make sure only one star is added even after multiple modifications of
    # data
    assert data_tab.panel.cget('text') == new_text + '*'


def _check_clear_all(data_tab):
    assert not data_tab.data
    assert data_tab.panel.cget('text') == TEXT_FOR_PANEL
    assert data_tab.sheet_name == ''
    assert data_tab.parent.reset_called is True
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '1 pages'
    assert data_tab.navigation_frame.current_page_str.get() == '1'
    assert data_tab.navigation_frame.goto_spin.cget('to') == 1
    assert data_tab.params_frame.clear_all_called is True


def test_clear_all(data_tab):
    data_tab.show_loaded_data('tests/categorical_test.xls')
    data_tab.clear_all()
    _check_clear_all(data_tab)


def test_save_data_as(data_tab):
    new_text = TEXT_FOR_PANEL + 'new file name.txt'
    data_tab.panel.config(text=new_text)
    data_tab.save_data_as()
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + data_tab.file_to_save
    assert os.path.isfile(data_tab.file_to_save)
    os.remove(data_tab.file_to_save)


def test_save_data(data_tab):
    data_tab.save_data_as()  # now file exists
    data_tab.sheet_name = 'Data'
    new_text = TEXT_FOR_PANEL + data_tab.file_to_save + '*'
    data_tab.panel.config(text=new_text)
    data_tab.save_data()
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + data_tab.file_to_save
    assert os.path.isfile(data_tab.file_to_save)
    # save already saved file again
    data_tab.save_data()
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + data_tab.file_to_save
    assert os.path.isfile(data_tab.file_to_save)
    # removed file and update panel text to '*'
    os.remove(data_tab.file_to_save)
    new_text = TEXT_FOR_PANEL + '*'
    data_tab.panel.config(text=new_text)
    data_tab.save_data()
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + data_tab.file_to_save
    assert os.path.isfile(data_tab.file_to_save)
    os.remove(data_tab.file_to_save)


def test_on_params_file_change(data_tab):
    data_tab.show_loaded_data('tests/categorical_test.xls')
    data_tab.data_from_params_file.set('')
    assert data_tab.panel.cget(
        'text') == TEXT_FOR_PANEL + 'tests/categorical_test.xls'
    data_tab.data_from_params_file.set('tests/DEA_example2_data.xls')
    assert data_tab.panel.cget('text') == TEXT_FOR_PANEL + \
        'tests/DEA_example2_data.xls'


def test_show_data(data_tab):
    categories = ['category 1', 'category2', 'cat3;']
    coefficients = [['DMU1', 0, 0.4, -10]]
    coefficients.append(['DMU2', 'a', '4', '10'])
    coefficients.append(['DMU3', 0.0, 5.98, '2'])
    dmu_name = 'some dmus'
    data_tab.show_data(categories, coefficients, dmu_name)
    assert data_tab.table.cells[0][0].get() == dmu_name
    print('data', data_tab.data)
    # print('data', data_tab.data)
    for count, category in enumerate(categories):
        assert data_tab.table.cells[0][count + 1].text_value.get() == category
    for row in range(len(coefficients)):
        for count, val in enumerate(coefficients[row]):
            assert data_tab.table.cells[
                row + 1][count].text_value.get() == str(val)
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '1 pages'
    assert data_tab.navigation_frame.current_page_str.get() == '1'
    assert data_tab.navigation_frame.goto_spin.cget('to') == 1


def test_show_data_multiple_pages(data_tab):
    data_tab.show_loaded_data('tests/Book1.xlsx')
    categories = ['I1', 'I2', 'I3', 'Out']
    assert len(data_tab.table.current_categories) == 4
    for category in categories:
        assert category in data_tab.table.current_categories
    assert data_tab.table.nb_cols < len(data_tab.data)
    for row in range(data_tab.table.nb_rows - 1):
        for col in range(len(categories) + 1):
            assert data_tab.table.cells[
                row + 1][col].text_value.get() == str(data_tab.data[row][col])


def _check_data_and_table(tab, categories, coefficients):
    assert len(tab.table.current_categories) == len(categories)
    for count, category in enumerate(categories):
        assert category in tab.table.current_categories
        assert tab.table.cells[0][count + 1].text_value.get() == category

    for row in range(len(coefficients)):
        for count, val in enumerate(coefficients[row]):
            assert tab.table.cells[row + 1][count].text_value.get() == str(val)
            assert tab.data[row][count] == val


def test_show_loaded_data(data_tab):
    file_name = 'tests/dataToTestDataLoad.xls'
    data_tab.file_to_load = file_name
    data_tab.load_file()
    categories = ['i1', 'i2', 'o1', 'o2']
    coefficients = [[1.0,   1.0,   2.0,   3.0,   4.0],
                    [2.0,   5.0,   6.0,   7.0,   8.0],
                    [3.0,   9.0,   10.0,  11.0,  12.0],
                    [4.0,   13.0,  14.0,  15.0,  16.0],
                    [5.0,   17.0,  18.0,  19.0,  20.0]]
    assert data_tab.params_frame.params.get_parameter_value(
        'DATA_FILE') == file_name
    _check_data_and_table(data_tab, categories, coefficients)


def test_show_loaded_data_second_sheet():
    parent = Tk()
    tab = DataTabFrameMock(parent, 'Sheet2')
    tab.show_loaded_data('tests/dataToTestDataLoad.xls')
    categories = ['inp1',  'inp2',  'out']
    coefficients = [['a',   10.0,  10.0,  10.0],
                    ['b',   20.0,  20.0,  20.0],
                    ['c',   30.0,  30.0,  30.0],
                    ['d',   40.0,  40.0,  40.0],
                    ['e',   50.0,  50.0,  50.0]
                    ]
    _check_data_and_table(tab, categories, coefficients)
    parent.destroy()


def test_show_loaded_data_one_page(data_tab):
    data_tab.show_loaded_data('tests/dataToTestDataLoadOneSheet.xls')
    categories = ['i1', 'i2', 'o1', 'o2']
    coefficients = [[1.0,   1.0,   2.0,   3.0,   4.0],
                    [2.0,   5.0,   6.0,   7.0,   8.0],
                    [3.0,   9.0,   10.0,  11.0,  12.0],
                    [4.0,   13.0,  14.0,  15.0,  16.0],
                    [5.0,   17.0,  18.0,  19.0,  20.0]]

    _check_data_and_table(data_tab, categories, coefficients)
