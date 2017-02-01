from tkinter import Tk
import pytest

from pyDEA.core.gui_modules.categories_checkbox_gui import CategoriesCheckBox
from pyDEA.core.data_processing.parameters import Parameters


categories = ['cat1', 'cat2', 'cat3']


@pytest.fixture
def box(request):
    parent = Tk()
    box = CategoriesCheckBox(parent, 'text', True,
                             Parameters(), 'INPUT_CATEGORIES')
    global categories
    for category in categories:
        box.add_category(category)
    request.addfinalizer(parent.destroy)
    return box


def _check_if_categories_in_cat_objs(box, categories):
    assert len(categories) == len(box.category_objects)
    for category in categories:
        assert category in box.category_objects.keys()


def _check_if_categories_in_params(box, categories, expected_nb_categories):
    input_categories = box.params.get_set_of_parameters('INPUT_CATEGORIES')
    assert len(input_categories) == expected_nb_categories
    for category in categories:
        assert category in input_categories


def _check_if_categories_in_options(box, categories):
    assert len(categories) == len(box.options)
    for category in categories:
        assert category in box.options.keys()


def _check_all(box, categories, expected_nb_categories):
    _check_if_categories_in_cat_objs(box, categories)
    _check_if_categories_in_params(box, categories, expected_nb_categories)
    _check_if_categories_in_options(box, categories)


def test_add_category(box):
    global categories
    _check_all(box, categories, 3)

    box.add_category('cat2')  # already added, should be appear twice
    _check_all(box, categories, 3)
    box.params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'cat4')
    box.add_category('cat4')
    assert box.options['cat4'][0].get() == 1

    box.params.update_parameter('WEAKLY_DISPOSAL_CATEGORIES', 'cat5')
    box.params.update_parameter('NON_DISCRETIONARY_CATEGORIES', 'cat5')
    box.add_category('cat5')
    assert box.options['cat5'][0].get() == 1
    assert box.options['cat5'][1].get() == 1


def test_change_category_name(box):
    box.change_category_name('cat2', 'new cat')
    new_categories = ['cat1', 'new cat', 'cat3']
    _check_all(box, new_categories, 3)
    box.change_category_name('fake', 'haha')
    _check_all(box, new_categories, 3)


def test_on_select_box(box):
    box.options['cat1'][0].set(1)  # imitating checkbox select
    box.on_select_box(box.category_objects['cat1'][0], 0)
    nd_cat = box.params.get_parameter_value('NON_DISCRETIONARY_CATEGORIES')
    assert nd_cat == 'cat1'
    box.options['cat1'][0].set(0)
    box.on_select_box(box.category_objects['cat1'][0], 0)
    nd_cat = box.params.get_parameter_value('NON_DISCRETIONARY_CATEGORIES')
    assert nd_cat == ''
    box.options['cat2'][1].set(1)
    box.on_select_box(box.category_objects['cat2'][0], 1)
    wd_cat = box.params.get_parameter_value('WEAKLY_DISPOSAL_CATEGORIES')
    assert wd_cat == 'cat2'
    box.options['cat2'][1].set(0)
    box.on_select_box(box.category_objects['cat2'][0], 1)
    wd_cat = box.params.get_parameter_value('WEAKLY_DISPOSAL_CATEGORIES')
    assert wd_cat == ''


def test_remove_category(box):
    box.remove_category('cat2')
    _check_all(box, ['cat1', 'cat3'], 2)
    assert 'cat2' not in box.category_objects.keys()
    assert 'cat2' not in box.options.keys()


def test_remove_all_categories(box):
    box.remove_all_categories()
    assert len(box.options) == 0
    assert len(box.category_objects) == 0
    assert box.params.get_parameter_value('INPUT_CATEGORIES') == ''
