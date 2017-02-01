''' This module contains DataFrame class that implements a Notebook
    with two tabs for loading input data
    and displaying solution.
'''

from tkinter.ttk import Notebook

from pyDEA.core.gui_modules.data_tab_frame_gui import DataTabFrame
from pyDEA.core.gui_modules.solution_tab_frame_gui import SolutionTabFrame


class DataFrame(Notebook):
    ''' This class is a Notebook with two tabs: one tab is used for
        loading and editing input data,
        the other tab is used for displaying solution.

        Attributes:
            parent (Tk object): parent of this widget

                Note:
                    Parent must have object progress_bar, which value can
                    be reset as follows:

                    >>> parent.progress_bar["value"] = 0

            solution_tab (Frame): tab used for displaying solution
            data_tab (Frame): tab used for loading, displaying and
                editing input data

        Args:
            parent (Tk object): parent of this widget
            params_frame (ParamsFrame): frame with parameters
            current_categories (list of str): list of current categories, this
                list might be
                modified by this class
            data_from_params_file (StringVar): StringVar object that contains
                name of data file.
                It is used for communication between this frame and parameters
                frame. This argument is necessary for data_tab creation
            str_var_for_input_output_boxes (ObserverStringVar): object that
                contains current input and output categories and notifies
                table with data when data is loaded
                and some categories need to be checked. This argument is
                necessary for data_tab creation
    '''

    def __init__(self, parent, params_frame, current_categories,
                 data_from_params_file,
                 str_var_for_input_output_boxes, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.parent = parent
        self.solution_tab = None
        self.data_tab = DataTabFrame(self, params_frame, current_categories,
                                     data_from_params_file,
                                     str_var_for_input_output_boxes,
                                     height=100, *args, **kw)
        self.create_widgets(self.data_tab)

    def create_widgets(self, data_tab):
        ''' Creates tabs of the notebook.
        '''
        self.enable_traversal()
        self.add(data_tab, text='Data')
        self.solution_tab = SolutionTabFrame(self)
        self.add(self.solution_tab, text='Solution')

    def change_solution_tab_name(self, new_name):
        ''' Changes name of the solution tab.
            This method is needed to add star (*) to unsaved solution and
            to remove star.

            Args:
                new_name (str): new name for the solution tab
        '''
        self.tab(1, text=new_name)

    def reset_progress_bar(self):
        ''' Resets progress bar of the parent frame to zero.
        '''
        self.parent.progress_bar['value'] = 0
