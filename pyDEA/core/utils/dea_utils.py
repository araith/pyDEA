''' This module contains various utility functions and constants.

    Attributes:

        FILE_TYPES (list of tuple of str, str): list of supported
            input file parameters.
        SOLUTION_XLSX_FILE (list of tuple of str, str): list of
            supported solution file formats (xlsx).
        TEXT_FOR_PANEL (str): text displayed in the label on the data tab before
            path to input data file.
        TEXT_FOR_FILE_LBL (str): text displayed in the label on the solution tab
            before path to input data file.
        ZERO_TOLERANCE (double): is used to check if a value is non-zero. All
            values greater than ZERO_TOLERANCE are considered to be strictly
            positive.
        VALID_COEFF (int): constant used to indicate valid data entry.
        WARNING_COEFF (int): constant used to indicate valid data entry that
            is zero.
        NOT_VALID_COEFF (int): constant used to indicate invalid data entry.
        EMPTY_COEFF (int): constant used to indicate empty data entry.
        CELL_DESTROY (int): constant used to indicate that cell of a table was
            destroyed.
        CHANGE_CATEGORY_NAME (int): constant used to indicate that name of the
            category was changed.
        INPUT_OBSERVER (int): constant used to indicate the observer for input
            categories.
        OUTPUT_OBSERVER (int): constant used to indicate the observer for
            output categories.
        XPAD_VALUE (int): horizontal padding.
        YPAD_VALUE (int): vertical padding.
        bg_color (hex): background colour for all widgets.
        TMP_FOLDER (str): name of the folder where all pickled files will
            be stored and then removed.
'''

from tkinter import StringVar
from tkinter import ALL
import os
import pkg_resources
import logging
from logging.config import fileConfig

LOG_FILE = 'logging_config.ini'
PACKAGE = 'pyDEA'

FILE_TYPES = [('Excel (xlsx)', '*.xlsx'),
              ('Text CSV', '*.csv')]
SOLUTION_XLSX_FILE = [('Excel (xlsx)', '*.xlsx')]
TEXT_FOR_PANEL = 'File: '
TEXT_FOR_FILE_LBL = 'Data from file: '

ZERO_TOLERANCE = 1e-10

VALID_COEFF = 1
WARNING_COEFF = 0
NOT_VALID_COEFF = -1
EMPTY_COEFF = -2
CELL_DESTROY = -3
CHANGE_CATEGORY_NAME = -4

INPUT_OBSERVER = 1
OUTPUT_OBSERVER = 2

XPAD_VALUE = 10
YPAD_VALUE = 5

bg_color = '#E8E9FA'

TMP_FOLDER = 'tmp'


class ObserverStringVar(StringVar):
    ''' This class extends StringVar and adds two data structures to it for
        storing input and output categories.

        Attributes:
            output_categories (list of str): list with output categories
            input_categories (list of str): list with input categories
    '''
    def __init__(self, *args, **kw):
        StringVar.__init__(self, *args, **kw)
        self.output_categories = []
        self.input_categories = []


def get_logger():
    ''' Gets a logger with all configuration specified in file ini-file.

        Returns:
            logger: configured logger
    '''
    logfile = pkg_resources.resource_filename(PACKAGE, LOG_FILE)
    fileConfig(logfile)
    return logging.getLogger()


def change_to_unique_name_if_needed(file_name):
    ''' Given a file name, this function checks if there is a file with
        such a name, and generates a new unique name if the file exists.

        Args:
            file_name (str): file name

        Returns:
            str: if given file does not exist, this file name is returned.
                If given file exists, the unique incremented file name is
                returned.
    '''
    if os.path.exists(file_name):
        i = 1
        base_name, file_extension = os.path.splitext(file_name)
        file_name = '{0}_{1}{2}'.format(base_name, i, file_extension)
        while os.path.exists(file_name):
            i += 1
            file_name = '{0}_{1}{2}'.format(base_name, i, file_extension)
    return file_name


def clean_up_pickled_files():
    ''' Removes mps-files from current folder and p-files from temporary folder.
    '''
    if os.path.exists(TMP_FOLDER):
        filelist = [f for f in os.listdir(TMP_FOLDER) if f.endswith('.p')]
        for f in filelist:
            os.remove(os.path.join(TMP_FOLDER, f))
    # remove mps file if any
    filelist = [f for f in os.listdir('.') if f.endswith('.mps')]
    for f in filelist:
        os.remove(f)


def format_data(data):
    ''' Formats floating point number to 6 digits.

        Args:
            data (double): data that must be formatted

        Returns:
            str: formatted data.

        Example:
            >>> format_data(1.222222222222222)
            >>> '1.222222'
            >>> format_data('str')
            >>> 'str'
            >>> format_data(0.123456789)
            >>> '0.123457'
            >>> format_data('0.05')
            >>> '0.050000'
    '''
    try:
        float_data = float(data)
    except ValueError:
        return str(data)
    else:
        return '%.6f' % float_data


def auto_name_if_needed(params, output_format, new_output_dir=''):
    ''' Creates an automatic name for solution file based on current
        parameter values, if OUTPUT_FILE is empty or set to auto.

        Args:
            params (Parameters): parameters
            output_format (str): output format of solution file that
                should be used. Allowed values: xlsx, csv
            new_output_dir (str, optional): directory where solution must be
                stored. It should be specified if it is different from current
                folder. Defaults to empty string.

        Returns:
            str: automatic name if OUTPUT_FILE is empty or set to auto in
                parameters.

        Raises:
            ValueError: if output_format is not 'xlsx' or 'csv'.
    '''
    output_name = params.get_parameter_value('OUTPUT_FILE')
    if output_name.lower() == 'auto' or output_name.strip() == '':
        input_file_name = params.get_parameter_value('DATA_FILE')
        input_base_name = os.path.basename(input_file_name)
        input_base_name, ext_tmp = os.path.splitext(input_base_name)
        ext = output_format
        if ext not in ['xlsx', 'csv']:
            raise ValueError('{0} is not supported output format'.format(ext))
        output_name = os.path.join(new_output_dir,
                                   input_base_name + '_result.' + ext)
        output_name = change_to_unique_name_if_needed(output_name)
    return output_name


def calculate_nb_pages(nb_data_rows, nb_table_rows):
    ''' Calculates number of pages given number of data rows and number of rows
        in the table.

        Note:
            first row is reserved for categories.

        Args:
            nb_data_rows (int): number of data rows.

                Warning:
                    It must be a positive number. Otherwise the function
                    will return incorrect value.

            nb_table_rows (int): number of rows in the table.

                Warning:
                    It must be a positive number. Otherwise the function
                    will return incorrect value.

        Returns:
            int: number of pages

        Example:
            >>> calculate_nb_pages(100, 10)
            >>> 12
            >>> calculate_nb_pages(25, 20)
            >>> 2
            >>> calculate_nb_pages(0, 20)
            >>> 1
            >>> calculate_nb_pages(10, 25):
            >>> 1

    '''
    if nb_table_rows:
        base = int(nb_data_rows / (nb_table_rows - 1))
        if nb_data_rows % (nb_table_rows - 1) != 0:
            base += 1
        return max(base, 1)
    return 0


def calculate_start_row_index(curr_page, nb_table_rows):
    ''' Calculates row index of data that will be displayed given
        current page and number of rows in the table.

        Note:
            The first row of the table is reserved for displaying categories.

        Args:
            curr_page (int): current page number. Pages start from 1.
            nb_table_rows (int): number of rows in the table.

        Returns:
            int: data row index
    '''
    if (curr_page == 0):
        return 0
    return (curr_page - 1) * (nb_table_rows - 1)


def validate_category_name(name, category_index, current_categories):
    ''' Checks if given category name is valid. Name is valid if it is not
        a number, if it does not contain semicolon and if it is not duplicated.

        Args:
            name (str): category name.
            category_index (int): index of this category in the list of
                current categories.
            current_categories (list of str): list of current categories.

        Returns:
            str: given category name if this name is valid, empty
                string otherwise.

        Example:
            >>> validate_category_name('I1n', 0, ['I1n', 'I2', 'O2])
            >>> 'I1n'
            >>> validate_category_name('I1n;', 0, ['I1n;', 'I2', 'O2])
            >>> ''
            >>> validate_category_name('1.2', 0, ['1.2', 'I2', 'O2])
            >>> ''
            >>> validate_category_name('I1n', 0, ['I1n', 'I1n', 'O2])
            >>> ''
    '''
    try:
        float(name)
    except ValueError:
        if ';' in name:
            return ''
        for index, category in enumerate(current_categories):
            if index != category_index and category == name:
                return ''
        return name
    else:
        return ''


def on_canvas_resize(canvas):
    ''' This function updates scroll region of the canvas.
        It should be called on canvas resize.

        Args:
            canvas (Canvas): canvas
    '''
    canvas.update_idletasks()
    yscroll = 0
    xscroll = 0
    if canvas.bbox(ALL)[2] > canvas.winfo_width():
        yscroll = canvas.bbox(ALL)[2]
    if canvas.bbox(ALL)[3] > canvas.winfo_height():
        xscroll = canvas.bbox(ALL)[3]
    canvas['scrollregion'] = (0, 0, yscroll, xscroll)


def center_window(widget, width=None, height=None):
    ''' Centres widget in the middle of the screen.

        Args:
            widget (Tk object): widget that needs to be centred.
            width (int, optional): width of the widget that should be used.
                If not specified, widget width is used.
            height (int, optional): height of the widget that should be used.
                If not specified, widget width is used.
    '''
    widget.withdraw()
    widget.update_idletasks()
    if width is None:
        width = widget.winfo_reqwidth()

    if height is None:
        height = widget.winfo_reqheight()

    sw = widget.winfo_screenwidth()
    sh = widget.winfo_screenheight()

    x = (sw - width)/2
    y = (sh - height)/2
    widget.geometry('%dx%d+%d+%d' % (width, height, x, y))
    widget.deiconify()


def create_params_str(params):
    ''' Creates string from values of ORIENTATION and RETURN_TO_SCALE
        specified in parameters.

        Args:
            params (Parameters): parameters.
    '''
    return '{0} orientation, {1}'.format(
        params.get_parameter_value('ORIENTATION'),
        params.get_parameter_value('RETURN_TO_SCALE'))


def is_valid_coeff(coeff):
    ''' Checks if given coefficient is valid. Valid coefficient is positive
        floating point or integer number.

        Args:
            coeff (double): data coefficient.

        Returns:
            int: 1, if coefficient is valid, 0 if coefficient is zero,
                -1, if coefficient is invalid.
    '''
    try:
        coeff = float(coeff)
        if coeff < 0:
            return NOT_VALID_COEFF
        elif coeff == 0:
            return WARNING_COEFF
        else:
            return VALID_COEFF
    except ValueError:
        return NOT_VALID_COEFF


def is_efficient(efficiency_score, lambda_variable):
    ''' Checks if dmu with given efficiency score and value of
        lambda variable is efficient.

        Args:
            efficiency_score (double): efficiency spyDEA.core.
            lambda_variable (double): value of lambda variable corresponding
                to DMU under consideration.

        Returns:
            bool: True if DMU is efficient, False otherwise.

        Example:
            >>> is_efficient(1, 1)
            True
            >>> is_efficient(0.5, 0)
            False
            >>> is_efficient(0.9999999, 1)
            True
            >>> is_efficient(1.0000001, 1)
            True

    '''
    if efficiency_score == 1:
        return True
    if lambda_variable > ZERO_TOLERANCE:
        return True
    # it seems that lambda_variable is not ultimate indication of efficiency
    if efficiency_score > 1:
        return True
    return False


def check_input_and_output_categories(input_data):
    ''' Raises ValueError if input or output categories are empty.

        Args:
            input_data (InputData): objects that stores all input data.

        Raises:
            ValueError: if input or output categories are empty.
    '''
    if (len(input_data.input_categories) == 0 or
            len(input_data.output_categories) == 0):
        raise ValueError('Both input and output categories must be specified')


def check_categories(categories_to_ckeck, categories, message=''):
    ''' Raises ValueError if at least one of the given categories is not
        present in categories list.

        Args:
            categories_to_ckeck (list of str): list of categories that must
                be checked.
            categories (list of str): list of current categories.
            message (str, optional): message that must be shown if ValueError
                is raised.

        Raises:
            ValueError: if at least one of the categories is not present in
                the list of current categories.

        Example:
            >>> check_categories(['I1', 'I2'], ['I1', 'O1', 'O2'])
            >>> ValueError
            >>> check_categories(['I1', 'O2'], ['I1', 'O1', 'O2'])
            >>>
    '''
    for category in categories_to_ckeck:
        if category not in categories:
            if not message:
                message = ('Category <{0}> is not present in categories: {1}'.
                           format(category, categories))
            raise ValueError(message)


def parse_price_ratio(elem, value, constraint, categories, bounds):
    ''' Parses price ratio constraints and writes result to bounds.
        This function is internal utility function that is used for parsing
        weight restrictions in parse_constraint().

        Args:
            elem (str): string that describes left hand side of price ratio
                constraint.
            value (str): string that describes right hand side of price
                ratio constraint.
            constraint (str): string that describes entire constraint.
            categories (set of str): set of current categories.
            bounds (dict of tuple of str, str to str or empty dictionary):
                dictionary where parsed constraint will be written.

        Raises:
            ValueError: if constraint cannot be parsed.

        Example:
            >>> bounds = dict()
            >>> s = set(['I1', 'I2', 'O1', 'O2'])
            >>> parse_price_ratio('I1/I2', '5', 'I1/I2 >= 5', s, bounds)
            >>> bounds
            >>> {('I1', 'I2'): 5}
    '''
    two_categories = elem.split('/')
    if len(two_categories) != 2:
        raise ValueError('Cannot parse constraint: {0}'.format(
                         constraint))
    two_categories[0] = two_categories[0].strip()
    two_categories[1] = two_categories[1].strip()
    if (two_categories[0] not in categories or
            two_categories[1] not in categories):
        raise ValueError('Incorrect constraint, category does not'
                         ' exist: {0}'.format(
                            constraint))
    key = two_categories[0], two_categories[1]
    bounds[key] = float(value)


def parse_constraint(constraint, split_str, new_bounds_lb, new_bounds_ub,
                     categories):
    ''' Parses weight restriction constraint. This is internal utility function
        that is used in create_bounds().

        Args:
            constraint (str): constraint that needs to be parsed.
            split_str (str): '>=' or '<='.
            new_bounds_lb (dict of tuple of str, str to str or empty
                dictionary): dictionary where parsed constraint will be written.
                This dictionary will be filled if split_str is '>='.
            new_bounds_ub (dict of tuple of str, str to str or empty
                dictionary): dictionary where parsed constraint will be written.
                This dictionary will be filled if  split_str is '<='.
            categories (set of str): set of current categories.

        Returns:
            bool: True if split_str was found in constraint, False otherwise.

        Raises:
            ValueError: if constraint cannot be parsed.

        Example:
            >>> new_bounds_lb = dict()
            >>> new_bounds_ub = dict()
            >>> s = set(['I1', 'I2', 'O1', 'O2'])
            >>> constr = 'I1 >= 5'
            >>> parse_constraint(constr, '>=', new_bounds_lb, new_bounds_ub, s)
            >>> True
            >>> new_bounds_lb
            >>> {'I1': 5}
            >>> new_bounds_ub
            >>> {}
    '''
    found = False
    if constraint.find('<=') != -1:
        first = 0
    elif constraint.find('>=') != -1:
        first = 1
    else:
        raise ValueError('Unexpected constraint type,'
                         ' supported types >= and <=')
    lq = constraint.find(split_str)
    if lq != -1:
        found = True
        elements = [elem.strip() for elem in constraint.split(split_str)]
        if len(elements) != 2:
            raise ValueError('Cannot parse constraint: {0}'.format(
                             constraint))

        if elements[first].find('/') != -1:
            parse_price_ratio(elements[first], elements[1 - first],
                              constraint, categories, new_bounds_ub)
        elif elements[1 - first].find('/') != -1:
            parse_price_ratio(elements[1 - first], elements[first],
                              constraint, categories, new_bounds_lb)
        else:
            if elements[first] in categories:
                new_bounds_ub[elements[first]] = float(elements[1 - first])
            elif elements[1 - first] in categories:
                new_bounds_lb[elements[1 - first]] = float(elements[first])
            else:
                raise ValueError('Incorrect constraint, category does not'
                                 ' exist: {0}'.format(
                                     constraint))
    return found


def create_bounds(constraints, categories):
    ''' Creates proper data structures after parsing all constraints.

        Args:
            constraints (list of str): list of constraints to parse.
            categories (set of str): set of current categories.

        Returns:
            dict of str to tuple of double,
                double or dict of tuple of str,
                str to tuple of double, double:
                dictionary with parsed values of constraints.

        Raises:
            ValueError: if some of the constraints cannot be parsed.

        Example:
            >>> categories = set(['I1', 'I2', 'O1', 'O2'])
            >>> constraints = ['I1 <= 10', 'I1 >= 2', 'O1 >= 3', 'O2 <= 7']
            >>> create_bounds(constraints, categories)
            >>> {'I1': (2, 10), 'O1': (3, None), 'O2': (None, 7)}
            >>> ratio_bounds = ['I1/I2 <= 10', 'I1/I2 >= 1',
                                'O2/O1 >= 0.2', 'O1/O2 <= 0.5']
            >>> create_bounds(ratio_bounds, categories)
            >>> {('I1', 'I2'): (1, 10), ('O2', 'O1'): (0.2, None),
                 ('O1', 'O2'): (None, 0.5)}
    '''
    new_bounds_lb = dict()
    new_bounds_ub = dict()
    for constraint in constraints:
        lq = parse_constraint(constraint, '<=', new_bounds_lb, new_bounds_ub,
                              categories)
        gq = parse_constraint(constraint, '>=', new_bounds_lb, new_bounds_ub,
                              categories)
        if not (lq or gq):
            raise ValueError('Cannot parse constraint: {0}'.format(
                             constraint))

    new_bounds = dict()
    for lb_key, lb_value in new_bounds_lb.items():
        new_bounds[lb_key] = lb_value, new_bounds_ub.get(lb_key, None)

    for up_key, up_value in new_bounds_ub.items():
        new_bounds[up_key] = new_bounds_lb.get(up_key, None), up_value

    assert new_bounds
    return new_bounds


def contraint_is_price_ratio_type(bounds_key):
    ''' Checks if given parameter is a tuple with two elements. In the case of price
        ratio weight restrictions key of bounds dictionary will be a tuple with two
        elements.

        Args:
            tuple of str: tuple with elements.

        Returns:
            bool: true if given element is a tuple with two elements, false otherwise.
    '''
    return isinstance(bounds_key, tuple) and len(bounds_key) == 2


def get_price_ratio_categories(val):
    ''' Parses price ratio categories.

        Args:
            val (str): string with price ratio categories.

        Returns:
            tuple of str, str: tuple with categories in numerator and
                denominator respectively.

        Example:
            >>> get_price_ratio_categories('I1/ I2')
            >>> ('I1', 'I2')
            >>> get_price_ratio_categories('   I1   /  I2  ')
            >>> ('I1', 'I2')
            >>> get_price_ratio_categories('  name with spaces / I2')
            >>> ('name with spaces', 'I2')

        Warning:
            If val does not contain / or has more than one /, the
            function will fail with assert.
    '''
    elements = [elem.strip() for elem in val.split('/')]
    assert len(elements) == 2
    return elements[0], elements[1]


def find_category_name_in_restrictions(val):
    ''' Finds category name in the given constraint.

        Args:
            val (str): string that contains one category name.

        Returns:
            tuple of str, int: category name and index. Index is 0 if
                category name is on the left hand side of the constraint,
                non-zero if category name is on the right hand side.
                In the latter case, index correspond
                to the position of the category name in the constraint.

        Example:
            >>> find_category_name_in_restrictions('I1 <= 7')
            >>> ('I1', 0)
            >>> find_category_name_in_restrictions('  I1  <=  7.8 ')
            >>> ('I1', 0)
            >>> find_category_name_in_restrictions('  category name with spaces  <=  7.8 ')
            >>> ('category name with spaces', 0)
            >>> find_category_name_in_restrictions('7.8 >= I2')
            >>> ('I2', 7)
            >>> find_category_name_in_restrictions('7.8 >=       I2')
            >>> ('I2', 13)
            >>> find_category_name_in_restrictions('I1/O2 >= 0.5')
            >>> ('I1/O2', 0)

        Warning:
            It is assumed that given constraint is a valid constraint with
            category name. If invalid value is given, the function will fail or
            return incorrect value

    '''
    split_val = '<='
    if '>=' in val:
        split_val = '>='
    elements = [elem for elem in val.split(split_val)]
    assert len(elements) == 2
    category = elements[0].strip()
    index = 0
    try:
        float(elements[1])
    except ValueError:
        category = elements[1].strip()
        print('category [{0}], after split [{1}]'.format(category, elements[1]))
        print('index', elements[1].index(category))
        index += len(elements[0]) + 2 + elements[1].index(category)
    return category, index
