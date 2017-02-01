''' This module contains classes that implement multi-platform
    scrolling for frames. Code is mainly borrowed from web and
    slightly modified. Unfortunately, I don't have web-page address
    any more.
'''

from tkinter import VERTICAL, Y, RIGHT, LEFT, BOTH, N, W
from tkinter.ttk import Frame, Scrollbar

from pyDEA.core.gui_modules.custom_canvas_gui import StyledCanvas
from pyDEA.core.utils.dea_utils import on_canvas_resize

import platform
os = platform.system()


class MouseWheel(object):
    ''' This class bind scrolling events to a scroll object.
    '''
    def __init__(self, root, factor=1):
        global os
        self.activeArea = None
        if type(factor) == int:
            self.factor = factor
        else:
            raise Exception("Factor must be an integer.")

        if os == "Linux":
            root.bind_all('<4>', self.onMouseWheel,  add='+')
            root.bind_all('<5>', self.onMouseWheel,  add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self.onMouseWheel,  add='+')

        self.root = root

    def onMouseWheel(self, event):
        if self.activeArea:
            self.activeArea.onMouseWheel(event)

    def mouseWheel_bind(self, widget):
        self.activeArea = widget

    def mouseWheel_unbind(self):
        self.activeArea = None

    @staticmethod
    def build_function_onMouseWheel(widget, orient, scrollbar, factor=1):
        view_command = getattr(widget, orient+'view')
        if os == 'Linux':
            def onMouseWheel(event):
                # scroll moves only when it is not disables

                if (len(scrollbar.state()) == 0 or
                        scrollbar.state()[0] != 'disabled'):
                    if event.num == 4:
                        view_command("scroll", (-1)*factor, "units")
                    elif event.num == 5:
                        view_command("scroll", factor, "units")

        elif os == 'Windows':
            def onMouseWheel(event):
                if (len(scrollbar.state()) == 0 or
                        scrollbar.state()[0] != 'disabled'):
                    view_command("scroll", (-1)*int((event.delta/120)*factor),
                                 "units")

        elif os == 'Darwin':
            def onMouseWheel(event):
                if (len(scrollbar.state()) == 0 or
                        scrollbar.state()[0] != 'disabled'):
                    view_command("scroll", event.delta, "units")

        return onMouseWheel

    def add_scrolling(self, scrollingArea, xscrollbar=None, yscrollbar=None):
        scrollingArea.bind('<Enter>',
                           lambda event: self.mouseWheel_bind(scrollingArea))
        scrollingArea.bind('<Leave>',
                           lambda event: self.mouseWheel_unbind())
        scrollingArea.bind('<Configure>',
                           lambda event: on_canvas_resize(scrollingArea))

        if xscrollbar and not hasattr(xscrollbar, 'onMouseWheel'):
                setattr(xscrollbar, 'onMouseWheel',
                        self.build_function_onMouseWheel(scrollingArea, 'x',
                        xscrollbar, self.factor))

        if yscrollbar and not hasattr(yscrollbar, 'onMouseWheel'):
                setattr(yscrollbar, 'onMouseWheel',
                        self.build_function_onMouseWheel(scrollingArea, 'y',
                        yscrollbar, self.factor))

        active_scrollbar_on_mouse_wheel = yscrollbar or xscrollbar
        if active_scrollbar_on_mouse_wheel:
            setattr(scrollingArea, 'onMouseWheel',
                    active_scrollbar_on_mouse_wheel.onMouseWheel)

        for scrollbar in (xscrollbar, yscrollbar):
            if scrollbar:
                scrollbar.bind(
                    '<Enter>', lambda event,
                    scrollbar=scrollbar: self.mouseWheel_bind(scrollbar))
                scrollbar.bind('<Leave>',
                               lambda event: self.mouseWheel_unbind())


class VerticalScrolledFrame(Frame):
        ''' A pure Tkinter scrollable frame that actually works!
            Use the 'interior' attribute to place widgets inside the scrollable
            frame Construct and pack/place/grid normally
            This frame only allows vertical scrolling.

            Attributes:
                canvas (StyledCanvas): canvas.
                interior (frame): frame where all widgets are palced.

            Args:
                parent (Tk object): parent of this widget.
        '''
        def __init__(self, parent, *args, **kw):
            Frame.__init__(self, parent, *args, **kw)

            # create a canvas object and a vertical scrollbar for scrolling it
            vscrollbar = Scrollbar(self, orient=VERTICAL)
            vscrollbar.pack(fill=Y, side=RIGHT, expand=False)
            self.canvas = canvas = StyledCanvas(
                self, bd=0, highlightthickness=0,
                yscrollcommand=vscrollbar.set)
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            vscrollbar.config(command=canvas.yview)

            # reset the view
            canvas.xview_moveto(0)
            canvas.yview_moveto(0)

            # create a frame inside the canvas which will be scrolled with it
            self.interior = interior = Frame(canvas)
            interior_id = canvas.create_window(0, 0, window=interior,
                                               anchor=N+W)

            # track changes to the canvas and frame width and sync them,
            # also updating the scrollbar
            def _configure_interior(event):
                # update the scrollbars to match the size of the inner frame
                size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
                canvas.config(scrollregion="0 0 %s %s" % size)
                if interior.winfo_reqwidth() != canvas.winfo_width():
                    # update the canvas's width to fit the inner frame
                    canvas.config(width=interior.winfo_reqwidth())
            interior.bind('<Configure>', _configure_interior)

            def _configure_canvas(event):
                if interior.winfo_reqwidth() != canvas.winfo_width():
                   # update the inner frame's width to fill the canvas
                    canvas.itemconfigure(interior_id,
                                         width=canvas.winfo_width())
            canvas.bind('<Configure>', _configure_canvas)
            MouseWheel(self).add_scrolling(canvas, yscrollbar=vscrollbar)
