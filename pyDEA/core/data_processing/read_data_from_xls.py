''' This module contains functions and classes responsible for reading
    input data from xls, xlsx and csv files.

    Note:
        In xlrd when text is read from xlsx, leading white spaces
        are automatically removed. But when text is read from xls,
        they are kept.
'''

import xlrd
import csv
import os
from collections import OrderedDict

from pyDEA.core.data_processing.input_data import InputData
from pyDEA.core.utils.dea_utils import is_valid_coeff, NOT_VALID_COEFF


def read_data(file_name, sheet_name=''):
    ''' Reads data from a given file.

        Args:
            file_name (str): path to file with input data.
            sheet_name (str, optional): name of the excel sheet
                where data is stored. Defaults to empty string.
                If it is not given, data is read from the first sheet.

        Returns:
            tuple of list of str, list of str, str, str:
                tuple with the following components:

                * list of categories (first non-empty row is considered
                  to be a list of categories);
                * list where the first element is DMU name, all other
                  elements are coefficients;
                * name of all DMUs if specified;
                * name of sheet where data was read from.

        Note:
            DMUs and categories can be strings or numbers, so returned types
            depend on these types.
    '''
    just_name, extension = os.path.splitext(file_name)
    if extension in ['.xls', '.xlsx']:
        reader = XLSReader()
    elif extension == '.csv':
        reader = CSVReader()
    else:
        raise ValueError('{0} format is not supported'.format(extension))
    reader.open_file(file_name, sheet_name)
    categories = []
    coefficients = []
    first_non_empty_row = True
    first_row_index = -1
    col_to_return = -1
    col_indexes = []
    for row_index, row in enumerate(reader.get_rows()):
        if has_non_empty_cells(reader, row):
            if first_non_empty_row:
                categories, col_indexes = extract_categories(reader, row)
                first_non_empty_row = False
                first_row_index = row_index
            else:
                assert(col_indexes)
                dmu, coeff_values, col = extract_coefficients(reader, row,
                                                              col_indexes)
                if col_to_return == -1:
                    col_to_return = col
                tmp = []
                tmp.append(dmu)
                tmp.extend(coeff_values)
                coefficients.append(tmp)
    dmu_name = reader.get_cell_value(first_row_index, col_to_return)
    if dmu_name:
        categories.pop(0)
    reader.close_file()
    return categories, coefficients, dmu_name, reader.get_sheet_name()


def fake_fnc(count):
    ''' Helper function that always returns True.
    '''
    return True


def convert_to_dictionary(data, check_value=fake_fnc):
    ''' Converts given list of data to a dictionary.

        Args:
            data (list of str or double): list where the first element
                is DMU name, all other elements are coefficients.
            check_value (func, optional): function that is called on each
                element of the data list (except the first one) before
                adding the coefficient to a dictionary. Defaults to
                fake_fnc.

        Returns:
            tuple of dict of str to list of double, bool:
                tuple with the following values:

                * dictionary that  maps DMU name to a list with coefficients.
                * true if there are the same DMU names, False otherwise.
    '''
    coefficients = OrderedDict()
    has_same_dmus = False
    for values in data:
        if values[0] in coefficients.keys():
            has_same_dmus = True
        coefficients[values[0]] = [float(val) for count, val in
                                   enumerate(values[1:])
                                   if check_value(count)]

    return coefficients, has_same_dmus


def validate_data(categories, coefficients):
    ''' Checks if given data is valid.

        Args:
            categories (list of str): list of categories.
            coefficients (dict of str to list of double): dictionary that
                maps DMU name to a list with coefficients.

        Returns:
            bool: True if data in categories and coefficients is valid,
                False otherwise.
    '''
    nb_categories = len(categories)
    if nb_categories == 0 or len(coefficients) == 0:
        return False
    for dmu, dmu_coeffs in coefficients.items():
        if len(dmu_coeffs) != nb_categories:
            return False
        for coeff in dmu_coeffs:
            if is_valid_coeff(coeff) == NOT_VALID_COEFF:
                return False
    return True


def construct_input_data_instance(categories, coefficients):
    ''' Constructs proper instance of InputData from categories and
        coefficients.

        Args:
            categories (list of str): list of categories.
            coefficients (dict of str to list of double): dictionary that
                maps DMU name to a list with coefficients.

        Returns:
            InputData: constructed instance.
    '''
    input_data = InputData()
    for (dmu, list_of_coefficients) in coefficients.items():
        for count, coeff in enumerate(list_of_coefficients):
            input_data.add_coefficient(dmu, categories[count], coeff)

    return input_data


def has_non_empty_cells(reader, row):
    ''' Checks if at least one of the values in array contains
        non-empty data.

        Args:
            reader (CSVReader or XLSReader): object that implements
                interface for reading input data.
            row (list of values): list of values stored in a row.

        Returns:
            bool: true if at least one of the values in array contains
                non-empty data, false otherwise.
    '''
    for cell in row:
        if (reader.cell_is_not_empty(cell) and
                reader.cell_is_not_blank(cell) or
                reader.is_valid_text(cell)):
            return True
    return False


def extract_categories(reader, row):
    ''' Constructs list of categories out of data in row.

        Args:
            reader (CSVReader or XLSReader): object that implements
                interface for reading input data.
            row (list of values): list of values stored in a row.

        Returns:
            tuple of list of str, list of int: tuple with list of
                parsed categories and list fo column indexes where
                parsed categories were found.
    '''
    categories = []
    col_indexes = []
    for col, cell in enumerate(row):
        if reader.cell_is_not_empty(cell) and reader.cell_is_not_blank(cell):
            col_indexes.append(col)
            if reader.is_valid_text(cell):
                categories.append(reader.get_cell_content(cell).strip())
            else:
                categories.append(reader.get_cell_content(cell))

    return categories, col_indexes


def extract_coefficients(reader, row, col_indexes):
    ''' Parses row with coefficients.

        Args:
            reader (CSVReader or XLSReader): object that implements
                interface for reading input data.
            row (list of values): list of values stored in a row.
            col_indexes (list of int): list of column indexes where
                categories were found.

        Returns:
            tuple of str, list of double, int: a tuple with DMU name,
                list of corresponding coefficients and column index
                of the first non-empty value.
    '''
    dmu = ''
    coefficients = []
    col_to_return = -1
    first_non_empty_col = find_first_non_empty_col(reader, row)

    for col_index, cell in enumerate(row):

        if col_index == first_non_empty_col:

            if not reader.cell_is_text(cell):
                dmu = reader.get_cell_content(cell)
                col_to_return = col_index
            elif reader.is_valid_text(cell):
                dmu = reader.get_cell_content(cell).strip()
                col_to_return = col_index
        elif col_index > first_non_empty_col:
            if col_index in col_indexes:
                if (reader.cell_is_not_empty(cell) and
                        reader.cell_is_not_blank(cell)):
                    if not reader.cell_is_text(cell):
                        coefficients.append(reader.get_cell_content(cell))
                    elif reader.is_valid_text(cell):
                        # try to convert to number
                        coeff = reader.get_cell_content(cell).strip()
                        try:
                            val = float(coeff)
                        except ValueError:
                            val = coeff
                        coefficients.append(val)
                else:
                    coefficients.append('')

    return dmu, coefficients, col_to_return


def find_first_non_empty_col(reader, row):
    ''' Finds index of the first non-empty column.

        Args:
            reader (CSVReader or XLSReader): object that implements
                interface for reading input data.
            row (list of values): list of values stored in a row.

        Returns:
            int: index of the first non-empty column.
    '''
    for col_index, cell in enumerate(row):
        if reader.cell_is_not_empty(cell) and reader.cell_is_not_blank(cell):
            return col_index


class XLSReader(object):
    ''' This class implements parsing of input data from xls and xlsx files.

        Attributes:
            open_sheet (xlrd.Sheet): open sheet where data is stored.

    '''
    def __init__(self):
        self.open_sheet = None

    def open_file(self, file_name, sheet_name):
        ''' Opens a given file and prepares to read data from a given sheet.

            Args:
                file_name (str): path to file with input data.
                sheet_name (str): sheet name.
        '''
        book = xlrd.open_workbook(file_name)
        if sheet_name:
            sheet = book.sheet_by_name(sheet_name)
        else:
            sheet = book.sheet_by_index(0)
        self.open_sheet = sheet

    def get_sheet_name(self):
        ''' Returns opened sheet name.

            Returns:
                str: sheet name.
        '''
        return self.open_sheet.name

    def get_cell_value(self, row, column):
        ''' Returns value of the cell with given row and column index.

            Args:
                row (int): row index.
                column (int): column index.

            Returns:
                str: cell value.
        '''
        return self.open_sheet.cell_value(row, column)

    def get_rows(self):
        ''' Returns a list of rows.

            Returns:
                list of list of xlrd.Cell: list of rows.
        '''
        return [self.open_sheet.row(row_index) for row_index in
                range(self.open_sheet.nrows)]

    def cell_is_not_empty(self, cell):
        ''' Checks if a given cell has non-empty value.

            Args:
                cell (xlrd.Cell): cell.

            Returns:
                bool: True if cell has non-empty value, False otherwise.
        '''
        return cell.ctype != xlrd.XL_CELL_EMPTY

    def cell_is_not_blank(self, cell):
        ''' Checks if a given cell has blank value.

            Args:
                cell (xlrd.Cell): cell.

            Returns:
                bool: True if cell has blank value, False otherwise.
        '''
        return cell.ctype != xlrd.XL_CELL_BLANK

    def is_valid_text(self, cell):
        ''' Checks if a given cell contain valid text.

            Args:
                cell (xlrd.Cell): cell.

            Returns:
                bool: True if cell contain valid text, False otherwise.
        '''
        return cell.ctype == xlrd.XL_CELL_TEXT and cell.value

    def cell_is_text(self, cell):
        ''' Checks if a given cell contain text.

            Args:
                cell (xlrd.Cell): cell.

            Returns:
                bool: True if cell contain text, False otherwise.
        '''
        return cell.ctype == xlrd.XL_CELL_TEXT

    def get_cell_content(self, cell):
        ''' Returns cell content.

            Args:
                cell (xlrd.Cell): cell.

            Returns:
                cell content (type depends on what is stored in the cell).
        '''
        return cell.value

    def close_file(self):
        ''' Closes file if necessary.
        '''
        pass


class CSVReader(object):
    ''' This class implements parsing of input data from csv files.

        Attributes:
            rows (list of list of str): list of rows with input data.
            file_ref (file): file reference.
    '''
    def __init__(self):
        self.rows = []
        self.file_ref = None

    def open_file(self, file_name, sheet_name):
        ''' Opens a given file and prepares to read data from a given sheet.

            Args:
                file_name (str): path to file with input data.
                sheet_name (str): sheet name.
        '''
        self.file_ref = open(file_name, 'r')
        rows = csv.reader(self.file_ref)
        self.rows.clear()
        for row in rows:
            self.rows.append(row)

    def get_sheet_name(self):
        ''' Since csv files do not support sheets, always returns empty string.

            Returns:
                str: empty string.
        '''
        return ''

    def get_cell_value(self, row_index, column):
        ''' Returns value of the cell with given row and column index.

            Args:
                row (int): row index.
                column (int): column index.

            Returns:
                str: cell value.
        '''
        count = 0
        for row in self.rows:
            if count == row_index:
                assert column < len(row)
                return row[column]
            count += 1
        return ''

    def get_rows(self):
        ''' Returns a list of rows.

            Returns:
                list of list of str: list of rows.
        '''
        return self.rows

    def cell_is_not_empty(self, cell):
        ''' Checks if a given cell has non-empty value.

            Args:
                cell (str): cell.

            Returns:
                bool: True if cell has non-empty value, False otherwise.
        '''
        return cell != ''

    def cell_is_not_blank(self, cell):
        ''' Checks if a given cell has blank value.

            Args:
                cell (str): cell.

            Returns:
                bool: True if cell has blank value, False otherwise.
        '''
        return cell != ''

    def is_valid_text(self, cell):
        ''' Checks if a given cell contain valid text.

            Args:
                cell (str): cell.

            Returns:
                bool: True if cell contain valid text, False otherwise.
        '''
        return cell != ''

    def cell_is_text(self, cell):
        ''' All cells are stored as strings, always returns True.

            Returns:
                bool: always returns True.
        '''
        return True

    def get_cell_content(self, cell):
        ''' Returns cell content.

            Args:
                cell (str): cell.

            Returns:
                str: cell content.
        '''
        return cell

    def close_file(self):
        ''' Closes file if necessary.
        '''
        self.file_ref.close()
