''' This module contains class TableModifierFrame that creates buttons
    for adding and removing rows and columns from data table.
'''
from tkinter import E, N, W, Spinbox, StringVar
from tkinter.ttk import Frame, Button

from pyDEA.core.utils.dea_utils import calculate_nb_pages, calculate_start_row_index


class TableModifierFrame(Frame):
    ''' This class creates buttons for adding and removing
        rows and columns from data table.

        Attributes:
            table (TableFrameWithInputOutputBox): data table.
            row_str_var (StringVar): stores number of rows that should
                be added to the data table.
            col_str_var (StringVar): stores number of columns that
                should be added to the data table.
            set_navigation (callable): function that sets number of
                pages to a given number,
                for details see navigation_frame_gui module.

        Args:
            parent (Tk object): parent of this frame.
            table (TableFrameWithInputOutputBox): data table.
            clear_all_fnc (callable): function that should be called when
                "Clear all" button is pressed.
            set_navigation (callable): function that sets number of pages
                to a given number,
                for details see navigation_frame_gui module.
    '''
    def __init__(self, parent, table, clear_all_fnc, set_navigation, *args,
                 **kw):
        super().__init__(parent, *args, **kw)
        self.table = table
        self.row_str_var = StringVar()
        self.col_str_var = StringVar()
        self.set_navigation = set_navigation
        self.create_widgets(clear_all_fnc)

    def create_widgets(self, clear_all_fnc):
        ''' Creates widgets of this frame.

            Args:
                clear_all_fnc (function): function that should be called when
                    "Clear all" button is pressed.
        '''
        rows_spinbox = Spinbox(self, from_=1, to=100, width=3,
                               textvariable=self.row_str_var)
        rows_spinbox.grid(row=0, column=0, pady=3, padx=3)
        add_row_btn = Button(self, text='Add row(s)', command=self.add_rows)
        add_row_btn.grid(row=0, column=1, sticky=N+E+W, pady=3)
        remove_row_btn = Button(self, text='Remove row(s)',
                                command=self.remove_rows)
        remove_row_btn.grid(row=1, column=1, sticky=N+E+W, pady=3)
        columns_spinbox = Spinbox(self, from_=1, to=100, width=3,
                                  textvariable=self.col_str_var)
        columns_spinbox.grid(row=2, column=0, pady=3, padx=3)
        add_column_btn = Button(self, text='Add column(s)',
                                command=self.add_columns)
        add_column_btn.grid(row=2, column=1, sticky=N+E+W, pady=3)
        remove_column_btn = Button(self, text='Remove column(s)',
                                   command=self.remove_columns)
        remove_column_btn.grid(row=3, column=1, sticky=N+E+W, pady=3)
        clear_all_btn = Button(self, text='Clear all', command=clear_all_fnc)
        clear_all_btn.grid(row=4, column=1, sticky=N+E+W, pady=3)

    def add_rows(self):
        ''' Adds rows to the data table. Number of rows is specified in Spinbox.
            If invalid value is given in Spinbox, only one row is added.
            Rows are added to the end of the table.
        '''
        nb_rows = self.get_nb_to_add(self.row_str_var)
        for i in range(nb_rows):
            self.table.add_row()

        # if data is displayed on multiple pages, when adding new row
        # we re-display data
        if len(self.table.cells) > 1:
            start_row = self.table.cells[1][0].data_row
            if start_row != -1:
                if len(self.table.data) - start_row >= self.table.nb_rows - 1:
                    # we need to reposition data on several pages
                    self.table.display_data(start_row)
                    nb_pages = calculate_nb_pages(len(self.table.data),
                                                  self.table.nb_rows)
                    self.set_navigation(nb_pages, False)

    def get_nb_to_add(self, str_var):
        ''' Calculates valid number of rows or columns that should be added
            to the data table.

            Args:
                str_var (StringVar): StringVar object that stores number
                    of rows or columns that must be added to the data table.

            Returns:
                int: positive integer number if str_var stores such a
                    number, 1 if negative or invalid value is stored in str_var.

            Example:
                >>> table.row_str_var.set(10)
                >>> tabel.get_nb_to_add(table.row_str_var)
                10
                >>> table.row_str_var.set(-1)
                >>> tabel.get_nb_to_add(table.row_str_var)
                1
                >>> table.row_str_var.set("abc")
                >>> tabel.get_nb_to_add(table.row_str_var)
                1
        '''
        try:
            nb_values = int(str_var.get())
            if nb_values <= 0:
                nb_values = 1
        except ValueError:
            nb_values = 1
        str_var.set(nb_values)
        return nb_values

    def remove_rows(self):
        ''' Removes rows that are checked in checkboxes for removal.
            First row cannot be removed.
        '''
        if self.table.nb_rows > 0:
            row_index = 1
            prev_nb_rows = self.table.nb_rows
            while row_index < self.table.nb_rows:
                box, var = self.table.row_checkboxes[row_index]
                if var is not None and var.get() == 1:
                    if self.table.remove_row(row_index) is False:
                        row_index += 1
                else:
                    row_index += 1

            # when rows are removed number of pages to display data might change
            if len(self.table.cells) > 1:
                start_row = self.table.cells[1][0].data_row
                if start_row != -1:
                    nb_pages = calculate_nb_pages(len(self.table.data),
                                                  self.table.nb_rows)
                    self.set_navigation(nb_pages, False)
                    # + 2 for index and first row is for categories
                    page_number = calculate_nb_pages(start_row + 2,
                                                  self.table.nb_rows)
                    new_start_row = calculate_start_row_index(
                        page_number, self.table.nb_rows)
                    self.table.display_data(new_start_row)

    def add_columns(self):
        ''' Adds columns to the data table. Number of columns is specified
            in Spinbox.
            If invalid value is given in Spinbox, only one column is added.
            Columns are added to the end of the table.
        '''
        nb_cols = self.get_nb_to_add(self.col_str_var)
        for i in range(nb_cols):
            self.table.add_column()

    def remove_columns(self):
        ''' Removes columns that are checked in checkboxes for removal.
            First column cannot be removed.
        '''
        if self.table.nb_cols > 1:
            col_index = 0
            while col_index < self.table.nb_cols - 1:
                box, var = self.table.col_checkboxes[col_index]
                if var.get() == 1:
                    self.table.remove_column(col_index + 1)
                else:
                    col_index += 1
