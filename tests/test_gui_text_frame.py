from tkinter import END, Tk
import pytest

from pyDEA.core.gui_modules.text_frame_gui import TextFrame


@pytest.fixture
def text_frame(request):
    parent = Tk()
    text_frame = TextFrame(parent)
    request.addfinalizer(parent.destroy)
    return text_frame


def test_clear_all_data(text_frame):
    text_frame.text.insert(END, 'some text \n haha')
    text_frame.clear_all_data()
    assert text_frame.text.get(1.0, END) == '\n'


def test_select_all(text_frame):
    text_frame.text.insert(END, 'some text \n haha')
    text_frame.select_all(None)
    assert text_frame.text.get(
        'sel.first', 'sel.last') == 'some text \n haha\n'


def test_write(text_frame):
    text_frame.write(0, 0, 'A')
    assert text_frame.text.get(1.0, END) == '\nA\n'
    text_frame.write(0, 1, '123')
    assert text_frame.text.get(1.0, END) == '\nA\t123.000000\n'
    text_frame.write(1, 0, 'new text')
    assert text_frame.text.get(1.0, END) == '\nA\t123.000000\nnew text\n'
    text_frame.write(1, 1, '3.6')
    assert text_frame.text.get(
        1.0, END) == '\nA\t123.000000\nnew text\t3.600000\n'
    text_frame.write(2, 1, 'haha')
    assert text_frame.text.get(
        1.0, END) == '\nA\t123.000000\nnew text\t3.600000\n\thaha\n'
