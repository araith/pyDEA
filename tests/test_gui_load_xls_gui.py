from tkinter import Toplevel
import pytest

from pyDEA.core.gui_modules.load_xls_gui import AskSheetName


@pytest.fixture
def ask_sheet_name_frame(request):
    win = Toplevel()
    win.withdraw()
    names = ['sheet1', 'sheet2', 'sheet3']
    ask_sheet_name_frame = AskSheetName(win, names)
    request.addfinalizer(win.destroy)
    return ask_sheet_name_frame


def test_ok_btn(ask_sheet_name_frame):
    assert ask_sheet_name_frame.sheet_name_str.get() == 'sheet1'
    ask_sheet_name_frame.ok()
    assert ask_sheet_name_frame.sheet_name_str.get() == 'sheet1'


def test_cancel(ask_sheet_name_frame):
    assert ask_sheet_name_frame.sheet_name_str.get() == 'sheet1'
    ask_sheet_name_frame.cancel()
    assert ask_sheet_name_frame.sheet_name_str.get() == ''
