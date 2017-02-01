''' This module contains StyledCanvas class.
'''

from tkinter import Canvas

from pyDEA.core.utils.dea_utils import bg_color


class StyledCanvas(Canvas):
    ''' Implements Canvas object with a custom background colour.

        Args:
            parent (Tk object): parent of this widget.
    '''
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.configure(background=bg_color)
