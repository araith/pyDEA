''' This module contains class responsible for displaying solution
    on the screen.

    Attributes:
        MAX_FILE_PARAMS_LBL_LENGTH (int): module constant that describes
            maximum length of the label with a file name
'''
import os

from tkinter import LEFT, W, N, E, S, IntVar
from tkinter.ttk import Frame, Label, Button, Progressbar, Radiobutton
from tkinter.filedialog import asksaveasfilename, askdirectory

from pyDEA.core.utils.dea_utils import SOLUTION_XLSX_FILE
from pyDEA.core.utils.dea_utils import TEXT_FOR_FILE_LBL
from pyDEA.core.gui_modules.solution_frame_gui import SolutionFrameWithText
from pyDEA.core.data_processing.write_data_to_xls import XLSWriter
from pyDEA.core.data_processing.xlsx_workbook import XlsxWorkbook
from pyDEA.core.data_processing.solution_text_writer import TxtWriter
from pyDEA.core.utils.progress_recorders import GuiProgress

MAX_FILE_PARAMS_LBL_LENGTH = 500


class SolutionTabFrame(Frame):
    ''' This class is responsible for displaying solution on the screen.
        It extends Frame class.

        Attributes:
                parent (Tk object that can contain Frame): parent that can
                        contain Frame, MUST implement method
                        change_solution_tab_name(str).
                data_from_file_lbl (Label): label that contains file name
                    with data if specified.
                solution_tab (SolutionFrameWithText): notebook with tabs
                    describing solution.
                model_solutions (list of Solution): list with one or more
                    solutions that have been generated after running algorithm.
                param_strs (list of str): list with strings that should appear
                    before printing every solution from model_solutions.
                ranks (list of list of int): list of ranks corresponding to
                    every solution from model_solutions, ranks are generated
                    by peel-the-onion algorithm.
                categorical (str): name of the categorical variable used in
                    categorical analysis.
                progress_bar (Progressbar): progress bar to show how solution
                    is loaded or saved to file.
                status_lbl (Label): label for displaying solution status.
                solution_format_var (IntVar): IntVar object that tracks which
                    file format is chosen for solution.
    '''
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.parent = parent
        self.data_from_file_lbl = None
        self.solution_tab = None
        self.model_solutions = None
        self.param_strs = None
        self.ranks = None
        self.params = None
        self.categorical = None
        self.run_date = None
        self.total_seconds = 0
        self.progress_bar = None
        self.status_lbl = None
        self.solution_format_var = IntVar()
        self.create_widgets()

    def create_widgets(self):
        ''' Creates appropriate widgets on this frame.
        '''
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        frame_for_save_btn = Frame(self)
        frame_for_save_btn.columnconfigure(1, weight=1)
        self.status_lbl = Label(frame_for_save_btn, text='')
        self.status_lbl.grid(row=0, column=1, sticky=N+W)
        save_solution_btn = Button(frame_for_save_btn, text='Save solution',
                                   command=self.on_save_solution)
        save_solution_btn.grid(row=1, column=0, sticky=W+N, padx=5, pady=5)
        self.progress_bar = Progressbar(frame_for_save_btn,
                                        mode='determinate', maximum=100)
        self.progress_bar.grid(row=1, column=1, sticky=W+E, padx=10, pady=5)

        frame_for_save_btn.grid(sticky=W+N+E+S, padx=5, pady=5)

        frame_for_btns = Frame(self)
        self._create_file_format_btn('*.xlsx', 1, frame_for_btns, 0)
        self._create_file_format_btn('*.csv', 2, frame_for_btns, 1)
        self.solution_format_var.set(1)

        frame_for_btns.grid(row=1, column=0, sticky=W+N+E+S, padx=5, pady=5)
        self.data_from_file_lbl = Label(self, text=TEXT_FOR_FILE_LBL, anchor=W,
                                        justify=LEFT,
                                        wraplength=MAX_FILE_PARAMS_LBL_LENGTH)
        self.data_from_file_lbl.grid(row=2, column=0, padx=5, pady=5,
                                     sticky=W+N)

        self.solution_tab = SolutionFrameWithText(self)
        self.solution_tab.grid(row=3, column=0, sticky=W+E+S+N, padx=5, pady=5)

    def _create_file_format_btn(self, btn_text, var_value, parent, column):
        ''' Creates and grids Radiobutton used for choosing solution file
            format.

            Args:
                btn_text (str): text displayed next to the Radiobutton.
                var_value (int): value of the IntVar associated with this
                    Radiobutton.
                parent (Tk object): parent of this Radiobutton.
                column (int): column index where this Radiobutton
                    should be gridded.
        '''
        sol_format_btn = Radiobutton(parent, text=btn_text,
                                     variable=self.solution_format_var,
                                     value=var_value)
        sol_format_btn.grid(row=2, column=column, sticky=W+N, padx=2)

    def on_save_solution(self):
        ''' Saves solution to file.

            This method is called when save solution button is pressed.
            If there is a solution, this method will ask user to provide
            a file name where solution should be stored. If a valid name
            is provided,
            solution is saved to that file. Allowed file format is .xlsx.

            If the user checked 'csv' as solution output format, then
            the user will be asked to choose a directory where all csv files
            will be written.
        '''
        if self.model_solutions is not None:
            assert(self.param_strs is not None)
            if self.solution_format_var.get() == 1: #xlsx
                file_name = self.ask_file_name_to_save(
                    self.solution_format_var.get())
                dir_name = ''
            else: #csv
                dir_name = askdirectory()
                file_name = ''
            if file_name or dir_name:
                print(file_name)
                self.status_lbl.config(text='Saving solution to file...')
                if file_name.endswith('.xlsx'):
                    work_book = XlsxWorkbook()
                else:
                    # all not supported formats will be written to csv
                    assert(dir_name)
                    work_book = TxtWriter(dir_name)
                writer = XLSWriter(self.params, work_book, self.run_date,
                                   self.total_seconds,
                                   ranks=self.ranks,
                                   categorical=self.categorical)
                nb_models = len(self.model_solutions)
                # +1 for parameters sheet, it is stored separately
                nb_sheets = len(writer.worksheets) + 1
                progress_recorder = GuiProgress(self.progress_bar, nb_models,
                                                nb_sheets)

                try:
                    for count, sol in enumerate(self.model_solutions):
                        writer.write_data(sol, self.param_strs[count],
                                          progress_recorder)
                    work_book.save(file_name)
                except ValueError:
                    # can happen if maximum number of rows is exceeded
                    self.status_lbl.config(
                        text='File is too large for xlsx format,'
                        ' it will be saved to csv instead')
                    work_book = TxtWriter(os.path.splitext(file_name)[0])
                    writer = XLSWriter(self.params, work_book, self.run_date,
                                       self.total_seconds,
                                       ranks=self.ranks,
                                       categorical=self.categorical)
                    progress_recorder.set_position(0)
                    for count, sol in enumerate(self.model_solutions):
                        writer.write_data(sol, self.param_strs[count],
                                          progress_recorder)
                    work_book.save(file_name)
                progress_recorder.set_position(100)
                self.parent.change_solution_tab_name('Solution')
                self.status_lbl.config(text='Solution saved')

    def ask_file_name_to_save(self, ext_code):
        ''' Calls asksaveasfilename dialogue to ask the user where file
            should be saved.
            If file without extension is entered, default extension
            will be used (.xlsx).
            This method is used to mock this object for unit tests.

            Args:
                ext_code (int): code for file extension 1 - xlsx.
        '''
        if ext_code == 1:
            filetype = SOLUTION_XLSX_FILE
        return asksaveasfilename(filetypes=filetype, defaultextension='.xlsx')

    def show_solution(self, solutions, params, param_strs, run_date,
                      total_seconds, ranks=None, categorical=None):
        ''' Displays solution on the screen.

            Args:
                solutions (list of Solution): list of solutions (might
                    contain just one solution)
                    that have been generated after running algorithm.
                params (Parameters): object with parameters that will
                    be written to file on the Parameters page.
                param_strs (list of str): list with strings that
                    should appear before
                    printing every solution from model_solutions.
                ranks (list of list of int): list of ranks corresponding
                    to every solution from model_solutions, ranks are
                    generated by peel-the-onion algorithm.
                categorical (str): name of the categorical variable used
                    in categorical analysis.
        '''
        self.status_lbl.config(text='')
        self.model_solutions = solutions
        self.param_strs = param_strs
        self.ranks = ranks
        self.params = params
        self.categorical = categorical
        self.run_date = run_date
        self.total_seconds = total_seconds
        self.status_lbl.config(text='Loading solution...')
        self.solution_tab.show_solution(solutions, params, param_strs, run_date,
                                        total_seconds, ranks, categorical)
        self.parent.change_solution_tab_name('Solution*')
        self.status_lbl.config(text='Solution loaded')

    def update_data_file_name(self, new_data_file_name):
        ''' Updates label with data file name.

            Args:
                new_data_file_name (str): new value of the data file name
        '''
        self.data_from_file_lbl.config(text=TEXT_FOR_FILE_LBL
                                       + new_data_file_name)
