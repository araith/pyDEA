''' This module contains OptionsFrame class used for displaying and modifying
    some of the parameters.

    Attributes:

        COUNT_TO_NAME_RADIO_BTN (dict of {(str, int) to str}): dictionary that
            maps parameter name and count to a valid value. This structure is
            used to identify parameter value used for display
            depending on parameter name and count. Count is simply a value of
            IntVar used in Radiobutton

    Warning:
        COUNT_TO_NAME_RADIO_BTN and all methods that use it must be modified if
        COUNT_TO_NAME_RADIO_BTN ever changes.
'''

from tkinter import W, N, DISABLED, NORMAL, StringVar, IntVar
from tkinter import Entry, END
from tkinter.ttk import LabelFrame, Label, Checkbutton, Radiobutton
from tkinter.ttk import Combobox, Frame
from tkinter.messagebox import showwarning

from pyDEA.core.utils.dea_utils import XPAD_VALUE, YPAD_VALUE

COUNT_TO_NAME_RADIO_BTN = {('RETURN_TO_SCALE', 1): 'VRS',
                           ('RETURN_TO_SCALE', 2): 'CRS',
                           ('RETURN_TO_SCALE', 3): 'both',
                           ('ORIENTATION', 1): 'input',
                           ('ORIENTATION', 2): 'output',
                           ('ORIENTATION', 3): 'both',
                           ('DEA_FORM', 1): 'env', ('DEA_FORM', 2): 'multi'}


class OptionsFrame(LabelFrame):
    ''' This class creates Checkbuttons and Radiobuttons for displaying
        and modifying some of the parameters.

        Attributes:
            params (Parameters): object with all parameters. Some of the
                parameter values are modified in this class.
            current_categories (list of str): list of categories.
            input_categories_frame (CategoriesCheckBox): frame with input
                categories. It is needed in this class to read what
                categories are input.
            output_categories_frame (CategoriesCheckBox): frame with
                output categories. It is needed in this class to read what
                categories are output.
            categorical_box (Combobox): Combobox for choosing categorical
                category.
            combobox_text_var (StringVar): text variable of categorical_box.
            options (dict of str to IntVar): dictionary that stores IntVars
                of Radiobuttons and Checkbuttons.

                Example:
                    >>> options = {"RETURN_TO_SCALE": IntVar(),
                    "ORIENTATION": IntVar()}

            multi_tol_strvar (StringVar): StringVar object that stores
                tolerance of multiplier model.
            max_slack_box (Checkbutton): Checkbutton for the option "Two phase".

        Args:
            parent (Tk object): parent of this widget.
            params (Parameters): object with all parameters. Some of
                the parameter values are modified in this class.
            current_categories (list of str): list of categories.
            input_categories_frame (CategoriesCheckBox): frame with input
                categories. It is needed in this class to read what
                categories are input.
            output_categories_frame (CategoriesCheckBox): frame with output
                categories. It is needed in this class to read what
                categories are output.
            name (str, optional): name of the LabelFrame that this class
                represents, defaults to Options.
    '''
    def __init__(self, parent, params, current_categories,
                 input_categories_frame,
                 output_categories_frame, name='Options', *args, **kw):
        super().__init__(parent, text=name, *args, **kw)
        self.params = params
        self.current_categories = current_categories
        self.input_categories_frame = input_categories_frame
        self.output_categories_frame = output_categories_frame
        self.categorical_box = None
        self.combobox_text_var = StringVar()
        self.combobox_text_var.trace('w', self.on_categorical_box_change)
        self.options = dict()
        self.multi_tol_strvar = StringVar()
        self.multi_tol_strvar.trace('w', self.on_multi_tol_change)
        self.max_slack_box = None
        self.create_widgets()

    def create_widgets(self):
        ''' Creates all widgets.
        '''
        rts_lbl = Label(self, text='Return to scale:')
        rts_lbl.grid(row=0, column=0, padx=XPAD_VALUE, pady=YPAD_VALUE,
                     sticky=W)
        self._create_frame_with_radio_btns(self, 'RETURN_TO_SCALE',
                                           ['VRS', 'CRS'],
                                           row_index=1, column_index=0)

        orientation_lbl = Label(self, text='Orientation:')
        orientation_lbl.grid(row=0, column=1, sticky=W, padx=XPAD_VALUE,
                             pady=YPAD_VALUE)
        self._create_frame_with_radio_btns(self, 'ORIENTATION',
                                           ['Input', 'Output'],
                                           row_index=1, column_index=1)

        model_lbl = Label(self, text='Model:')
        model_lbl.grid(row=0, column=2, padx=XPAD_VALUE, pady=YPAD_VALUE,
                       sticky=W)
        self._create_frame_with_radio_btns(self, 'DEA_FORM',
                                           ['Envelopment', 'Multiplier'],
                                           row_index=1, column_index=2,
                                           add_both=False)

        other_lbl = Label(self, text='Others:')
        other_lbl.grid(row=0, column=3, sticky=W, padx=XPAD_VALUE)

        max_slacks = IntVar()
        self.options['MAXIMIZE_SLACKS'] = max_slacks
        frame_other_options = Frame(self)
        self.max_slack_box = max_slacks_check_btn = Checkbutton(
            frame_other_options, text='Two phase', variable=max_slacks,
            command=(lambda: self.on_check_box_click(
                max_slacks, 'MAXIMIZE_SLACKS')))
        max_slacks_check_btn.grid(row=1, column=0, sticky=W)
        super_efficiency = IntVar()
        self.options['USE_SUPER_EFFICIENCY'] = super_efficiency
        super_efficiency_check_btn = Checkbutton(frame_other_options,
                                                 text='Super efficiency',
                                                 variable=super_efficiency,
                                                 command=(
                                                 lambda: self.on_check_box_click(
                                                 super_efficiency,
                                                 'USE_SUPER_EFFICIENCY')))
        super_efficiency_check_btn.grid(row=2, column=0, sticky=W)
        peel_the_onion = IntVar()
        self.options['PEEL_THE_ONION'] = peel_the_onion
        peel_the_onion_check_btn = Checkbutton(
            frame_other_options, text='Peel the onion', variable=peel_the_onion,
            command=(lambda: self.on_check_box_click(peel_the_onion,
                     'PEEL_THE_ONION')))
        peel_the_onion_check_btn.grid(row=3, column=0, sticky=W)
        frame_other_options.grid(row=1, column=3, padx=XPAD_VALUE,
                                 pady=YPAD_VALUE, sticky=W)

        frame_for_toleramce = Frame(self)
        tolerance_lbl = Label(frame_for_toleramce,
                              text='Multiplier model tolerance:')
        tolerance_lbl.grid(row=0, column=0, padx=XPAD_VALUE, pady=YPAD_VALUE,
                           sticky=W)
        tolerance_ent = Entry(frame_for_toleramce, width=5,
                              textvariable=self.multi_tol_strvar)
        tolerance_ent.insert(END, 0)
        tolerance_ent.grid(row=0, column=1, sticky=W, padx=XPAD_VALUE)
        categorical_lbl = Label(frame_for_toleramce, text='Categorical:')
        categorical_lbl.grid(row=1, column=0, padx=XPAD_VALUE,
                             pady=YPAD_VALUE, sticky=W)
        self.categorical_box = categorical_box = Combobox(
            frame_for_toleramce, textvariable=self.combobox_text_var,
            exportselection=0, state="readonly",
            width=20, values=(''),
            postcommand=self.change_categorical_box)
        categorical_box.grid(row=1, column=1, padx=XPAD_VALUE,
                             pady=YPAD_VALUE, sticky=W)
        frame_for_toleramce.grid(row=5, column=0, sticky=W, padx=XPAD_VALUE,
                                 pady=YPAD_VALUE, columnspan=4)

    def _create_frame_with_radio_btns(self, parent, name, text, row_index,
                                      column_index, add_both=True):
        ''' Creates frame with one set of Radiobuttons.

            Args:
                parent (Tk object): parent of the frame.
                name (str): name of the parameter that will a key in options
                    dictionary.
                text (list of str): list with two parameter values that should
                    be displayed next to the first two Radiobuttons.
                row_index (int): index of the row where the frame should
                    be placed using grid method.
                column_index (int): index of the column where the frame
                    should be placed using grid method.
                add_both (bool, optional): True if the third Radiobutton
                    with text "both" must be displayed, False otherwise,
                    defaults to True.
        '''
        assert len(text) == 2
        v = IntVar()
        self.options[name] = v
        self.options[name].trace(
            'w', (lambda *args: self.radio_btn_change(name)))
        frame_with_radio_btns = Frame(parent)
        first_option = Radiobutton(frame_with_radio_btns,
                                   text=text[0], variable=v, value=1)
        first_option.grid(row=0, column=0, sticky=W+N, padx=2)
        v.set(1)
        second_option = Radiobutton(frame_with_radio_btns,
                                    text=text[1], variable=v, value=2)
        second_option.grid(row=1, column=0, sticky=W+N, padx=2)
        if add_both:
            both = Radiobutton(frame_with_radio_btns, text='Both',
                               variable=v, value=3)
            both.grid(row=3, column=0, sticky=W+N, padx=2)
        frame_with_radio_btns.grid(row=row_index, column=column_index,
                                   padx=1, pady=5, sticky=W+N)

    def radio_btn_change(self, name, *args):
        ''' Actions that happen when user clicks on a Radiobutton.
            Changes the corresponding parameter values and options.

            Args:
                name (str): name of the parameter that is a key in
                    options dictionary.
                *args: are provided by IntVar trace method and are
                    ignored in this method.
        '''
        count = self.options[name].get()
        self.params.update_parameter(name, COUNT_TO_NAME_RADIO_BTN[name, count])
        dea_form = COUNT_TO_NAME_RADIO_BTN[name, count]
        if self.max_slack_box:  # on creation it is None
            if dea_form == 'multi':
                # disable max slacks
                self.max_slack_box.config(state=DISABLED)
                self.params.update_parameter('MAXIMIZE_SLACKS', '')
            elif dea_form == 'env':
                self.max_slack_box.config(state=NORMAL)
                if self.options['MAXIMIZE_SLACKS'].get() == 1:
                    self.params.update_parameter('MAXIMIZE_SLACKS', 'yes')

    def change_categorical_box(self):
        ''' Updates categories that can be chosen as categorical category
            when the user clicks on the Combobox.
        '''
        values = [category for category in self.current_categories if
                  category and category not in
                  self.input_categories_frame.category_objects.keys() and
                  category not in
                  self.output_categories_frame.category_objects.keys()]
        values.append('')
        self.categorical_box.config(values=values)

    def on_categorical_box_change(self, *args):
        ''' Updates value of the CATEGORICAL_CATEGORY in parameters.
            This method is called when the user clicks on the Combobox and
            chooses one item from the drop-down list.

            Args:
                *args: are provided by the StringVar trace method and are
                    ignored in this method.
        '''
        categorical_var = self.combobox_text_var.get()
        self.params.update_parameter('CATEGORICAL_CATEGORY', categorical_var)

    def set_params_values(self):
        ''' Reads all parameter values from the parameter object (params)
            and sets all widgets
            and options to these read values. Might display warnings if
            invalid values are stored in parameter object.
        '''
        self.set_radio_btns()
        self.set_check_btns()
        self.change_categorical_box()
        self.set_categorical_box(self.params.get_parameter_value(
            'CATEGORICAL_CATEGORY'))
        self.set_multi_tol()

    def set_radio_btns(self):
        ''' Goes through all Radiobuttons and changes their values
            according to the values stored in parameter object.
            Might display warnings.
        '''
        self.set_one_radio_btn('RETURN_TO_SCALE', ['VRS', 'CRS', 'both'])
        self.set_one_radio_btn('ORIENTATION', ['input', 'output', 'both'])
        self.set_one_radio_btn('DEA_FORM', ['env', 'multi'])

    def set_one_radio_btn(self, param_name, valid_values):
        ''' Sets value of a given set of Radiobuttons according to its value
            stored in parameter object if this value is valid.
            Might display warnings.

            Args:
                param_name (str): name of parameter whose value must be changed.
                valid_values (list of str): list of valid values that this
                    parameter might take.
        '''
        param_value = self.params.get_parameter_value(param_name)
        for count, value in enumerate(valid_values):
            if param_value == value:
                self.options[param_name].set(count + 1)
                return
        self._show_warning(param_name)
        self.options[param_name].set(1)

    def _show_warning(self, param_name):
        ''' Displays a warning saying that a value of a given parameter
            is not valid.

            Args:
                param_name (str): name of the parameter.
        '''
        showwarning('Warning', 'Parameter <{0}> does not have valid values.'
                    ' It will be set to default'.
                    format(param_name))

    def set_check_btns(self):
        ''' Goes through all Checkbuttons and changes their values
            according to the values
            stored in parameter object. Might display warnings.
        '''
        self.set_one_check_btn('MAXIMIZE_SLACKS')
        self.set_one_check_btn('PEEL_THE_ONION')
        self.set_one_check_btn('USE_SUPER_EFFICIENCY')

    def set_one_check_btn(self, param_name):
        ''' Sets value of a given set of Checkbutton according to its value
            stored in parameter object if this value is valid. Might
            display warnings.

            Args:
                param_name (str): name of parameter whose value must be changed.
        '''
        param_value = self.params.get_parameter_value(param_name)
        if param_value:
            self.options[param_name].set(1)

    def set_categorical_box(self, categorical_param):
        ''' Sets the value of Combobox with categorical category according
            to a given value
            if this value is in the list of values of this Combobox.
            If the given value
            is not in the list of values, a warning is displayed.

            Args:
                categorical_param (str): value of the categorical category.
        '''
        if categorical_param in self.categorical_box.cget('values'):
            self.combobox_text_var.set(categorical_param)
        else:
            self._show_warning_combobox(categorical_param)

    def _show_warning_combobox(self, categorical_param):
        ''' Displays a warning saying that a value of a given parameter is
            not a valid categorical category.

            Args:
                categorical_param (str): name of the categorical category.
        '''
        showwarning('Warning', 'Category: <{0}> cannot be chosen as a '
                    'categorical variable'.
                    format(categorical_param))

    def set_multi_tol(self):
        ''' Sets the value of Entry with multiplier model tolerance
            according to a given value
            if this value is valid (non-negative float). If the given value
            is invalid, a warning is displayed.
        '''
        tol_str = self.params.get_parameter_value('MULTIPLIER_MODEL_TOLERANCE')
        try:
            tol = float(tol_str)
            if (tol < 0):
                self._show_multi_tol_warning(tol_str)
                self.multi_tol_strvar.set('0')
            else:
                self.multi_tol_strvar.set(tol_str)
        except ValueError:
            self._show_multi_tol_warning(tol_str)
            self.multi_tol_strvar.set('0')

    def _show_multi_tol_warning(self, tol_str):
        ''' Displays a warning saying that a value of a multiplier model
            tolerance is invalid.

            Args:
                tol_str (str): value of the multiplier model tolerance.
        '''
        showwarning('Warning', 'Value: <{0}> is not valid as a multiplier'
                    ' model tolerance'.
                    format(tol_str))

    def on_multi_tol_change(self, *args):
        ''' Updates parameter MULTIPLIER_MODEL_TOLERANCE in the parameter
            object when the user
            modifies the content of the Entry widget that stores
            multiplier model tolerance.

            Args:
                *args: are provided by the StringVar trace method and are
                    ignored in this method.
        '''
        # this parameter will be validated before run
        tol_str = self.multi_tol_strvar.get()
        self.params.update_parameter('MULTIPLIER_MODEL_TOLERANCE', tol_str)

    def on_check_box_click(self, var, name):
        ''' Updates parameter specified by the Checkbutton in the parameter
            object when the user clicks on the Checkbutton.

            Args:
                var (IntVar): IntVar of the Checkbutton.
                name (str): name of the parameter that is the key in options
                    dictionary.
        '''
        if var.get() == 1:
            self.params.update_parameter(name, 'yes')
        else:
            self.params.update_parameter(name, '')
