''' This module contains TextFrame class that is responsible for
    displaying solution tabs in text widget.
'''

from tkinter import Text, NONE, N, W, E, S, HORIZONTAL, END, SEL, INSERT
from tkinter import NUMERIC
from tkinter.ttk import Frame, Scrollbar

from pyDEA.core.data_processing.solution_text_writer import SolutionTextWriter


class TextFrame(Frame):
    ''' Implements text widget for displaying one solution tab.

        Attributes:
            name (str): solution tab name.
            text_writer (SolutionTextWriter): object that knows how
                to format data.

        Args:
            parent (Tk object): parent of this widget.
    '''
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.name = ''
        self.create_widgets()
        self.text_writer = SolutionTextWriter('\t', self.write_text)

    def write_text(self, data):
        ''' Writes given data to text widget.

            Args:
                data (str): string that should be displayed.
        '''
        self.text.insert(END, data)

    def create_widgets(self):
        ''' Creates all widgets.
        '''
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(self, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = Scrollbar(self)
        yscrollbar.grid(row=0, column=1, sticky=N+S)

        self.text = Text(self, wrap=NONE,
                         xscrollcommand=xscrollbar.set,
                         yscrollcommand=yscrollbar.set)

        self.text.bind("<Control-Key-a>", self.select_all)
        self.text.bind("<Control-Key-A>", self.select_all)

        self.text.grid(row=0, column=0, sticky=N+S+E+W)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

    def clear_all_data(self):
        ''' Removes all text from text widget.
        '''
        self.text.delete('1.0', END)

    def select_all(self, event):
        ''' Selects all data in the text widget. This event is
            called when user presses Control-Key-a or Control-Key-A.

            Returns:
                str: string break.
        '''
        self.text.tag_add(SEL, '1.0', END)
        self.text.mark_set(INSERT, '1.0')
        self.text.see(INSERT)
        return 'break'

    def write(self, row_index, column_index, data):
        ''' Writes given data to the text widget.

            Args:
                row_index (int): row index.
                column_index (int): column index.
                data (str): text to write.
        '''
        self.text_writer.write(row_index, column_index, data)
        self.text.tag_add('all_text', '1.0', 'end')
        self.text.tag_configure('all_text',  tabs=('1.5i', NUMERIC))
