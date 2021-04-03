''' This module contains class AskSheetName that is responsible for
    asking the user to specify the sheet name of the xlsx-file where input
    data is.
'''

from tkinter import W, E, N, StringVar
from tkinter.ttk import Frame, Label, Combobox, Button


class AskSheetName(Frame):
    ''' This class is responsible for asking the user to
        specify the sheet name of the xlsx-file where input data is.

        Attributes:
            parent (Toplevel): new window where this Frame will be situated.
            names (list of str): list of available sheet names.
            sheet_name_str (StringVar): StringVar object used for reading
                what sheet was chosen by the user.

        Args:
            parent (Toplevel): new window where this Frame will be situated.
            names (list of str): list of available sheet names.
    '''
    def __init__(self, parent, names, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.parent = parent
        self.sheet_name_str = StringVar()
        self.create_widgets(names)
        self.update_idletasks()

    def create_widgets(self, names):
        ''' Creates appropriate widgets.

            Args:
                names (list of str): list of available sheet names.
        '''
        sheet_name_lbl = Label(self,
                               text='Choose sheet name where data is stored:')
        sheet_name_lbl.grid(sticky=N+W, padx=5, pady=5)
        sheet_names_box = Combobox(self, state="readonly", width=20,
                                   textvariable=self.sheet_name_str,
                                   values=names)
        sheet_names_box.current(0)
        sheet_names_box.grid(row=1, column=0, columnspan=2,
                             sticky=N+W, padx=5, pady=5)
        ok_btn = Button(self, text='OK', command=self.ok)
        ok_btn.grid(row=2, column=0, sticky=N+E, padx=5, pady=5)
        ok_btn.bind('<Return>', self.ok)
        ok_btn.focus()
        cancel_btn = Button(self, text='Cancel', command=self.cancel)
        cancel_btn.grid(row=2, column=1, sticky=N+E, padx=5, pady=5)
        cancel_btn.bind('<Return>', self.cancel)

    def cancel(self, event=None):
        ''' This method is called if the user presses Cancel button.
            In this case sheet name is set to empty string.

            Args:
                event (Tk event, optional): event that is given when the
                    button is pressed.  It is ignored in this method.
        '''
        self.sheet_name_str.set('')
        self.parent.destroy()

    def ok(self, event=None):
        ''' This method is called if the user presses OK button.
            In this case sheet name is set to the currently selected value
            in Combobox.

            Args:
                event (Tk event, optional): event that is given when the
                    button is pressed.  It is ignored in this method.
        '''
        self.parent.destroy()
