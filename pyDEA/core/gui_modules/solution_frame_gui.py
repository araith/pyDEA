''' This module contains classes responsible for displaying
    solution in GUI.
'''

from tkinter.ttk import Notebook

from pyDEA.core.gui_modules.table_gui import TableFrame
from pyDEA.core.gui_modules.text_frame_gui import TextFrame
from pyDEA.core.data_processing.write_data import FileWriter
from pyDEA.core.utils.progress_recorders import GuiProgress


class SolutionFrame(Notebook):
    ''' This class is responsible for creating tabs with
        various information about solution to a given problem.

        Attributes:
            parent (Tk object): parent of this widget.
            last_modified_tab (int): index of the last modified tab.
            nb_tabs (int): total number of tabs.
            all_tabs (list of Frame): list of all tabs.
            nb_filled_tabs (int): number of filled tabs.

        Args:
            parent (Tk object): parent of this widget.
    '''
    def __init__(self, parent, *args, **kw):
        Notebook.__init__(self, parent, *args, **kw)
        self.parent = parent
        self.last_modified_tab = -1
        self.nb_tabs = 0
        self.all_tabs = []
        self.nb_filled_tabs = 0

    def create_tab(self, name):
        ''' Creates a tab with a given name.

            Args:
                name (str): name of the tab.
        '''
        tab = self._create_tab_object()
        tab.pack()
        self.add(tab, text=name)
        self.all_tabs.append(tab)

    def _create_tab_object(self):
        ''' Allocates a proper Frame object that is placed on each tab.

            Returns:
                Frame: allocated frame.
        '''
        return TableFrame(self)

    def show_solution(self, solutions, params_to_print, all_params, run_date,
                      total_seconds, ranks=None, categorical=None):
        ''' Displays a given solution.

            Args:
                solutions (list of Solution): list with solutions that
                    must be displayed, can have 1, 2 or 4 elements.
                params_to_print (Parameters): parameters that should be
                    displayed.
                all_params (list of str): list with strings that should
                    appear before printing every solution from solutions.
                run_date (datetime): date and time when the problem was solved.
                total_seconds (float): time (in seconds) needed to solve
                    the problem.
                ranks (list of dict of str to double, optional):
                    list that contains dictionaries that map DMU code
                    to peel the onion rank.
                categorical (str, optional): name of the categorical variable
                    used in categorical analysis.
        '''
        self.create_default_tabs(solutions, params_to_print, all_params,
                                 run_date, total_seconds, ranks, categorical)

    def create_default_tabs(self, solutions, params_to_print, all_params,
                            run_date, total_seconds, ranks, categorical):
        ''' Creates all tabs.

            Args:
                solutions (list of Solution): list with solutions that
                    must be displayed, can have 1, 2 or 4 elements.
                params_to_print (Parameters): parameters that should be
                    displayed.
                all_params (list of str): list with strings that should
                    appear before printing every solution from solutions.
                run_date (datetime): date and time when the problem was solved.
                total_seconds (float): time (in seconds) needed to solve
                    the problem.
                ranks (list of dict of str to double):
                    list that contains dictionaries that map DMU code
                    to peel the onion rank.
                categorical (str): name of the categorical variable
                    used in categorical analysis.
        '''
        writer = FileWriter(params_to_print, self, run_date, total_seconds,
                           ranks=ranks, categorical=categorical)
        nb_models = len(solutions)
        # +1 for parameters sheet, it is stored separately
        nb_sheets = len(writer.worksheets) + 1
        progress_recorder = GuiProgress(self.parent.progress_bar, nb_models,
                                        nb_sheets)
        self.last_modified_tab = -1
        self.clear_all_tabs()
        self.nb_filled_tabs = 0
        for count, sol in enumerate(solutions):
            writer.write_data(sol, all_params[count], progress_recorder)
        self.modify_tab_names()
        self.remove_unused_tabs()
        progress_recorder.set_position(100)

    def add_sheet(self, tab_name):
        ''' Creates a tab with a given name.

            Args:
                tab_name (str): tab name.

            Returns:
                Frame: created tab.
        '''
        self.last_modified_tab += 1
        if self.last_modified_tab >= self.nb_tabs:
            self.create_tab(tab_name)
            self.nb_tabs += 1
        self.nb_filled_tabs += 1
        return self.all_tabs[self.last_modified_tab]

    def clear_all_tabs(self):
        ''' Clears all tabs.
        '''
        for tab in self.all_tabs:
            tab.clear_all_data()

    def modify_tab_names(self):
        ''' Modifies tab names according to the names that were passed
            as a parameter when tab was created.
        '''
        for count, tab in enumerate(self.all_tabs):
            self.tab(count, text=tab.name)

    def remove_unused_tabs(self):
        ''' Removes unused tabs.
        '''
        if self.nb_filled_tabs < self.nb_tabs:
            i = self.nb_tabs-1
            while self.nb_tabs != self.nb_filled_tabs:
                self.all_tabs[i].destroy()
                self.all_tabs.pop(i)
                self.nb_tabs -= 1


class SolutionFrameWithText(SolutionFrame):
    ''' This class creates a different frame for displaying solution
        as a plain text instead of table.

        Note:
            this works much faster than tables.
    '''
    def _create_tab_object(self):
        return TextFrame(self)
