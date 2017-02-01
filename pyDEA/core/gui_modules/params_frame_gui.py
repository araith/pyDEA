''' This module contains class ParamsFrame which is responsible for
    all operations with parameters.

    Attributes:
        MAX_FILE_LBL_LENGTH (int): maximum length of the label with
            file name.
        TEXT_FOR_PARAMS_LBL (str): text displayed on one of the labels.
'''
import os

from tkinter import W, E, S, N, LEFT, IntVar
from tkinter.ttk import Frame, Label, Button, Notebook
from tkinter.ttk import Checkbutton
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning

from pyDEA.core.gui_modules.categories_checkbox_gui import CategoriesCheckBox
from pyDEA.core.gui_modules.scrollable_frame_gui import VerticalScrolledFrame
from pyDEA.core.data_processing.parameters import parse_parameters_from_file, Parameters
from pyDEA.core.data_processing.parameters import CATEGORICAL_AND_DATA_FIELDS, write_parameters_to_file
from pyDEA.core.utils.dea_utils import XPAD_VALUE, YPAD_VALUE
from pyDEA.core.gui_modules.weight_frame_gui import WeightFrame
from pyDEA.core.gui_modules.options_frame_gui import OptionsFrame

MAX_FILE_LBL_LENGTH = 400
TEXT_FOR_PARAMS_LBL = 'Parameters loaded from file: '


class ParamsFrame(Notebook):
    ''' This class implements various operations with parameters like
        loading and saving from and to file, modifying parameters values.

        Attributes:
            parent (Tk object): parent of this widget.
            params (Parameters): Parameters object with values of all
                parameters.
            current_categories (list of str): list of current valid categories.
            input_categories (CategoriesCheckBox): frame for displaying
                input categories.
            output_categories (CategoriesCheckBox): frame for displaying
                output categories.
            params_from_file_lbl (Label): label for displaying file name if
                parameters were loaded from file.
            data_from_params_file(StringVar): StringVar object used for
                communication of this widget with DataFrame. Changing the
                value of data_from_params_file
                triggers changes in DataFrame (like clearing all data and
                loading data from file).
            str_var_for_input_output_boxes (ObserverStringVar):
                ObserverStringVar
                object used for storing input and output categories and for
                tracking changes in input and output categories.
            weight_tab (WeightFrame): widget used for displaying and
                editing weights.
            load_without_data (IntVar): IntVar object used for Checkbutton,
                if its value
                is 1, then parameters will be loaded from file without data,
                if its value
                is 0, then parameters will be loaded from file with data.
            options_frame (OptionsFrame): widget used for displaying and
                modifying some of the parameters.

        Args:
            parent (Tk object): parent of this widget.
            current_categories (list of str): list of current valid categories.
            data_from_params_file(StringVar): StringVar object used for
                communication of this widget with DataFrame. Changing the value
                of data_from_params_file
                triggers changes in DataFrame (like clearing all data and
                loading data from file).
            str_var_for_input_output_boxes (ObserverStringVar):
                ObserverStringVar object used for
                storing input and output categories and for tracking changes
                in input and output categories.
            weights_status_str (StringVar): StringVar object used for changing
                label of weights editor, for details see WeightFrame.
    '''
    def __init__(self, parent, current_categories, data_from_params_file,
                 str_var_for_input_output_boxes, weights_status_str,
                 *args, **kw):
        Notebook.__init__(self, parent, *args, **kw)
        self.parent = parent
        self.params = Parameters()
        self.current_categories = current_categories
        self.input_categories_frame = None
        self.output_categories_frame = None
        self.params_from_file_lbl = None
        self.data_from_params_file = data_from_params_file
        self.str_var_for_input_output_boxes = str_var_for_input_output_boxes
        self.weight_tab = None
        self.load_without_data = IntVar()
        self.options_frame = None
        self.create_widgets(weights_status_str)

    def create_widgets(self, weights_status_str):
        ''' Creates all widgets.
        '''
        self.enable_traversal()
        self._create_params_tab()
        self.weight_tab = WeightFrame(self, self.current_categories,
                                      self.params, weights_status_str)
        self.add(self.weight_tab, text='Weights editor')

    def change_weight_tab_name(self, new_name):
        ''' Changes name of weights editor tab.

            Args:
                new_name (str): new name for weights editor tab.
        '''
        self.tab(1, text=new_name)

    def _create_params_tab(self):
        ''' Creates all widgets of the parameters tab.
        '''
        frame_for_all_objects = VerticalScrolledFrame(self)
        frame_for_all_objects.columnconfigure(0, weight=1)
        frame_for_all_objects.rowconfigure(0, weight=1)

        params_tab = frame_for_all_objects.interior
        params_tab.columnconfigure(0, weight=1, pad=5)

        frame_for_save_btns = Frame(params_tab)
        frame_for_save_btns.columnconfigure(0, weight=1)
        frame_for_save_btns.columnconfigure(1, weight=1)
        load_btn = Button(frame_for_save_btns, text='Load parameters',
                          command=self.load_file)
        load_btn.grid(row=0, column=0, sticky=W+N, pady=2)
        load_wo_data_box = Checkbutton(frame_for_save_btns,
                                       text='Load without data',
                                       variable=self.load_without_data)
        load_wo_data_box.grid(row=1, column=0, sticky=W+N, pady=2)
        save_btn = Button(frame_for_save_btns, text='Save parameters',
                          command=self.on_save_params)
        save_btn.grid(row=0, column=1, sticky=E+N, pady=2)
        save_btn = Button(frame_for_save_btns, text='Save parameters as...',
                          command=self.on_save_params_as)
        save_btn.grid(row=1, column=1, sticky=E+N, pady=2)
        frame_for_save_btns.grid(row=0, column=0, sticky=E+W,
                                 padx=XPAD_VALUE, pady=YPAD_VALUE)

        self.params_from_file_lbl = Label(params_tab, text=TEXT_FOR_PARAMS_LBL,
                                          anchor=W, justify=LEFT,
                                          wraplength=MAX_FILE_LBL_LENGTH)
        self.params_from_file_lbl.grid(row=1, column=0, columnspan=3,
                                       sticky=W+N, padx=XPAD_VALUE,
                                       pady=YPAD_VALUE)

        input_categories_list = CategoriesCheckBox(
            params_tab, 'Input categories:', True, self.params,
            'INPUT_CATEGORIES')
        self.input_categories_frame = input_categories_list
        input_categories_list.grid(row=4, column=0, sticky=W+N+S+E,
                                   padx=XPAD_VALUE,
                                   pady=YPAD_VALUE, columnspan=2)
        output_categories_list = CategoriesCheckBox(
            params_tab, 'Output categories:', False, self.params,
            'OUTPUT_CATEGORIES')
        self.output_categories_frame = output_categories_list
        output_categories_list.grid(row=5, column=0, sticky=W+N+S+E,
                                    padx=XPAD_VALUE,
                                    pady=YPAD_VALUE, columnspan=2)

        self.options_frame = OptionsFrame(params_tab, self.params,
                                          self.current_categories,
                                          self.input_categories_frame,
                                          self.output_categories_frame)
        self.options_frame.grid(row=6, column=0, columnspan=2,
                                sticky=N+S+W+E, padx=XPAD_VALUE,
                                pady=YPAD_VALUE)
        self.add(frame_for_all_objects, text='Parameters')

    def on_save_params(self):
        ''' Saves current parameter values to a file from where the\
            parameters were loaded.
            This file name is displayed. If no file name is displayed
            (i.e. parameters were not
            previously loaded from file), then asksaveasfilename dialogue
            is called.
        '''
        file_name = self.params_from_file_lbl.cget('text')
        if TEXT_FOR_PARAMS_LBL in file_name:
            file_name = file_name[len(TEXT_FOR_PARAMS_LBL):]
        if file_name:
            write_parameters_to_file(self.params, file_name)
        else:
            self.on_save_params_as()

    def on_save_params_as(self):
        ''' Calls asksaveasfilename dialogue and saves current values of
            parameters to
            the specified file.
        '''
        file_name = self._get_file_name_to_save()
        if file_name:
            write_parameters_to_file(self.params, file_name)

    def _get_file_name_to_save(self):
        ''' Calls asksaveasfilename dialogue. This method is overridden
            in unit tests.

            Returns:
                (str): file name.
        '''
        return asksaveasfilename(filetypes=[('Text files', '*.txt')],
                                 defaultextension='.txt')

    def load_file(self):
        ''' Loads parameters from file specified by the user.
        '''
        file_name = self._get_filename_for_load()
        if file_name:

            self.str_var_for_input_output_boxes.input_categories.clear()
            self.str_var_for_input_output_boxes.output_categories.clear()

            # save previous params
            params_to_restore = dict()
            for param_name in CATEGORICAL_AND_DATA_FIELDS:
                params_to_restore[param_name] = self.params.get_parameter_value(
                    param_name)
            self.params.copy_all_params(parse_parameters_from_file(file_name))

            if self.load_without_data.get() == 0:
                self.load_data_file_and_related_params(file_name,
                                                       params_to_restore)
            else:
                self.data_from_params_file.set('')
                # restore previous parameters
                for param_name, value in params_to_restore.items():
                    self.params.update_parameter(param_name, value)
            self.options_frame.set_params_values()

    def _get_filename_for_load(self):
        ''' Calls askopenfilename dialogue. This method is overridden
            in unit tests.

            Returns:
                (str): file name.
        '''
        file_types = [('Text files', '*.txt'), ('All files', '*.*')]
        file_name = askopenfilename(title='Choose a file', filetypes=file_types)
        return file_name

    def load_data_file_and_related_params(self, file_name, params_to_restore):
        ''' Loads data if possible and sets widgets to proper values
            depending on parameters.

            Args:
                file_name (str): file name of file with parameters. It is needed
                    to display it on parameters frame.
                params_to_restore (dict of str to str): dictionary of
                    previous values of parameters. They are used in order
                    to restore
                    previous values if loading of data from file fails.
        '''
        data_file = self.params.get_parameter_value('DATA_FILE')
        norm_data_path = os.path.normpath(data_file)
        if os.path.isfile(norm_data_path):
            params_to_restore = dict()
            # I have to store this here, because when I clean all data
            # from data tab, it deletes these values from params
            for param_name in CATEGORICAL_AND_DATA_FIELDS:
                params_to_restore[param_name] = self.params.get_parameter_value(
                    param_name)
            # this line calls clear all from data_tab
            self.data_from_params_file.set(norm_data_path)

            self.params_from_file_lbl.config(
                text=TEXT_FOR_PARAMS_LBL + file_name)
            for param_name, value in params_to_restore.items():
                self.params.update_parameter(param_name, value)

            self.add_categories(
                'INPUT_CATEGORIES', self.input_categories_frame,
                self.str_var_for_input_output_boxes.input_categories)
            self.add_categories(
                'OUTPUT_CATEGORIES', self.output_categories_frame,
                self.str_var_for_input_output_boxes.output_categories)
            self.str_var_for_input_output_boxes.set('notify')
            self.weight_tab.add_weights()
        else:
            self._show_warning(norm_data_path)
            for param_name, value in params_to_restore.items():
                self.params.update_parameter(param_name, value)

    def _show_warning(self, norm_data_path):
        ''' Shows warning that data cannot be loaded from file.
            This method is overridden in unit tests.
        '''
        showwarning('Warning', 'Cannot load data file: ' + norm_data_path +
                    '. Parameters will be loaded without data.')

    def change_category_name(self, old_name, new_name):
        ''' Changes category name in parameters and all widgets to a new name.
            If new name is empty string, then some of the parameters might
            be lost (for example, weight restrictions will be lost).

            Args:
                old_name (str): old name of the category.
                new_name (str): new name of the category.
        '''
        if old_name != new_name:
            self.input_categories_frame.change_category_name(old_name, new_name)
            self.output_categories_frame.change_category_name(old_name,
                                                              new_name)
            self.weight_tab.add_weights()
            if self.options_frame.combobox_text_var.get() == old_name:
                self.options_frame.change_categorical_box()
                self.options_frame.set_categorical_box(new_name)

    def add_categories(self, name, frame, categories_container):
        ''' Adds input or output categories to a specified widget
            with categories from parameters.

            Args:
                name (str): name of the parameter where categories come from,
                    possible values INPUT_CATEGORIES, OUTPUT_CATEGORIES.
                frame (CategoriesCheckBox): widget where categories will
                    be added.
                categories_container (list of str): list of categories where
                    categories from parameters will be added.
        '''
        categories = self.params.get_set_of_parameters(name)
        for category in categories:
            # we add only categories that are
            # present in data file
            if category in self.current_categories:
                frame.add_category(category)
                categories_container.append(category)
            else:
                self.params.remove_category_from_params(name, category)

    def clear_all(self):
        ''' Clears all parameters and corresponding widgets.
        '''
        self.input_categories_frame.remove_all_categories()
        self.output_categories_frame.remove_all_categories()
        self.options_frame.combobox_text_var.set('')
        self.weight_tab.remove_all_weights()
        self.params.clear_all_categorical_and_data_fields()
        self.params_from_file_lbl.config(text='')
        self.str_var_for_input_output_boxes.input_categories.clear()
        self.str_var_for_input_output_boxes.output_categories.clear()
