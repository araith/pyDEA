import pytest

from pyDEA.core.gui_modules.navigation_frame_gui import NavigationForTableFrame


class TableFrameMock(object):

    def __init__(self):
        self.nb_rows = 100
        self.display_data_called = False

    def display_data(self, row_index):
        self.display_data_called = True


@pytest.fixture
def nav_frame(request):
    nav_frame = NavigationForTableFrame(None, TableFrameMock())
    request.addfinalizer(nav_frame.destroy)
    return nav_frame


def test_reset_navigation(nav_frame):
    nav_frame.reset_navigation()
    assert nav_frame.current_page_str.get() == '1'
    assert nav_frame.text_var_nb_pages.get() == '1 pages'
    assert nav_frame.goto_spin.cget('to') == 1


def test_set_navigation(nav_frame):
    nav_frame.set_navigation(10)
    assert nav_frame.current_page_str.get() == '1'
    assert nav_frame.text_var_nb_pages.get() == '10 pages'
    assert nav_frame.goto_spin.cget('to') == 10


def test_on_page_change(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(3)
    nav_frame.on_page_change()
    assert nav_frame.table.display_data_called is True


def test_on_page_change_more_than_max(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(7)
    nav_frame.on_page_change()
    assert nav_frame.table.display_data_called is True
    assert nav_frame.current_page_str.get() == '5'


def test_on_page_change_negative(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(-7)
    nav_frame.on_page_change()
    assert nav_frame.table.display_data_called is True
    assert nav_frame.current_page_str.get() == '1'


def test_on_page_change_invalid(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set('text')
    nav_frame.on_page_change()
    assert nav_frame.table.display_data_called is True
    assert nav_frame.current_page_str.get() == '1'


def test_show_prev_page_ok(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(3)
    nav_frame.show_prev_page()
    assert nav_frame.current_page_str.get() == '2'
    assert nav_frame.table.display_data_called is True


def test_show_prev_page_invalid(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(1)
    nav_frame.show_prev_page()
    assert nav_frame.current_page_str.get() == '1'
    assert nav_frame.table.display_data_called is False


def test_show_next_page_ok(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(3)
    nav_frame.show_next_page()
    assert nav_frame.current_page_str.get() == '4'
    assert nav_frame.table.display_data_called is True


def test_show_next_page_invalid(nav_frame):
    nav_frame.set_navigation(5)
    nav_frame.current_page_str.set(5)
    nav_frame.show_next_page()
    assert nav_frame.current_page_str.get() == '5'
    assert nav_frame.table.display_data_called is False
