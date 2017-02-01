from tkinter import IntVar
from tkinter.ttk import Frame
import pytest

from pyDEA.core.gui_modules.table_modifier_gui import TableModifierFrame


class TableFrameMock(Frame):

    def __init__(self):
        super().__init__()
        self.nb_rows = 20
        self.nb_cols = 5
        self.row_checkboxes = []
        self.cells = []
        for row in range(self.nb_rows):
            box = IntVar(value=0)
            self.row_checkboxes.append((None, box))

        self.col_checkboxes = []
        for row in range(self.nb_cols - 1):
            box = IntVar(value=0)
            self.col_checkboxes.append((None, box))

    def add_row(self):
        self.nb_rows += 1

    def add_column(self):
        self.nb_cols += 1

    def remove_row(self, row_index):
        self.nb_rows -= 1
        self.row_checkboxes.pop(row_index)

    def remove_column(self, col_index):
        self.nb_cols -= 1
        self.col_checkboxes.pop(col_index - 1)


def clear_all_fnc():
    pass


def set_navigation(nb_data_pages, reset_curr_page=True):
    pass


@pytest.fixture
def table_modifier(request):
    table_modifier = TableModifierFrame(
        None, TableFrameMock(), clear_all_fnc, set_navigation)
    request.addfinalizer(table_modifier.destroy)
    return table_modifier


def test_add_rows(table_modifier):
    nb_rows = table_modifier.table.nb_rows
    val = 3
    table_modifier.row_str_var.set(val)
    table_modifier.add_rows()
    assert table_modifier.table.nb_rows == nb_rows + val


def test_add_rows_invalid_val(table_modifier):
    nb_rows = table_modifier.table.nb_rows
    table_modifier.row_str_var.set('val')
    table_modifier.add_rows()
    assert table_modifier.table.nb_rows == nb_rows + 1
    table_modifier.row_str_var.set(-10)
    table_modifier.add_rows()
    assert table_modifier.table.nb_rows == nb_rows + 2


def test_add_columns(table_modifier):
    nb_cols = table_modifier.table.nb_cols
    val = 2
    table_modifier.col_str_var.set(val)
    table_modifier.add_columns()
    assert table_modifier.table.nb_cols == nb_cols + val


def test_add_columns_invalid_val(table_modifier):
    nb_cols = table_modifier.table.nb_cols
    table_modifier.col_str_var.set("text isn't allowed")
    table_modifier.add_columns()
    assert table_modifier.table.nb_cols == nb_cols + 1
    table_modifier.col_str_var.set(-7)
    table_modifier.add_columns()
    assert table_modifier.table.nb_cols == nb_cols + 2


def test_remove_rows(table_modifier):
    nb_rows = table_modifier.table.nb_rows
    table_modifier.table.row_checkboxes[1][1].set(1)
    table_modifier.table.row_checkboxes[18][1].set(1)
    table_modifier.remove_rows()
    assert table_modifier.table.nb_rows == nb_rows - 2


def test_remove_rows_non_checked(table_modifier):
    nb_rows = table_modifier.table.nb_rows
    table_modifier.remove_rows()
    assert table_modifier.table.nb_rows == nb_rows


def test_remove_rows_one_left(table_modifier):
    table_modifier.table.nb_rows = 1
    table_modifier.remove_rows()
    assert table_modifier.table.nb_rows == 1


def test_remove_all_rows(table_modifier):
    for box, var in table_modifier.table.row_checkboxes:
        var.set(1)
    table_modifier.remove_rows()
    assert table_modifier.table.nb_rows == 1
    assert len(table_modifier.table.row_checkboxes) == 1


def test_remove_columns(table_modifier):
    nb_cols = table_modifier.table.nb_cols
    table_modifier.table.col_checkboxes[0][1].set(1)
    table_modifier.table.col_checkboxes[3][1].set(1)
    table_modifier.remove_columns()
    assert table_modifier.table.nb_cols == nb_cols - 2


def test_remove_col_in_the_middle(table_modifier):
    nb_cols = table_modifier.table.nb_cols
    table_modifier.table.col_checkboxes[2][1].set(1)
    table_modifier.remove_columns()
    assert table_modifier.table.nb_cols == nb_cols - 1


def test_remove_columns_non_checked(table_modifier):
    nb_cols = table_modifier.table.nb_cols
    table_modifier.remove_columns()
    assert table_modifier.table.nb_cols == nb_cols


def test_remove_all_columns(table_modifier):
    for box, var in table_modifier.table.col_checkboxes:
        var.set(1)
    table_modifier.remove_columns()
    assert table_modifier.table.nb_cols == 1
    assert len(table_modifier.table.col_checkboxes) == 0
