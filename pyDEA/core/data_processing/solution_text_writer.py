''' This model contains classes used for writing one page of a
    solution to a file.
'''

import os

from pyDEA.core.utils.dea_utils import format_data, change_to_unique_name_if_needed


class SolutionTextWriter(object):
    ''' This class implements generic utility to write formatted data
        to a given output (usually file, but could be anything that implements
        a particular interface). Data is written row by row and column by column,
        as a table.

        Attributes:
            current_row (int): index of current row.
            current_col (int): index of current column.
            delimiter (str): delimiter used to separate columns.

                    Note:
                        Rows are separated by end of line symbol.

            write_fnc (callable): function that takes one string argument which
                should be written to a given output, and writes this argument
                to that output.
            name (str): name of the solution page
                (i.e. EfficiencyScores, Parameters,...).
                Name is usually changed by the user or another function
                manually, for example see module write_data.

        Args:
            delimiter (str): delimiter used to separate columns.
            write_fnc (callable): function that takes one string argument which
                should be written to a given output, and writes this argument
                to that output.
    '''
    def __init__(self, delimiter, write_fnc):
        self.current_row = -1
        self.current_col = -1
        self.delimiter = delimiter
        self.write_fnc = write_fnc
        self.name = ''

    def write(self, row_index, column_index, data):
        ''' Writes given data to an output (usually file).

            Warning:
                When using this function, rows and columns must be
                specified in order,
                i.e. you can call write(0, 0, 'data'), then write(1, 0, 'data').
                But you cannot call write(2, 0, 'data'), and then
                write(0, 0, 'data').
                Data should be written row by row and column by column.

            Args:
                row_index (int): index of the row where data must be written.
                column_index (int): index of the column where data must
                    be written.
                data (str or float): data that will be written.

                    Note:
                        data will be formatted before writing, see function
                        format_data.

            Example:
                >>> writer = SolutionTextWriter(';', write_fnc)
                >>> write(0, 0, 'a')
                >>> write(0, 1, 'b')
                >>> write(1, 0, 'c')
                "\\na;b\\nc"
        '''
        if row_index != self.current_row:
            self.write_fnc('\n')
            if self.current_col != -1 and column_index != 0:
                self.write_fnc(self.delimiter)
        else:
            self.write_fnc(self.delimiter)
        self.current_row = row_index
        self.current_col = column_index
        self.write_fnc(format_data(data))


class TxtOneFileWriter(object):
    ''' This class is a helper class for TxtWriter. It implements
        function write_text that writes data to a file, and it
        keeps reference to file.

        Attributes:
            file_ref (file reference): reference to file where all data
                is written.

        Args:
            file_ref (file reference): reference to file where all
                data is written.
    '''
    def __init__(self, file_ref):
        self.file_ref = file_ref

    def write_text(self, data):
        ''' Writes given data to file.

            Args:
                data (str): data to write to file.
        '''
        self.file_ref.write(data)


class TxtWriter(object):
    ''' This class is used for writing solution to csv. It creates a
        given folder where all csv files will be written and
        creates solution files in this folder.

        Attributes:
            folder_name (str): folder for csv files.
            tabs (list of file references): list of references to files where
                solution will be written.
            tab_writers (list of SolutionTextWriter): list of SolutionTextWriter
                objects each of which is responsible to filling one csv
                file with data.

        Args:
            folder_name (str): folder for csv files.
    '''
    def __init__(self, folder_name):
        self.folder_name = folder_name
        try:
            os.makedirs(folder_name)
        except OSError:
            pass
        self.tabs = []
        self.tab_writers = []

    def add_sheet(self, name):
        ''' Creates a csv file that represents one page of the solution.

            Args:
                name (str): name of the file.

                    Note:
                        This is a temporary name. After solution is written
                        and save is called,
                        file will be renamed according to a solution page name
                        (i.e. EfficiencyScores).

            Returns:
                SolutionTextWriter: SolutionTextWriter object that is
                    responsible for filling this file with data.
        '''
        file_name = '{0}.csv'.format(name)
        file_name = os.path.join(self.folder_name, file_name)
        file_name = change_to_unique_name_if_needed(file_name)
        file_ref = open(file_name, 'w')
        self.tabs.append(file_ref)
        tab_writer = TxtOneFileWriter(file_ref)
        writer = SolutionTextWriter(',', tab_writer.write_text)
        self.tab_writers.append((file_name, writer))
        return writer

    def save(self, file_name):
        ''' Closes all created csv files and renames them according to solution
            page names.

            Args:
                file_name (str): this parameter is ignored.
        '''
        # no need to save, only to close all files
        for file_ref in self.tabs:
            file_ref.close()
        for saved_file_name, tab_writer in self.tab_writers:
            new_name = '{0}.csv'.format(tab_writer.name)
            new_name = change_to_unique_name_if_needed(new_name)
            os.rename(saved_file_name, os.path.join(self.folder_name, new_name))


class OneCsvWriter(object):
    ''' This class is used for writing data to a csv file.

        Attributes:
            file_name (str): name of the file to create.
            tab_writer (TxtOneFileWriter): TxtOneFileWriter
                object which is responsible to filling  csv
                file with data.

        Args:
            file_name (str): name of the file to create.
    '''
    def __init__(self, file_name):
        self.tab_writer = None
        self.file_name = file_name

    def add_sheet(self, name):
        ''' Creates a csv file.

            Args:
                name (str): this parameter is ignored.

                    Note:
                        This argument is ignored, the file name given in class
                        consructor is used.

            Returns:
                SolutionTextWriter: SolutionTextWriter object that is
                    responsible for filling this file with data.
        '''
        file_ref = open(self.file_name, 'w')
        tab_writer = TxtOneFileWriter(file_ref)
        writer = SolutionTextWriter(',', tab_writer.write_text)
        self.tab_writer = tab_writer
        return writer

    def save(self, file_name):
        ''' Closes opened csv file.

            Args:
                file_name (str): this parameter is ignored.
        '''
        # no need to save, only to close opened file
        self.tab_writer.file_ref.close()
