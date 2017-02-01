''' This module contains class NavigationForTableFrame.
'''

from tkinter import Spinbox, StringVar, N, W
from tkinter.ttk import Frame, Label, Button

from pyDEA.core.utils.dea_utils import calculate_start_row_index


class NavigationForTableFrame(Frame):
    ''' This class is responsible for navigation over the table object.
        Table rows are displayed page by page.
        This class provides buttons that allow to navigate from page
        to page.

        Attributes:
            table (TableFrame or any object that has attribute nb_rows and
                implements display_data method): table that should be navigated.
            goto_spin (Spinbox): Spinbox widget that allows to enter page
                number and to switch between pages.
            text_var_nb_pages (StringVar): text variable that shows total
                number of pages.
            current_page_str (StringVar): text variable that stores
                currently displayed page.

        Args:
            parent (Tk object): parent for this frame.
            table (TableFrameWithInputOutputBox): table with multiple pages that
                will be navigated by this frame.
    '''
    def __init__(self, parent, table, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.table = table
        self.goto_spin = None
        self.text_var_nb_pages = StringVar()
        self.current_page_str = StringVar()
        self.create_widgets()

    def create_widgets(self):
        ''' Creates all necessary widgets for navigation.
        '''
        prev_btn = Button(self, text='<<', width=5,
                          command=self.show_prev_page)
        prev_btn.grid(row=0, column=0, sticky=N, padx=3)
        next_btn = Button(self, text='>>', width=5,
                          command=self.show_next_page)
        next_btn.grid(row=0, column=1, sticky=N)
        goto_lbl = Label(self, text='Go to')
        goto_lbl.grid(row=0, column=3, sticky=N, padx=5)

        self.goto_spin = Spinbox(self, width=7, from_=1, to=1,
                                 textvariable=self.current_page_str,
                                 command=self.on_page_change)

        self.goto_spin.bind('<Return>', self.on_page_change)
        self.goto_spin.grid(row=0, column=4, sticky=N, padx=5)
        nb_pages_lb = Label(self, textvariable=self.text_var_nb_pages)
        nb_pages_lb.grid(row=0, column=5, sticky=W+N, padx=5)
        self.reset_navigation()

    def show_prev_page(self):
        ''' Displays previous page.

            This method is called when user presses button '<<'.
            If the first page is currently displayed and the method is called,
            then the call to this method is ignored.
        '''
        prev_page_index = int(self.current_page_str.get()) - 1
        if prev_page_index > 0:
            self.current_page_str.set(prev_page_index)
            self.on_page_change()

    def show_next_page(self):
        ''' Displays next page.

            This method is called when user presses button '>>'.
            If the last page is currently displayed and the method is called,
            then the call to this method is ignored.
        '''
        next_page_index = int(self.current_page_str.get()) + 1
        if next_page_index <= int(self.goto_spin.cget('to')):
            self.current_page_str.set(next_page_index)
            self.on_page_change()

    def on_page_change(self, *args):
        ''' Displays a page which number is currently stored in
            current_page_str.

            This method is called in show_next_page(), show_prev_page() and
            when the user enters data and presses Enter.
            args are supplied by Return event.
            If the entered value is invalid, then the first page is displayed.
            If the entered value is zero or negative, then the first page is
            isplayed.
            If the entered value is larger than the total number of pages,
            then the last page is displayed.
        '''
        try:
            curr_page = int(self.current_page_str.get())
        except ValueError:
            curr_page = 1
            self.current_page_str.set(curr_page)

        max_page = int(self.goto_spin.cget('to'))
        if curr_page > max_page:
            curr_page = max_page
            self.current_page_str.set(curr_page)
        if curr_page <= 0:
            curr_page = 1
            self.current_page_str.set(curr_page)
        # second -1 because row indeces start with 0
        row_index = calculate_start_row_index(curr_page, self.table.nb_rows)

        self.table.display_data(row_index)

    def reset_navigation(self):
        ''' Resets navigation parameters.

            Sets current page number to 1 and total number of pages to zero.
        '''
        self.current_page_str.set('1')
        self.text_var_nb_pages.set('1 pages')
        self.goto_spin.config(to=1)

    def set_navigation(self, nb_data_pages, reset_curr_page=True):
        ''' Sets navigation parameters.

            Sets current page number to 1 and total number of pages
            to nb_data_pages.

            Args:
                nb_data_pages (int): new value for the total number of pages.
                reset_curr_page (bool): True is current page must be reset to 1,
                    False otherwise.
        '''
        self.goto_spin.config(to=nb_data_pages)
        if reset_curr_page:
            self.current_page_str.set('1')
        self.text_var_nb_pages.set('{0} pages'.format(nb_data_pages))
