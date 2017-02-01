from tkinter import StringVar, Tk
from tkinter import IntVar, DISABLED, NORMAL
from tkinter.ttk import Frame
import pytest

from pyDEA.core.gui_modules.table_gui import ObserverCheckbutton
from pyDEA.core.gui_modules.table_gui import FollowingObserverCheckbutton
from pyDEA.core.gui_modules.table_gui import DefaultCategoriesAndDMUModifier
from pyDEA.core.gui_modules.table_gui import SelfValidatingEntry
from pyDEA.core.utils.dea_utils import INPUT_OBSERVER, OUTPUT_OBSERVER

from tests.test_gui_data_tab_frame import CategoryFrameMock


def change_category_name(old_name, new_name):
    pass


@pytest.fixture
def all_boxes(request):
    parent = Tk()
    parent_for_boxes = Frame(parent)
    parent_for_boxes.grid(row=0, column=2)
    var = IntVar()
    opposite_var = IntVar()
    category_frame = CategoryFrameMock()
    opposite_category_frame = CategoryFrameMock()
    categories = []
    cells = []
    data = []
    observer = DefaultCategoriesAndDMUModifier(cells, categories)
    for i in range(4):
        cells.append([])
        for j in range(3):
            entry = SelfValidatingEntry(parent, data, cells)
            cells[i].append(entry)
            if j == 1 or j == 2:
                entry.observers.append(observer)
            entry.grid(row=i + 2, column=j + 1)

    combobox_text_var = StringVar()
    box = ObserverCheckbutton(parent_for_boxes, var, opposite_var,
                              category_frame, opposite_category_frame,
                              categories, cells, INPUT_OBSERVER,
                              change_category_name, data,
                              combobox_text_var)

    follow_box = FollowingObserverCheckbutton(parent_for_boxes, opposite_var,
                                              var, opposite_category_frame,
                                              category_frame,
                                              categories, cells,
                                              OUTPUT_OBSERVER,
                                              change_category_name, data,
                                              combobox_text_var, box)

    parent_for_boxes2 = Frame(parent)
    parent_for_boxes2.grid(row=0, column=3)
    var2 = IntVar()
    opposite_var2 = IntVar()
    box2 = ObserverCheckbutton(parent_for_boxes2, var2, opposite_var2,
                               category_frame, opposite_category_frame,
                               categories, cells, INPUT_OBSERVER,
                               change_category_name, data,
                               combobox_text_var)

    follow_box2 = FollowingObserverCheckbutton(parent_for_boxes2, opposite_var2,
                                               var2, opposite_category_frame,
                                               category_frame,
                                               categories, cells,
                                               OUTPUT_OBSERVER,
                                               change_category_name, data,
                                               combobox_text_var, box2)

    for i in range(4):
        cells[i][1].observers.append(box)
        cells[i][1].observers.append(follow_box)
        cells[i][2].observers.append(box2)
        cells[i][2].observers.append(follow_box2)

    request.addfinalizer(parent.destroy)
    return cells, box, follow_box, box2, follow_box2


def test_process(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[0][1].text_value.set('new category')
    box.combobox_text_var.set('new category')
    box.var.set(1)
    box._process()
    assert box.var.get() == 1
    assert follow_box.var.get() == 0
    assert box.category_frame.add_category_called is True
    assert follow_box.category_frame.remove_category_called is True
    assert box.combobox_text_var.get() == ''
    box.category_frame.reset()
    box.opposite_category_frame.reset()
    box.var.set(0)
    box._process()
    assert box.var.get() == 0
    assert follow_box.var.get() == 0
    assert box.category_frame.remove_category_called is True

    # check follow_box
    box.var.set(1)
    box._process()
    box.category_frame.reset()
    box.opposite_category_frame.reset()
    follow_box.var.set(1)
    follow_box._process()
    assert box.var.get() == 0
    assert follow_box.var.get() == 1
    assert follow_box.category_frame.add_category_called is True
    assert box.category_frame.remove_category_called is True
    assert box.combobox_text_var.get() == ''


def test_manual_text_entry(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes

    assert box.var.get() == 0
    assert box.opposite_var.get() == 0
    assert str(box.cget('state')) == NORMAL

    cells[1][1].text_value.set(10)
    assert cells[0][1].text_value.get() == 'Category0'
    assert box.cells[0][1].text_value.get() == 'Category0'
    assert 'Category0' in box.current_categories
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    cells[1][1].text_value.set(-5)
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    cells[1][1].text_value.set(5)
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    cells[1][1].text_value.set('some text')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    cells[1][1].text_value.set(5)
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL

    # testing various category names
    cells[0][1].text_value.set('New category name')
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    assert 'New category name' in box.current_categories
    assert len(box.current_categories) == 1
    cells[0][1].text_value.set('Invalid name;')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    assert box.current_categories[0] == ''
    cells[0][1].text_value.set('New category name')
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    assert 'New category name' in box.current_categories
    assert len(box.current_categories) == 1
    cells[0][1].text_value.set('     ')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    assert box.current_categories[0] == ''
    cells[0][1].text_value.set('New category name')
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    assert 'New category name' in box.current_categories
    assert len(box.current_categories) == 1
    cells[0][1].text_value.set('1.2')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    assert box.current_categories[0] == ''
    cells[0][1].text_value.set('New category name')
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    assert 'New category name' in box.current_categories
    assert len(box.current_categories) == 1
    box.opposite_var.set(1) # select as outout category
    box._process()
    box.category_frame.remove_category_called = False
    box.opposite_category_frame.remove_category_called = False
    cells[0][1].text_value.set('')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    assert box.current_categories[0] == ''
    assert box.opposite_category_frame.remove_category_called is True


def test_manual_entry_with_checked_boxes(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[1][1].text_value.set(10)
    box.var.set(1)
    box._process()
    assert str(box.cget('state')) == NORMAL
    assert str(follow_box.cget('state')) == NORMAL
    box.category_frame.reset()
    box.opposite_category_frame.reset()
    cells[1][1].text_value.set('invalid value')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    assert box.category_frame.remove_category_called is True


def test_manual_entry_when_no_data_in_first_row(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[3][2].text_value.set(10)
    assert str(box2.cget('state')) == DISABLED
    assert str(follow_box2.cget('state')) == DISABLED


def test_manual_entry_valid_coeff_second_column(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[1][2].text_value.set(4)
    cells[2][2].text_value.set(4)
    assert cells[0][2].text_value.get() == 'Category1'
    box2.select()
    box2._process()
    assert str(box2.cget('state')) == NORMAL
    assert str(follow_box2.cget('state')) == NORMAL
    cells[2][1].text_value.set('')
    assert str(box.cget('state')) == DISABLED
    assert str(follow_box.cget('state')) == DISABLED
    cells[2][2].text_value.set(-17)
    assert str(box2.cget('state')) == DISABLED
    assert str(follow_box2.cget('state')) == DISABLED
    assert box2.category_frame.remove_category_called is True
    cells[2][2].text_value.set(0)
    assert str(box2.cget('state')) == NORMAL
    assert str(follow_box2.cget('state')) == NORMAL
    assert box2.category_frame.add_category_called is True
    box2.category_frame.reset()
    box2.opposite_category_frame.reset()
    cells[2][2].text_value.set('')
    assert str(box2.cget('state')) == DISABLED
    assert str(follow_box2.cget('state')) == DISABLED
    assert box2.category_frame.remove_category_called is True
    follow_box2.select()
    follow_box2._process()
    box2.category_frame.reset()
    box2.opposite_category_frame.reset()
    cells[2][2].text_value.set('0.7')
    assert str(box2.cget('state')) == NORMAL
    assert str(follow_box2.cget('state')) == NORMAL
    assert follow_box2.category_frame.add_category_called is True


def test_change_category_name_no_data_entered(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[0][2].text_value.set('cat')
    assert str(box2.cget('state')) == DISABLED
    assert str(follow_box2.cget('state')) == DISABLED
    cells[1][2].text_value.set('2')
    assert str(box2.cget('state')) == NORMAL
    assert str(follow_box2.cget('state')) == NORMAL

   
def test_unselect_combobox(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[0][1].text_value.set('new category')
    box.combobox_text_var.set('new category')
    cells[2][1].text_value.set('')
    assert box.combobox_text_var.get() == ''


def test_unselect_combobox_check_second(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[0][1].text_value.set('new category')
    cells[0][2].text_value.set('category')
    box2.combobox_text_var.set('category')
    cells[2][1].text_value.set('')
    assert box.combobox_text_var.get() == 'category'
    assert box2.combobox_text_var.get() == 'category'


def test_emty_value(all_boxes):
    cells, box, follow_box, box2, follow_box2 = all_boxes
    cells[1][2].text_value.set('')
    cells[2][2].text_value.set('')
    print('data', box.data)
    assert str(box2.cget('state')) == DISABLED
    assert str(follow_box2.cget('state')) == DISABLED
