''' This module contains methods for running pyDEA from terminal.
'''
import sys

from pyDEA.core.data_processing.parameters import parse_parameters_from_file
from pyDEA.core.utils.run_routine import RunMethodTerminal
from pyDEA.core.utils.dea_utils import clean_up_pickled_files, get_logger


def main(filename, output_format='xlsx', output_dir='', sheet_name_usr=''):
    ''' Main function to run DEA models from terminal.

        Args:
            filename (str): path to file with parameters.
            output_format (str, optional): file format of solution file.
                This value is used
                only if OUTPUT_FILE in parameters is empty or set to auto.
                Defaults to xlsx.
            output_dir (str, optional): directory where solution must
                be written.
                If it is not given, solution will be written to current folder.
                This value is used
                only if OUTPUT_FILE in parameters is empty or set to auto.
            sheet_name_usr (str, optional): name of the sheet in xlsx-file with
                input data from which data will be read. If input data file is
                in csv format,
                this value is ignored.

    '''
    print('Params file', filename, 'output_format', output_format,
          'output_dir', output_dir, 'sheet_name_usr', sheet_name_usr)
    
    logger = get_logger()
    logger.info('Params file "%s", output format "%s", output directory "%s", sheet name "%s".',
                filename, output_format, output_dir, sheet_name_usr)

    params = parse_parameters_from_file(filename)
    params.print_all_parameters()
    run_method = RunMethodTerminal(params, sheet_name_usr, output_format,
                                   output_dir)
    run_method.run(params)
    clean_up_pickled_files()
    logger.info('pyDEA exited.')

if __name__ == '__main__':
    args = sys.argv[1:]
    logger = get_logger()
    logger.info('pyDEA started as a console application.')
    print('args = {0}'.format(args))
    if len(args) < 1 or len(args) > 4:
        logger.error('Invalid number of input arguments. At least one '
                     'argument must be given, no more than 4 arguments, but %d were given.',
                     len(args))
        raise ValueError('Invalid number of input arguments. At least one '
                         'argument must be given, no more than 4 arguments'
                         ' are expected. Input arguments are:\n (1) path to'
                         ' file with parameters (compulsory)\n'
                         '(2) output file format, possible values: xlsx'
                         ' and csv, default value is xlsx (optional), this'
                         ' value is used only if auto or empty string was set'
                         ' for OUTPUT_FILE in parameters file \n'
                         '(3) output directory (optional, if not specified,'
                         ' output is written to current directory)\n'
                         '(4) sheet name from which data should be read '
                         '(optional, if not specified, data is read from'
                         ' the first sheet)')
    try:
        main(*args)
    except Exception as excinfo:
        logger.error(excinfo)
        raise    
