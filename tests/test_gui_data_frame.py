from tkinter import StringVar, Tk
from tkinter.ttk import Frame
import pytest

from pyDEA.core.gui_modules.data_frame_gui import DataFrame

from tests.test_gui_data_tab_frame import ParamsFrameMock


class ParentMock(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.progress_bar = {'value': 100}


@pytest.fixture
def data_book(request):
    parent = Tk()
    current_categories = []
    data_book = DataFrame(ParentMock(parent), ParamsFrameMock(parent),
                          current_categories,
                          StringVar(master=parent), StringVar(master=parent))
    request.addfinalizer(parent.destroy)
    return data_book


def test_change_solution_tab_name(data_book):
    new_name = 'New solution name'
    data_book.change_solution_tab_name(new_name)
    assert data_book.tab(1, option='text') == new_name


def test_reset_progress_bar(data_book):
    data_book.reset_progress_bar()
    assert data_book.parent.progress_bar['value'] == 0
