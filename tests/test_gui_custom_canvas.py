from tkinter import Tk

from pyDEA.core.gui_modules.custom_canvas_gui import StyledCanvas
from pyDEA.core.utils.dea_utils import bg_color


def test_bg_color():
    parent = Tk()
    canvas = StyledCanvas(parent)
    assert canvas.cget('background') == bg_color
    parent.destroy()
