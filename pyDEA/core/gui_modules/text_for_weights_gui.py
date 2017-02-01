''' This module contains TextForWeights class which is a text widget
    used for displaying and editing weight restrictions.

    Attributes:
        TEXT_WIDTH_VAL (int): width of Text widget.
        TEXT_HEIGHT_VAL (int): heigth of Text widget.
'''


from tkinter import Text, NONE, N, W, E, S, HORIZONTAL, END, TclError
from tkinter import StringVar, LEFT
from tkinter.ttk import Frame, Label, Scrollbar

from pyDEA.core.utils.dea_utils import create_bounds, contraint_is_price_ratio_type

TEXT_WIDTH_VAL = 50
TEXT_HEIGHT_VAL = 10


class TextForWeights(Frame):
    ''' Implements text widget used for displaying and editing weight
        restrictions.

        Attributes:
            parent (Tk object): parent of this widget.
            weight_name (str): text describing type of weight restrictions,
                e.g. absolute, virtual, etc.
            examples (str): string with an example of usage of this
                type of weight restrictions, e.g. I1 <= 2.
            current_categories (list of str): list of current categories.
            params (Parameters): parameters.
            param_name (str): parameter name that corresponds to this type
                of weight restrictions, e.g. ABS_WEIGHT_RESTRICTIONS.
            text (Text): text widget used for displaying weight restrictions.
            error_tag_exists (bool): if set to True, means that there are
                invalid weight restrictions, False otherwise.
            errors_strvar (StringVar): is used for storing and displaying
                error messages for invalid weight restrictions.
            is_price_ratio (bool): if True price ratio constraints are 
                expected to be entered, if False other constraint types are 
                expected to be entered. Defaults to False.

        Args:
            parent (Tk object): parent of this widget.
            weight_name (str): text describing type of weight restrictions,
                e.g. absolute, virtual, etc.
            examples (str): string with an example of usage of this
                type of weight restrictions, e.g. I1 <= 2.
            current_categories (list of str): list of current categories.
            params (Parameters): parameters.
            param_name (str): parameter name that corresponds to this type
                of weight restrictions, e.g. ABS_WEIGHT_RESTRICTIONS.
            is_price_ratio (bool): if True price ratio constraints are 
                expected to be entered, if False other constraint types are 
                expected to be entered. Defaults to False.
    '''
    def __init__(self, parent, weight_name, examples,
                 current_categories, params, param_name,
                 is_price_ratio_constraint = False, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.parent = parent
        self.examples = examples
        self.current_categories = current_categories
        self.params = params
        self.param_name = param_name
        self.text = None
        self.error_tag_exists = False
        self.errors_strvar = StringVar()
        self.weight_name = weight_name
        self.is_price_ratio_constraint = is_price_ratio_constraint
        self.create_widgets(weight_name)

    def create_widgets(self, weight_name):
        ''' Creates all widgets.
        '''
        constraints_lbl = Label(
            self, text='Enter {0} weight restrictions:'.format(
                weight_name))
        constraints_lbl.grid(padx=10, pady=2, sticky=N+W)
        examples_lbl = Label(self, text='e.g. {0}'.format(self.examples))
        examples_lbl.grid(row=1, column=0, padx=10, pady=5, sticky=N+W)

        errors_lbl = Label(self, textvariable=self.errors_strvar, 
                           foreground='red', anchor=W, justify=LEFT, 
                           wraplength=80)
        errors_lbl.grid(row=2, column=2, sticky=N+W, padx=5, pady=5)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(self, orient=HORIZONTAL)
        xscrollbar.grid(row=3, column=0, sticky=E+W)

        yscrollbar = Scrollbar(self)
        yscrollbar.grid(row=2, column=1, sticky=N+S)

        self.text = Text(self, wrap=NONE, width=TEXT_WIDTH_VAL,
                         height=TEXT_HEIGHT_VAL,
                         xscrollcommand=xscrollbar.set,
                         yscrollcommand=yscrollbar.set)

        self.text.grid(row=2, column=0, sticky=N+S+E+W)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

    def delete_weights(self):
        ''' Removes all weight restrictions.
        '''
        self.text.delete(1.0, END)
        self.error_tag_exists = False

    def insert_weight(self, weight):
        ''' Add a given weight restriction in the end of the
            text widget.

            Args:
                weight (str): string that describes a given weight
                    restriction.
        '''
        # we assume that inserted weight is always correct
        self.text.insert(END, weight + '\n')

    def validate_weights(self):
        ''' Checks if all weight restrictions are valid.

            Returns:
                bool: True if all weight restrictions are valid,
                    False otherwise.
        '''
        self.text.config(foreground='black')
        if self.error_tag_exists:
            try:
                self.text.tag_remove('error', 'error.first', 'error.last')
            except TclError:
                # there is no error tag
                pass

        self.error_tag_exists = False
        self.errors_strvar.set('')
        errors = []
        all_constraints = []
        for count, line in enumerate(self.text.get('1.0', 'end-1c').splitlines()):
            # Iterate lines
            if line:
                weight_as_list = []
                weight_as_list.append(line)
                try:
                    bounds = create_bounds(weight_as_list, self.current_categories)
                    assert len(bounds) == 1
                    key, value = bounds.popitem()
                    is_price_ratio = contraint_is_price_ratio_type(key)
                    if self.is_price_ratio_constraint and not is_price_ratio:
                        raise ValueError('Constraint {0} is not a price ratio constraint'.
                            format(line))
                    if not self.is_price_ratio_constraint and is_price_ratio:
                        raise ValueError('Constraint {0} is a price ratio constraint.'
                            ' Use {1} weight restriction type constraint instead.'.
                            format(line, self.weight_name))

                except ValueError as err:
                    self.text.tag_add('error', '%d.0' % (count + 1),
                                      '%d.end' % (count + 1))
                    self.error_tag_exists = True
                    errors.append('* ' + str(err) + '\n')
                else:
                    # combine correct lines for parameters
                    all_constraints.append(line)
                    errors.append('\n')

        if self.error_tag_exists:
            self.text.tag_config('error', foreground='red')

        constraints = '; '.join(all_constraints)
        self.params.update_parameter(self.param_name, constraints)
        if self.error_tag_exists:
            self.errors_strvar.set(self.get_all_errors(errors))
        if constraints:
            return True
        return False

    def get_all_errors(self, error_list):
        ''' Returns given list of errors as one string.

            Args:
                error_list (list of str): list of strings to concatenate.

            Returns:
                str: concatenated string.
        '''
        if len(error_list) == 0:
            return ''
        return ''.join(error_list)
