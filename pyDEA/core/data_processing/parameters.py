''' This module contains methods and Parameters class responsible
    for parsing, storing and updating parameters from a file.

    Attributes:
        VALID_PARAM_NAME (str): string for regular expressions that
            describes valid parameter names (must start with a word character,
            might contain word characters and spaces).
        VALID_PARAM_VALUE (str): string for regular expressions that
            describes valid parameter values (must start with any non-space
            character).
        VALID_PARAM_NAMES (list of str): list of allowed parameter names.
        CATEGORICAL_AND_DATA_FIELDS (list of str): list of parameter names
            that contain data or categorical information.
'''


import re

import pyDEA.core.utils.dea_utils as dea_utils

# must start with word character
# might contain word characters and spaces
VALID_PARAM_NAME = r'\w[\w ]*'

# must start with any non-space character,
# all other characters are allowed,
# since file paths must be treated
VALID_PARAM_VALUE = r'\S.*|(?imsux)' #previously r'\S.*|(?iLmsux)' causing error "cannot use LOCALE flag with a str pattern" with Python>=3.6

VALID_PARAM_NAMES = ['DATA_FILE', 'INPUT_CATEGORIES', 'OUTPUT_CATEGORIES',
                     'DEA_FORM', 'RETURN_TO_SCALE', 'ORIENTATION',
                     'NON_DISCRETIONARY_CATEGORIES',
                     'WEAKLY_DISPOSAL_CATEGORIES', 'USE_SUPER_EFFICIENCY',
                     'ABS_WEIGHT_RESTRICTIONS', 'VIRTUAL_WEIGHT_RESTRICTIONS',
                     'PRICE_RATIO_RESTRICTIONS', 'MAXIMIZE_SLACKS',
                     'MULTIPLIER_MODEL_TOLERANCE', 'OUTPUT_FILE',
                     'CATEGORICAL_CATEGORY', 'PEEL_THE_ONION']

CATEGORICAL_AND_DATA_FIELDS = ['DATA_FILE', 'INPUT_CATEGORIES',
                               'OUTPUT_CATEGORIES',
                               'NON_DISCRETIONARY_CATEGORIES',
                               'WEAKLY_DISPOSAL_CATEGORIES',
                               'ABS_WEIGHT_RESTRICTIONS',
                               'VIRTUAL_WEIGHT_RESTRICTIONS',
                               'PRICE_RATIO_RESTRICTIONS', 'OUTPUT_FILE',
                               'CATEGORICAL_CATEGORY']


def parse_parameters_from_file(filename):
    ''' Reads parameters from a given file. If file does not exist, the
        exception will be thrown. Returns Parameters object with
        all parameters. Does not validate parameters.
        Throws an exception if there are repeating
        parameters (all parameters must be unique).
        All parameters must follow convention: <param_name> {param_value}.
        Supports one line comments:
        <param_name> {param_value} # this parameter is important.
        If some parameters are missing, their value will be set to empty
        string.

        Args:
            filename (str): path to file with parameters. Only text files
                are accepted, but actual file extension does not matter.

        Returns:
            Parameters: parameter object with parsed parameters.

        Raises:
            FileNotFound: if given file does not exist.
            ValueError: if file does not contain any valid parameters.
    '''
    pattern = ''.join(['<(', VALID_PARAM_NAME, r')>\s*{(',
                       VALID_PARAM_VALUE, ')}'])
    params = Parameters()
    # will raise IOError exception if fileName
    # does not exists, 'rU' - r - read mode,
    # U - Universal for encoding
    nb_parsed_params = 0
    with open(filename, 'rU') as file_with_params:
        for line in file_with_params:
            line = extract_comment(line)
            matched_params = re.findall(pattern, line)
            for match in matched_params:
                if match[0] in VALID_PARAM_NAMES:
                    params.update_parameter(match[0], match[1])
                    nb_parsed_params += 1
    if nb_parsed_params == 0:
        raise ValueError('File {filename} does not contain any valid'
                         ' parameter values'.format(filename=filename))
    return params


def extract_comment(line):
    ''' Removes comments from a given line. Symbol # is treated as
        one line comment separator.

        Example:
            >>> extract_comment("some line")
            some line
            >>> extract_comment("line with comment # here comes comment")
            line with comment
            >>> extract_comment("# only comment is present")
            >>>

        Args:
            line (str): line with text.

        Returns:
            str: line without comment.
    '''
    pos = line.find('#')
    if pos != -1:
        return line[:pos]
    return line


def write_parameters_to_file(params, filename):
    ''' Writes all parameters stored in a given Parameters object
        to a given file in the following format format:
        <param_name> {param_value}. If the file
        already exists, all parameters will be over-written with the new ones.

        Args:
            params (Parameters): parameters object.
            filename (str): file name where parameters must be written.
    '''
    file_with_params = open(filename, 'w')  # w - open to write data
    for (name, value) in params.params.items():
        file_with_params.write('<' + name + '> {' + value + '}\n')
    file_with_params.close()


def validate_string(string, expression):
    ''' Checks if a given string matched a given regular expression.

        Example:
            >>> validate_string('', VALID_PARAM_NAME)
            False
            >>> validate_string('abc', VALID_PARAM_NAME)
            True
            >>> validate_string('abc something', VALID_PARAM_NAME)
            True
            >>> validate_string(' space', VALID_PARAM_NAME)
            False
            >>> validate_string('     ', VALID_PARAM_NAME)
            False
            >>> validate_string(r'\home\path\\file.txt  ', VALID_PARAM_VALUE)
            True
            >>> validate_string(r' \home\path\\file.txt  ', VALID_PARAM_VALUE)
            False

        Args:
            string (str): string to check.
            expression (str): regular expression string.

        Returns:
            bool: True if string meets conditions specified by a regular
                expression, False otherwise.
    '''
    match = re.search(expression, string)
    if match and match.group() == string:
        return True
    return False


class Parameters:
    ''' This class stores and manipulates all parameters needed to run
        DEA models. After object creation all parameter values are set
        to empty string.

        Attributes:
            params (dict of str to str): dictionary of parameter names
                and values.

                Example:
                    >> params = {'DEAform': 'env', 'ReturnsToScale': 'VRS'}
    '''
    def __init__(self):
        self.params = dict()
        for key in VALID_PARAM_NAMES:
            self.params[key] = ''

    def update_parameter(self, param_name, param_value):
        ''' Updates existing parameter in the dictionary. If parameter does not
            exist in the dictionary, throws exception.
            Parameter name and value must satisfy conditions specified by
            regular expressions
            VALID_PARAM_NAME and VALID_PARAM_VALUE.

            Example:
                >>> p = Parameters()
                >>> p.get_parameter_value('DEA_FORM')
                ''
                >>> p.update_parameter('DEA_FORM', 'new value')
                >>> p.get_parameter_value('DEA_FORM')
                'new value'
                >>> p.update_parameter('param2', 'value2')
                KeyError
                >>> p.update_parameter('DEA_FORM', '   ')
                ValueError

            Args:
                param_name (str): parameter name.
                param_value (str): parameter value.

            Raises:
                KeyError: if a given parameter name does not belong to
                    VALID_PARAM_NAMES.
                ValueError: if a given parameter value does not satisfy
                    regular expression given in VALID_PARAM_VALUE.
        '''
        if param_name not in self.params:
            raise KeyError('Parameter {0} does not exists in'
                           ' the dictionary'.format(param_name))
        if not validate_string(param_value, VALID_PARAM_VALUE):
            raise ValueError('Trying to update parameter <{0}> with '
                             'not valid value <{1}>'.
                             format(param_name, param_value))
        self.params[param_name] = param_value

    def get_parameter_value(self, param_name):
        ''' Returns a value that corresponds to a given parameter name.
            If there is no such parameter name, throws KeyError exception.

            Example:
                >>> allParams = Parameters()
                >>> allParams.update_parameter('DEA_FORM', 'value1')
                >>> allParams.get_parameter_value('DEA_FORM')
                value1
                >>> allParams.get_parameter_value('Param2')
                KeyError

            Args:
                param_name (str): parameter name.

            Returns:
                str: parameter value.
        '''
        return self.params[param_name]

    def print_all_parameters(self):
        ''' Prints all parameters on screen.
        '''
        for param in self.params.items():
            print("<{0}> = {1}".format(param[0], param[1]))

    def get_all_params_as_string(self):
        ''' Returns all parameters with values as a string. 

            Returns:
                str: all paremeters with values.
        '''
        all_params = []
        for param in self.params.items():
            all_params.append("<{0}> = '{1}'".format(param[0], param[1]))
        return ', '.join(all_params)

    def get_set_of_parameters(self, param_name, delimiter=';'):
        ''' Some of the parameters contain a set of values.
            Returns a set of strings with these values instead of
            one string.

            Args:
                param_name (str): parameter name.
                delimiter (str, optional): delimiter. Defaults to semicolon.

            Returns:
                set of str: set of parsed parameter values.
        '''
        params_as_str = self.get_parameter_value(param_name)
        return set([elem.strip() for elem in params_as_str.split(delimiter)
                    if elem.strip()])

    def copy_all_params(self, params_from):
        ''' Copies all parameter values from a given parameter object.

            Args:
                params_from (Parameters): parameter object from which
                    parameter values will be copied.
        '''
        for name, value in params_from.params.items():
            self.update_parameter(name, value)

    def remove_category_from_params(self, category_type, category_name):
        ''' Removes a given parameter value from parameters.

            Args:
                category_type (str): parameter name.
                category_name (str): value that should be removed.
        '''
        categories = self.get_set_of_parameters(category_type)
        if category_name in categories:
            categories.remove(category_name)
            self.update_parameter(category_type, '; '.join(categories))

    def clear_all_categorical_and_data_fields(self):
        ''' Sets values of parameters from CATEGORICAL_AND_DATA_FIELDS
            to empty strings.
        '''
        for param_name in CATEGORICAL_AND_DATA_FIELDS:
            self.update_parameter(param_name, '')

    def change_category_name(self, old_name, new_name):
        ''' Changes a given category name to a new name in all parameter
            values that contain this category.

            Args:
                old_name (str): previous category name.
                new_name (str): new category name.
        '''
        for param_name in CATEGORICAL_AND_DATA_FIELDS:
            if param_name != 'DATA_FILE' and param_name != 'OUTPUT_FILE':
                param_values = self.get_set_of_parameters(param_name)
                new_param_value = ''
                for val in param_values:

                    value_to_compare = val
                    index = 0
                    name_to_add = new_name
                    price_ratio = False
                    if (param_name == 'ABS_WEIGHT_RESTRICTIONS' or
                            param_name == 'VIRTUAL_WEIGHT_RESTRICTIONS'):
                        value_to_compare, index = dea_utils.find_category_name_in_restrictions(val)
                    elif param_name == 'PRICE_RATIO_RESTRICTIONS':
                        value_to_compare, index = dea_utils.find_category_name_in_restrictions(val)
                        category1, category2 = dea_utils.get_price_ratio_categories(value_to_compare)
                        if old_name == category1:
                            name_to_add = new_name + '/' + category2
                            price_ratio = True
                        elif old_name == category2:
                            name_to_add = category1 + '/' + new_name
                            price_ratio = True

                    if old_name == value_to_compare or price_ratio:
                        new_param_value = (new_param_value + val[:index] +
                                           name_to_add +
                                           val[index + len(value_to_compare):])
                    else:
                        new_param_value = new_param_value + val
                    if new_param_value and param_name != 'CATEGORICAL_CATEGORY':
                        new_param_value = new_param_value + ';'

                if new_param_value:
                    self.update_parameter(param_name, new_param_value)
