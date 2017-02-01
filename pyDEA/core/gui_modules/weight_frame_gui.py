''' This module contains class WeightFrame that is used as a tab in
    parameters frame to edit and display weights.
'''
from tkinter.ttk import Button, Frame, LabelFrame
from tkinter import N, W, S, E

from pyDEA.core.utils.dea_utils import create_bounds
from pyDEA.core.gui_modules.text_for_weights_gui import TextForWeights
from pyDEA.core.gui_modules.scrollable_frame_gui import VerticalScrolledFrame


class WeightFrame(Frame):
    ''' This class represents weights editor. It allows to display, modify
        and validate weights.

        Attributes:
            parent (Tk object): parent of this widget.
            current_categories (list of str): list of current categories,
                this list is not modified by this class.
            params (Parameters): Parameters object with all parameter values.

                Note:
                    This class does not change values in Parameters object
                    until the weight
                    restrictions are validated, see on_validate_weights().

            weights_status_str (StringVar): StringVar object that is used
                to show an error if it occurred after validating weights.
            abs_weights (TextForWeights): text widget for displaying and editing
                absolute weight restrictions.
            virtual_weights (TextForWeights): text widget for displaying and
                editing virtual weight restrictions.
            price_ratio_weights (TextForWeights): text widget for displaying and
                editing price-ratio weight restrictions.

        Args:
            parent (Tk object): parent of this widget.
            current_categories (list of str): list of current categories,
                this list is not modified by this class.
            params (Parameters): Parameters object with all parameter values
            weights_status_str (StringVar): StringVar object that is used to
                show an error if it occurred after validating weights.
    '''

    def __init__(self, parent, current_categories, params, weights_status_str,
                 *args, **kw):
        super().__init__(parent, *args, **kw)
        self.parent = parent
        self.current_categories = current_categories
        self.params = params
        self.weights_status_str = weights_status_str
        self.abs_weights = None
        self.virtual_weights = None
        self.price_ratio_weights = None
        self.create_widgets()

    def create_widgets(self):
        ''' Creates all widgets.
        '''
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        validate_btn = Button(self, text='Validate weight restrictions',
                              command=self.on_validate_weights)
        validate_btn.grid(row=0, column=0, padx=10, pady=5, sticky=N+W)

        panel = LabelFrame(self, text='Weight restrictions')
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=1)
        panel.grid(row=1, column=0,
                   padx=5, pady=5, sticky=E+W+S+N)

        weight_tab_main = VerticalScrolledFrame(panel)
        weight_tab_main.grid(row=0, column=0, sticky=E+W+S+N)
        weights_tab = weight_tab_main.interior

        self.abs_weights = TextForWeights(weights_tab, 'absolute',
                                          'Input1 <= 0.02',
                                          self.current_categories, self.params,
                                          'ABS_WEIGHT_RESTRICTIONS')
        self.abs_weights.grid(row=0, column=0, padx=10, pady=5, sticky=N+W)
        self.virtual_weights = TextForWeights(weights_tab, 'virtual',
                                              'Input1 >= 0.34',
                                              self.current_categories,
                                              self.params,
                                              'VIRTUAL_WEIGHT_RESTRICTIONS')
        self.virtual_weights.grid(row=1, column=0, padx=10, pady=5, sticky=N+W)
        self.price_ratio_weights = TextForWeights(weights_tab, 'price ratio',
                                                  'Input1/Input2 <= 5',
                                                  self.current_categories,
                                                  self.params,
                                                  'PRICE_RATIO_RESTRICTIONS',
                                                  True)
        self.price_ratio_weights.grid(row=2, column=0, padx=10, pady=5,
                                      sticky=N+W)

    def add_weights(self):
        ''' Adds weight restrictions stored in params to the appropriate
            text widgets if such weight restrictions can be parsed and
            contain categories that are also present in current_categories.
        '''
        self.remove_all_weights()
        self._add_given_weights(self.abs_weights, 'ABS_WEIGHT_RESTRICTIONS')
        self._add_given_weights(self.virtual_weights,
                                'VIRTUAL_WEIGHT_RESTRICTIONS')
        self._add_given_weights(self.price_ratio_weights,
                                'PRICE_RATIO_RESTRICTIONS')

    def _add_given_weights(self, text_widget, weights_name):
        ''' Adds given weight restrictions to a given text widget.

            Args:
                text_widget (TextForWeights): text widget where weight
                    restrictions will be added.
                weights_name (str): name of the parameter that stores weight
                    restrictions in params.

            Example:
                If currently parameters contain absolute weight
                restrictions "I1 >= 0.1", then we can add this constraint to the
                text widget as follows:
                >>> self._add_given_weights(self.abs_weights,
                    'ABS_WEIGHT_RESTRICTIONS')
        '''
        weights = self.params.get_set_of_parameters(weights_name)
        weights_were_added = False
        if weights:
            for weight in weights:
                weight_as_list = []
                weight_as_list.append(weight)
                try:
                    create_bounds(weight_as_list, self.current_categories)
                except ValueError:
                    pass  # everything that we cannot parse is ignored
                else:
                    text_widget.insert_weight(weight)
                    weights_were_added = True
        if weights_were_added:
            self.parent.change_weight_tab_name('Weights editor*')

    def remove_all_weights(self):
        ''' Removes all weight restrictions from all text widgets.

            Note:
                Parameters object is not affected by this. All weight
                restrictions will still be there. Parameters are updated
                only when they are validated,
                i.e. when the user presses validate weights button or run
                button.
        '''
        self.parent.change_weight_tab_name('Weights editor')
        self.weights_status_str.set('')
        self.abs_weights.delete_weights()
        self.virtual_weights.delete_weights()
        self.price_ratio_weights.delete_weights()

    def on_validate_weights(self):
        ''' Validates weights of all text widgets and displays an error if
            some of the weights are invalid.

            Note:
                Parameters object is modified by this method.
        '''
        abs_weights_present = self.abs_weights.validate_weights()
        virtual_weights_present = self.virtual_weights.validate_weights()
        price_ratio_weights_present = self.price_ratio_weights.validate_weights()
        if (self.abs_weights.error_tag_exists or
                self.virtual_weights.error_tag_exists or
                self.price_ratio_weights.error_tag_exists):
            self.weights_status_str.set(
                'Some of the weight restrictions cannot be parsed. \n'
                'For error details, see Weights editor tab.')
        else:
            self.weights_status_str.set('')
        if (abs_weights_present or virtual_weights_present or
                price_ratio_weights_present):
            self.parent.change_weight_tab_name('Weights editor*')
        else:
            self.parent.change_weight_tab_name('Weights editor')
