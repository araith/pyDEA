from tkinter import StringVar, Tk
import pytest

from pyDEA.core.gui_modules.table_gui import TableFrameWithInputOutputBox
from pyDEA.core.utils.dea_utils import INPUT_OBSERVER, OUTPUT_OBSERVER, ObserverStringVar

from tests.test_gui_data_tab_frame import ParamsFrameMock
from tests.test_gui_data_tab_frame import data_tab


@pytest.fixture
def table(request):
    parent = Tk()
    current_categories = []
    data = []
    table = TableFrameWithInputOutputBox(parent, ParamsFrameMock(parent),
                                         StringVar(), current_categories,
                                         ObserverStringVar(),
                                         StringVar(), data, nb_rows=20,
                                         nb_cols=5)
    request.addfinalizer(parent.destroy)
    return table


def test_table_creation(table):
    assert len(table.row_checkboxes) == table.nb_rows
    assert len(table.col_checkboxes) == table.nb_cols - 1
    assert len(table.frames) == table.nb_cols - 1


def select_box(col, table, box_type):
    for child in table.frames[col].winfo_children():
        try:
            if child.observer_type == box_type:
                child.select()
                child._proccess()
        except AttributeError:
            pass


def get_observer_var_value(col, table, box_type):
    for child in table.frames[col].winfo_children():
        try:
            if child.observer_type == box_type:
                return child.var.get()
        except AttributeError:
            pass
    return -1


def fill_first_row(table):
    for col in range(len(table.cells[1]) - 1):
        table.cells[1][col + 1].text_value.set('1')


def test_deselect_all_boxes(table):
    # by default there are 5 columns: 4 of them for categories
    # fill with data
    fill_first_row(table)
    # select some boxes
    select_box(0, table, INPUT_OBSERVER)
    select_box(1, table, OUTPUT_OBSERVER)
    table.deselect_all_boxes()
    assert get_observer_var_value(0, table, INPUT_OBSERVER) == 0
    assert get_observer_var_value(1, table, OUTPUT_OBSERVER) == 0


def test_on_load_categories(table):
    table.cells[0][1].text_value.set('inp1')
    table.cells[0][2].text_value.set('inp2')
    table.cells[0][3].text_value.set('out1')
    table.cells[0][4].text_value.set('out2')
    fill_first_row(table)
    table.str_var_for_input_output_boxes.input_categories.extend(
        ['inp1', 'inp2'])
    table.str_var_for_input_output_boxes.output_categories.extend(
        ['out1', 'out2'])
    table.str_var_for_input_output_boxes.set('notify')
    assert get_observer_var_value(0, table, INPUT_OBSERVER) == 1
    assert get_observer_var_value(0, table, OUTPUT_OBSERVER) == 0
    assert get_observer_var_value(1, table, INPUT_OBSERVER) == 1
    assert get_observer_var_value(1, table, OUTPUT_OBSERVER) == 0
    assert get_observer_var_value(2, table, OUTPUT_OBSERVER) == 1
    assert get_observer_var_value(2, table, INPUT_OBSERVER) == 0
    assert get_observer_var_value(3, table, OUTPUT_OBSERVER) == 1
    assert get_observer_var_value(3, table, INPUT_OBSERVER) == 0


def check_nb_cols(table, expected_nb_cols):
    assert table.nb_cols == expected_nb_cols
    assert len(table.col_checkboxes) == expected_nb_cols - 1
    assert len(table.frames) == expected_nb_cols - 1
    for i in range(table.nb_rows):
        assert len(table.cells[i]) == expected_nb_cols


def test_add_column(table):
    expected_nb_cols = table.nb_cols + 1
    table.add_column()
    check_nb_cols(table, expected_nb_cols)


def check_nb_rows(table, expected_nb_rows):
    assert table.nb_rows == expected_nb_rows
    assert len(table.row_checkboxes) == expected_nb_rows
    assert len(table.cells) == expected_nb_rows


def test_add_row(table):
    expected_nb_rows = table.nb_rows + 1
    table.add_row()
    check_nb_rows(table, expected_nb_rows)


def test_add_row_multiple_pages(data_tab):
    data_tab.show_loaded_data('tests/dataTestRemoveRow.xls')
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '2 pages'
    nb_rows = data_tab.table.nb_rows
    data_tab.table_modifier_frame.add_rows()
    check_nb_rows(data_tab.table, nb_rows + 1)
    assert len(data_tab.data) == 25
    assert data_tab.table.cells[20][0].text_value.get() == '20.0'
    assert data_tab.table.cells[20][1].text_value.get() == '200.0'
    assert data_tab.table.cells[20][2].text_value.get() == '100.0'
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '2 pages'
    data_tab.table_modifier_frame.row_str_var.set(5)
    data_tab.table_modifier_frame.add_rows()
    check_nb_rows(data_tab.table, nb_rows + 6)
    assert len(data_tab.data) == 25
    assert data_tab.table.cells[25][0].text_value.get() == '25.0'
    assert data_tab.table.cells[25][1].text_value.get() == '250.0'
    assert data_tab.table.cells[25][2].text_value.get() == '125.0'
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '1 pages'


def test_remove_row_multiple_pages_change_page_number(data_tab):
    data_tab.show_loaded_data('tests/dataTestRemoveRow.xls')
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '2 pages'
    nb_rows = data_tab.table.nb_rows
    data_tab.navigation_frame.show_next_page()
    for j in range(10):
        data_tab.table.row_checkboxes[10 + j][1].set(1)

    data_tab.table_modifier_frame.remove_rows()
    check_nb_rows(data_tab.table, nb_rows)
    assert len(data_tab.data) == 25
    print('data_tab.data', data_tab.data)
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '2 pages'
    assert data_tab.table.cells[1][0].text_value.get() == '20.0'
    assert data_tab.table.cells[1][1].text_value.get() == '200.0'
    assert data_tab.table.cells[1][2].text_value.get() == '100.0'


def test_remove_column_empty_data(table):
    expected_nb_cols = table.nb_cols - 1
    select_box(0, table, INPUT_OBSERVER)
    table.remove_column(1)
    check_nb_cols(table, expected_nb_cols)
    assert get_observer_var_value(0, table, INPUT_OBSERVER) == 0


def fill_data_one_page(table):
    assert table.nb_cols == 5
    for i in range(5):
        for j in range(table.nb_cols - 1):
            table.cells[i + 1][j + 1].text_value.set(j)
    assert len(table.data) == 5
    assert len(table.data[0]) == 5
    print('--------------------------------------------zjnvkjsdnvskj')
    print(table.data)


def test_remove_column_with_data(table):
    expected_nb_cols = table.nb_cols - 1
    fill_data_one_page(table)

    table.remove_column(2)
    check_nb_cols(table, expected_nb_cols)
    assert len(table.data) == 5
    for j in range(5):
        assert len(table.data[j]) == 4
    assert table.data[0][1] == '0'
    assert table.cells[1][1].data_column == 1
    assert table.data[0][2] == '2'
    assert table.cells[1][2].data_column == 2
    assert table.data[0][3] == '3'
    assert table.cells[1][3].data_column == 3


def check_data_cols_rows(table):
    for row in range(table.nb_rows):
        for col in range(table.nb_cols):
            assert table.cells[row][col].data_row == -1
            assert table.cells[row][col].data_column == -1


def test_remove_all_columns(table):
    nb_cols = table.nb_cols
    for i in range(nb_cols):
        table.remove_column(1)
    check_nb_cols(table, 1)
    check_data_cols_rows(table)
    # check that the first column cannot be deleted
    table.remove_column(0)
    table.remove_column(0)
    check_nb_cols(table, 1)


def test_remove_all_columns_with_data(table):
    fill_data_one_page(table)
    nb_cols = table.nb_cols
    for i in range(nb_cols):
        table.remove_column(1)
    check_nb_cols(table, 1)
    assert len(table.data) == 5
    for i in range(5):
        assert len(table.data[i]) == 1


def test_remove_column_in_the_middle(table):
    fill_data_one_page(table)
    nb_cols = table.nb_cols
    table.remove_column(3)
    check_nb_cols(table, nb_cols - 1)
    assert len(table.data) == 5
    for j in range(5):
        assert len(table.data[j]) == 4
    assert table.data[0][1] == '0'
    assert table.cells[1][1].data_column == 1
    assert table.data[0][2] == '1'
    assert table.cells[1][2].data_column == 2
    assert table.data[0][3] == '3'
    assert table.cells[1][3].data_column == 3


def test_remove_row_empty_data(table):
    expected_nb_rows = table.nb_rows - 1
    table.remove_row(1)
    check_nb_rows(table, expected_nb_rows)


def test_remove_empty_rows_between_data(table):
    for j in range(table.nb_cols - 1):
        table.cells[1][j + 1].text_value.set(j)
        table.cells[4][j + 1].text_value.set(j)
    table.remove_row(2)
    table.remove_row(2)
    assert len(table.data) == 2


def test_remove_all_rows(table):
    nb_rows = table.nb_rows
    for i in range(nb_rows):
        table.remove_row(1)
    check_nb_rows(table, 1)
    # check that the first row cannot be deleted
    table.remove_row(0)
    table.remove_row(0)
    check_nb_rows(table, 1)


def test_remove_row_with_data(table):
    expected_nb_rows = table.nb_rows - 1
    fill_data_one_page(table)
    table.remove_row(2)
    check_nb_rows(table, expected_nb_rows)
    assert len(table.data) == 4
    for j in range(4):
        assert len(table.data[j]) == 5
    for i in range(4):
        assert table.data[i][1] == '0'
        assert table.data[i][2] == '1'
        assert table.data[i][3] == '2'
        assert table.data[i][4] == '3'
    assert table.data[0][0] == 'DMU1'
    assert table.cells[1][1].data_row == 0
    assert table.data[1][0] == 'DMU3'
    assert table.cells[2][1].data_row == 1
    assert table.data[2][0] == 'DMU4'
    assert table.cells[3][1].data_row == 2
    assert table.data[3][0] == 'DMU5'
    assert table.cells[4][1].data_row == 3


def test_remove_all_rows_with_data(table):
    nb_rows = table.nb_rows
    fill_data_one_page(table)
    for i in range(nb_rows):
        table.remove_row(1)
    check_nb_rows(table, 1)
    assert len(table.data) == 0
    check_data_cols_rows(table)


def test_remove_empty_rows(table):
    nb_rows = table.nb_rows
    fill_data_one_page(table)
    table.remove_row(1)
    check_nb_rows(table, nb_rows - 1)
    assert len(table.data) == 4
    for j in range(4):
        assert len(table.data[j]) == 5
    for i in range(4):
        assert table.data[i][1] == '0'
        assert table.data[i][2] == '1'
        assert table.data[i][3] == '2'
        assert table.data[i][4] == '3'
    table.remove_row(10)
    check_nb_rows(table, nb_rows - 2)
    assert len(table.data) == 4
    for j in range(4):
        assert len(table.data[j]) == 5
    for i in range(4):
        assert table.data[i][1] == '0'
        assert table.data[i][2] == '1'
        assert table.data[i][3] == '2'
        assert table.data[i][4] == '3'


def test_remove_rows_multiple_pages(data_tab):
    data_tab.table.add_row()
    data_tab.show_loaded_data('tests/1.xls')
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '3 pages'
    nb_rows = data_tab.table.nb_rows
    print('nb_rows', nb_rows)
    data_tab.table.remove_row(20)
    check_nb_rows(data_tab.table, nb_rows)


def test_remove_rows_next_page(data_tab):
    data_tab.show_loaded_data('tests/1.xls')
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '3 pages'
    nb_rows = data_tab.table.nb_rows
    data_tab.navigation_frame.show_next_page()
    data_tab.table.remove_row(18)
    data_tab.table.remove_row(18)
    check_nb_rows(data_tab.table, nb_rows)
    data_tab.navigation_frame.show_prev_page()
    data_tab.table.remove_row(10)
    check_nb_rows(data_tab.table, nb_rows)


def test_remove_row_two_pages_data(data_tab):
    data_tab.show_loaded_data('tests/dataTestRemoveRow.xls')
    assert data_tab.navigation_frame.text_var_nb_pages.get() == '2 pages'
    nb_rows = data_tab.table.nb_rows
    print('nb_rows', nb_rows)
    data_tab.table.remove_row(1)
    data_tab.navigation_frame.show_next_page()
    data_tab.table.remove_row(1)
    print('data', data_tab.data)
    assert data_tab.table.nb_rows == nb_rows
    assert len(data_tab.data) == 23
    assert data_tab.data[0][0] == 2.0
    assert data_tab.data[0][1] == 20.0
    assert data_tab.data[0][2] == 10.0
    assert data_tab.data[17][0] == 19.0
    assert data_tab.data[17][1] == 190.0
    assert data_tab.data[17][2] == 95.0
    assert data_tab.data[18][0] == 20.0
    assert data_tab.data[18][1] == 200.0
    assert data_tab.data[18][2] == 100.0


def test_add_row_and_remove_added_row(table):
    row = table.nb_rows
    table.add_row()
    table.remove_row(row)
    check_nb_rows(table, row)


def test_remove_row_zero(table):
    nb_rows = table.nb_rows
    table.remove_row(0)
    check_nb_rows(table, nb_rows)
    assert len(table.data) == 0
    check_data_cols_rows(table)
