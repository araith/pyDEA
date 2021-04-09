''' This module contains classes responsible for solving a given
    data instance either through terminal or GUI.
'''
import datetime
import os

from tkinter.messagebox import showerror
from tkinter import StringVar

from pyDEA.core.data_processing.read_data import validate_data
from pyDEA.core.data_processing.read_data import construct_input_data_instance, read_data
from pyDEA.core.data_processing.read_data import convert_to_dictionary
from pyDEA.core.utils.dea_utils import create_params_str, auto_name_if_needed
from pyDEA.core.utils.dea_utils import get_logger
from pyDEA.core.data_processing.write_data import FileWriter
from pyDEA.core.data_processing.xlsx_workbook import XlsxWorkbook
import pyDEA.core.utils.model_builder as model_builder
from pyDEA.core.models.model_progress_bar_decorator import ProgressBarDecorator
from pyDEA.core.models.peel_the_onion import peel_the_onion_method
from pyDEA.core.data_processing.solution_text_writer import TxtWriter


class RunMethodBase(object):
    ''' This class is an abstract base class for other classes used
        for executing solution routine - create data instance,
        solve LPs, post-process solutions.
    '''
    def run(self, params):
        ''' Executes solution routine - create data instance,
            solve LPs, post-process solutions.

            Args:
                params (Parameters): parameters of a given problem instance
        '''
        logger = get_logger()
        logger.info('Started solving given DEA model(s).')
        logger.info('Parameters: %s', params.get_all_params_as_string())
        categories = self.get_categories()
        coefficients, has_same_dmus = self.get_coefficients()

        if has_same_dmus:
            self.show_error('Some DMUs have the same name')
        else:
            if validate_data(categories, coefficients):
                try:

                    self.validate_weights_if_needed()  # MUST be called
                    # before model_builder, because it might
                    # update parameters
                    model_input = construct_input_data_instance(categories,
                                                                coefficients)

                    models, all_params = model_builder.build_models(params,
                                                                    model_input)

                    self.init_before_run(len(models), coefficients)

                    solutions = []

                    state = True
                    param_strs = []
                    all_ranks = []
                    run_date = datetime.datetime.today()
                    start_time = datetime.datetime.now()
                    for count, model_obj in enumerate(models):
                        model = self.decorate_model(model_obj)

                        call_peel_the_onion = params.get_parameter_value(
                            'PEEL_THE_ONION')

                        if call_peel_the_onion:
                            model_solution, ranks, state = (
                                peel_the_onion_method(model))
                            all_ranks.append(ranks)
                        else:
                            model_solution = model.run()

                        str_to_write = create_params_str(all_params[count])
                        param_strs.append(str_to_write)
                        solutions.append(model_solution)
                        try:
                            solutions.append(model.second_solution)
                            param_strs.append(str_to_write + ' second phase')
                        except AttributeError:
                            pass

                    end_time = datetime.datetime.now()
                    diff = end_time - start_time
                    total_seconds = diff.total_seconds()
                    if params.get_parameter_value('RETURN_TO_SCALE') == 'both':
                        derive_returns_to_scale_classification(param_strs, solutions)
                    self.post_process_solutions(solutions, params, param_strs,
                                                all_ranks, run_date,
                                                total_seconds)

                    if state is False:
                        self.show_error('For one of the runs of the '
                                        'peel-the-onion problem is infeasible'
                                        ' or unbounded')
                    self.show_success()
                except Exception as excinfo:
                    self.show_error(excinfo)
                else:
                    logger.info('Given DEA model(s) successfully solved.')
            else:
                self.show_error('Some of the input data is not correct')

    def get_categories(self):
        ''' Returns current categories.

            Returns:
                (list of str): list of current categories
        '''
        raise NotImplementedError()

    def get_coefficients(self):
        ''' Returns problem data coefficients.

            Returns:
                (dict of str to list of double): dictionary that maps
                    DMU code to the list of coefficients. Coefficients
                    must appear in the same order as categories.
        '''
        raise NotImplementedError()

    def show_error(self, message):
        ''' Displays error message.

            Args:
                message (str): error message
        '''
        raise NotImplementedError()

    def validate_weights_if_needed(self):
        ''' Validates weight restrictions if they are present.
            This method might update parameters, hence,
            it MUST be called before model_builder.
        '''
        raise NotImplementedError()

    def init_before_run(self, nb_models, coefficients):
        ''' Initialises appropriate data structures before solving LPs,
            implementation depends on a concrete class.

            Args:
                nb_models (int): number of models, can take values 1, 2 or 4.
                coefficients (dict of str to list of float): dictionary
                    that maps DMU code to the list of coefficients
        '''
        raise NotImplementedError()

    def decorate_model(self, model_obj):
        ''' This method is called after a model has been created,
            implementation depends on a concrete class.

            Args:
                model_obj (ModelBase or any of its derivatives):
                    model

            Returns:
                (ModelBase or any of its derivatives): decorated model
        '''
        raise NotImplementedError()

    def post_process_solutions(self, solutions, params, param_strs, all_ranks,
                               run_date, total_seconds):
        ''' Post-processes solutions,
            implementation depends on a concrete class.

            Args:
                solutions (list of Solution): list of obtained solutions.
                params (Parameter): parameters.
                param_strs (list of str): list of strings that describe
                    each model.
                all_ranks (list of dict of str to double):
                    list that contains dictionaries that map DMU code
                    to peel the onion rank.
                run_date (datetime): date and time when the problem was solved.
                total_seconds (float): time (in seconds) needed to solve
                    the problem.
        '''
        raise NotImplementedError()

    def show_success(self):
        ''' By default does not do anything, but can be redefined
            by child classes to show a message that the execution was successful.
        '''
        pass


class RunMethodTerminal(RunMethodBase):
    ''' This class implements running routing from terminal.

        Attributes:
            params (Parameters): parameters.
            sheet_name_usr (str): sheet name from which input data must be read.
            output_dir (str): path to directory where solution must be stored.
            output_format (str): file extension for solution files.
            data (list of str): list where the first element is DMU name, all
                other elements are coefficients.

        Args:
            params (Parameters): parameters.
            sheet_name_usr (str): sheet name from which input data must be read.
            output_format (str): file extension for solution files.
            output_dir (str, optional): path to directory where solution must
                be stored. If not given, solution will be stored to current
                directory.
    '''
    def __init__(self, params, sheet_name_usr, output_format, output_dir=''):
        self.params = params
        self.sheet_name_usr = sheet_name_usr
        self.output_dir = output_dir
        self.output_format = output_format
        self.data = []

    def get_categories(self):
        ''' See base class.
        '''
        categories, self.data, dmu_name, sheet_name = read_data(
            self.params.get_parameter_value('DATA_FILE'),
            self.sheet_name_usr)
        return categories

    def get_coefficients(self):
        ''' See base class.
        '''
        return convert_to_dictionary(self.data)

    def show_error(self, message):
        ''' See base class.
        '''
        logger = get_logger()
        logger.error(message)
        print(message)

    def validate_weights_if_needed(self):
        ''' See base class.
        '''
        pass

    def init_before_run(self, nb_models, coefficients):
        ''' See base class.
        '''
        pass

    def decorate_model(self, model_obj):
        ''' See base class.
        '''
        return model_obj

    def show_success(self):
        ''' Displays success message on screen.
        '''
        print('*************************************')
        print('Successfully solved given DEA models.')

    def post_process_solutions(self, solutions, params, param_strs, all_ranks,
                               run_date, total_seconds):
        ''' See base class.
        '''
        output_file = auto_name_if_needed(self.params, self.output_format,
                                          self.output_dir)
        if output_file:
            categorical = self.params.get_parameter_value(
                'CATEGORICAL_CATEGORY')
            if not categorical.strip():
                categorical = None
            if output_file.endswith('.xlsx'):
                work_book = XlsxWorkbook()
            elif output_file.endswith('.csv'):
                work_book = TxtWriter(os.path.splitext(output_file)[0])
            else:
                raise ValueError('File {0} has unsupported output format'.format
                                 (output_file))
            writer = FileWriter(self.params, work_book, run_date, total_seconds,
                               ranks=all_ranks, categorical=categorical)
            try:
                for count, sol in enumerate(solutions):
                    writer.write_data(sol, param_strs[count])
                work_book.save(output_file)
            except ValueError:
                work_book = TxtWriter(os.path.splitext(output_file)[0])
                writer = FileWriter(self.params, work_book, run_date,
                                   total_seconds, ranks=all_ranks,
                                   categorical=categorical)
                for count, sol in enumerate(solutions):
                    writer.write_data(sol, param_strs[count])
                work_book.save(output_file)


class RunMethodGUI(RunMethodBase):
    ''' This class implements running routing from GUI.

        Attributes:
            frame (Tk Frame): main GUI frame.
            current_dmu (StringVar): StringVar object that tracks when
                when DMU changes during solution process.
            increment (double): progress bar increment.

        Args:
            frame (Tk Frame): main GUI frame.
    '''
    def __init__(self, frame):
        self.frame = frame
        self.current_dmu = None
        self.increment = 0

    def get_categories(self):
        ''' See base class.
        '''
        return self.frame.construct_categories()

    def get_coefficients(self):
        ''' See base class.
        '''
        return self.frame.data_frame.data_tab.read_coefficients()

    def show_error(self, message):
        ''' See base class.
        '''
        logger = get_logger()
        logger.error(message)
        showerror('Error', message)

    def validate_weights_if_needed(self):
        ''' See base class.
        '''
        self.frame.params_frame.weight_tab.on_validate_weights()

    def init_before_run(self, nb_models, coefficients):
        ''' See base class.
        '''
        current_dmu = StringVar()
        current_dmu.trace('w', self.frame.on_dmu_change)
        self.current_dmu = current_dmu
        self.increment = 100 / (len(coefficients) * nb_models)
        self.frame.progress_bar['value'] = 0

    def decorate_model(self, model_obj):
        ''' See base class.
        '''
        model = ProgressBarDecorator(model_obj, self.current_dmu)
        self.frame.increment = self.increment
        return model

    def post_process_solutions(self, solutions, params, param_strs, all_ranks,
                               run_date, total_seconds):
        ''' See base class.
        '''
        categorical = params.get_parameter_value('CATEGORICAL_CATEGORY')
        if not categorical.strip():
            categorical = None

        data_file = self.frame.data_frame.data_tab.get_data_file_name()
        self.frame.data_frame.solution_tab.update_data_file_name(data_file)
        if '*' not in data_file:
            params.update_parameter('DATA_FILE', data_file)

        self.frame.progress_bar['value'] = 100
        self.frame.data_frame.select(1)

        self.frame.data_frame.solution_tab.show_solution(solutions, params,
                                                         param_strs,
                                                         run_date,
                                                         total_seconds,
                                                         ranks=all_ranks,
                                                         categorical=
                                                         categorical)
                                                         

def derive_returns_to_scale_classification(param_strs, solutions):
    ''' Add a dictionary that describes the DMUs' returns-to-scale classification
        to the solution object. Note that for a given orientation (intput or
        ouput), the returns-to-scale of a DMU is the same for both the CRS 
        and the VRS models. See the following algorithm for more detail: 

        For a DMUo
            If CRSeff of DMUo  = VRSeff of DMUo then classify DMUo as CRS
            Else
                If sum of DMUo’s CRS lambdas < 1 then classify DMUo as IRS
                Else classify DMUo as DRS
        Args:
            param_strs (list of str): list of strings that describe
                    each model.
            solutions (list of Solution): list of obtained solutions.            

        Returns:
            RTS_classification (dict of dmu_code (str) to classification (str)): indicate frontier 
                for the DMUs.
    '''

    for orientation in ["input orientation", "output orientation"]:
        solution_crs = None
        solution_vrs = None
        RTS_classification = dict()

        for count, param_str in enumerate(param_strs):
            if param_str == orientation + ", CRS":
                solution_crs = solutions[count]
                solution_crs_count = count
            elif param_str == orientation + ", VRS":
                solution_vrs = solutions[count]
                solution_vrs_count = count
            else:
                pass
        if solution_crs is None or solution_vrs is None:
            # if we cannot find both the crs and vrs model, then continue to
            # the next iteration
            continue
            
        ordered_dmu_codes = solution_crs._input_data.DMU_codes_in_added_order
        for dmu_code in ordered_dmu_codes:
            # check dmu_code exist in both solutions        
            if solution_crs._input_data.DMU_code_to_user_name[dmu_code] != solution_vrs._input_data.DMU_code_to_user_name[dmu_code]:
                raise Exception("Cannot find DMU" + solution_vrs._input_data.DMU_code_to_user_name[dmu_code] + "in the VRS model")
        
            if solution_crs.efficiency_scores[dmu_code] == solution_vrs.efficiency_scores[dmu_code]:
                RTS_classification[dmu_code] = 'CRS'
            else: 
                all_lambda_vars = solution_crs.get_lambda_variables(dmu_code)
                sum_of_lambda = 0
                for dmu_key in all_lambda_vars:
                    sum_of_lambda += all_lambda_vars[dmu_key]
                if sum_of_lambda < 1:
                    RTS_classification[dmu_code] = 'IRS'
                else:
                    RTS_classification[dmu_code] = 'DRS'
            
        solutions[solution_crs_count].return_to_scale = RTS_classification
        solutions[solution_vrs_count].return_to_scale = RTS_classification
        
    return