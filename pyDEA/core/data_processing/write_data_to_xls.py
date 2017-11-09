''' This module contains functions and classes responsible for
    writing solutions into different outputs (files, screen, GUI, etc).
    All names start with XLS because originally only xls-files were supported.

    Warning:
        if new methods for writing output are added, they MUST
        follow the rule: data must be added
        sequentially, row after row, column after column.
'''

import pulp
from itertools import chain
from collections import defaultdict

from pyDEA.core.utils.dea_utils import ZERO_TOLERANCE
from pyDEA.core.data_processing.targets_and_slacks import calculate_target
from pyDEA.core.data_processing.targets_and_slacks import calculate_radial_reduction
from pyDEA.core.data_processing.targets_and_slacks import calculate_non_radial_reduction
from pyDEA.core.utils.progress_recorders import NullProgress


class XLSSheetWithParameters(object):
    ''' Writes parameters to a given output.

        Attributes:
            params (Parameters): parameters.
            run_date (datetime): date and time when the problem was solved.
            total_seconds (float): time (in seconds) needed to solve
                the problem.

        Args:
            params (Parameters): parameters.
            run_date (datetime): date and time when the problem was solved.
            total_seconds (float): time (in seconds) needed to solve
                the problem.
    '''
    def __init__(self, params, run_date, total_seconds):
        self.params = params
        self.run_date = run_date
        self.total_seconds = total_seconds

    def create_sheet_parameters(self, work_sheet, solution, start_row_index,
                                params_str):
        ''' Writes parameters to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        work_sheet.name = 'Parameters'

        work_sheet.write(start_row_index, 0, 'Run date and time:')
        work_sheet.write(start_row_index, 1, self.run_date.strftime('%c'))
        work_sheet.write(start_row_index + 1, 0, 'Calculation time:')
        work_sheet.write(start_row_index + 1, 1, '{0} seconds'.format(
            self.total_seconds))
        work_sheet.write(start_row_index + 2, 0, 'Parameter name')
        work_sheet.write(start_row_index + 2, 1, 'Value')
        row_index = start_row_index + 3
        for param_name, param_value in self.params.params.items():
            work_sheet.write(row_index, 0, param_name)
            work_sheet.write(row_index, 1, param_value)
            row_index += 1
        return row_index


class XLSSheetOnionRank(object):
    ''' Writes information about peel the onion solution to a given output.

        Attributes:
            ranks (list of dict of str to double):
                list that contains dictionaries that map DMU code
                to peel the onion rank.

        Args:
            ranks (list of dict of str to double):
                list that contains dictionaries that map DMU code
                to peel the onion rank.
    '''
    def __init__(self, ranks):
        self.ranks = ranks
        self.count = 0

    def create_sheet_onion_rank(self, work_sheet, solution, start_row_index,
                                params_str):
        ''' Writes information about peel the onion solution to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        work_sheet.name = 'OnionRank'
        # in case of max_slacks and peel-the-onion we should not
        # write ranks twice
        if self.count < len(self.ranks):

            work_sheet.write(start_row_index, 0, params_str)
            work_sheet.write(
                start_row_index + 1, 0,
                'Tier / Rank is the run in which DMU became efficient')
            work_sheet.write(start_row_index + 2, 0, 'DMU')
            work_sheet.write(start_row_index + 2, 1, 'Efficiency')
            work_sheet.write(start_row_index + 2, 2, 'Tier / Rank')
            ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
            row_index = start_row_index + 3
            for dmu_code in ordered_dmu_codes:
                work_sheet.write(
                    row_index, 0,
                    solution._input_data.get_dmu_user_name(dmu_code))
                if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
                    work_sheet.write(row_index, 1,
                                     solution.get_efficiency_score(dmu_code))
                    work_sheet.write(row_index, 2,
                                     self.ranks[self.count][dmu_code])
                else:
                    work_sheet.write(
                        row_index, 1,
                        pulp.LpStatus[solution.lp_status[dmu_code]])
                row_index += 1
            self.count += 1
            return row_index
        return -1


class XLSSheetWithCategoricalVar(object):
    ''' Writes various solution information to a given output, and
        adds categorical information if necessary.

        Attributes:
            categorical (str): name of categorical category.

        Args:
            categorical (str): name of categorical category.
    '''
    def __init__(self, categorical=None):
        self.categorical = categorical

    def create_sheet_efficiency_scores(self, work_sheet, solution,
                                       start_row_index, params_str):
        ''' Writes efficiency scores to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        work_sheet.name = 'EfficiencyScores'

        work_sheet.write(start_row_index, 0, params_str)
        work_sheet.write(start_row_index + 1, 0, 'DMU')
        work_sheet.write(start_row_index + 1, 1, 'Efficiency')
        if self.categorical is not None:
            work_sheet.write(start_row_index + 1, 2,
                             'Categorical: {0}'.format(self.categorical))

        ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
        row_index = 0
        for count, dmu_code in enumerate(ordered_dmu_codes):
            row_index = start_row_index + count + 2
            work_sheet.write(
                row_index, 0, solution._input_data.get_dmu_user_name(dmu_code))
            if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
                work_sheet.write(
                    row_index, 1, solution.get_efficiency_score(dmu_code))
            else:
                work_sheet.write(
                    row_index, 1, pulp.LpStatus[solution.lp_status[dmu_code]])
            if self.categorical is not None:
                work_sheet.write(
                    row_index, 2,
                    int(solution._input_data.coefficients[
                        dmu_code, self.categorical]))
        return row_index

    def create_sheet_input_output_data_base(self, work_sheet, solution,
                                            get_multiplier,
                                            sheet_name, start_row_index,
                                            params_str):
        ''' Writes input and output weights or weighted data to a given output
            depending on input parameters.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                get_multiplier (func): function that scales weights.
                sheet_name (str): name that will be written into the name
                    attribute of work_sheet.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        work_sheet.name = sheet_name

        work_sheet.write(start_row_index, 0, params_str)
        work_sheet.write(start_row_index + 1, 0, 'DMU')
        work_sheet.write(start_row_index + 1, 1, 'Efficiency')

        init_column_index = 2
        if self.categorical is not None:
            work_sheet.write(start_row_index + 1, 2,
                             'Categorical: {0}'.format(self.categorical))
            init_column_index = 3

        categories = []
        categories.extend(solution._input_data.input_categories)
        categories.extend(solution._input_data.output_categories)

        column_index = init_column_index
        for category in categories:
            work_sheet.write(start_row_index + 1, column_index, category)
            column_index += 1

        try:
            solution.vrs_duals
        except AttributeError:
            pass
        else:
            work_sheet.write(start_row_index + 1,
                             init_column_index + len(categories), 'VRS')

        row_index = start_row_index + 2
        ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
        for dmu_code in ordered_dmu_codes:
            dmu_name = solution._input_data.get_dmu_user_name(dmu_code)
            work_sheet.write(row_index, 0, dmu_name)

            if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
                work_sheet.write(
                    row_index, 1, solution.get_efficiency_score(dmu_code))

            if self.categorical is not None:
                work_sheet.write(
                    row_index, 2,
                    int(solution._input_data.coefficients[
                        dmu_code, self.categorical]))

            if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:

                column_index = init_column_index
                for input_category in solution._input_data.input_categories:
                    work_sheet.write(
                        row_index, column_index,
                        get_multiplier(solution, dmu_code, input_category) *
                        solution.get_input_dual(dmu_code, input_category))
                    column_index += 1

                for output_category in solution._input_data.output_categories:
                    work_sheet.write(
                        row_index, column_index,
                        get_multiplier(solution, dmu_code, output_category) *
                        solution.get_output_dual(dmu_code, output_category))
                    column_index += 1

                try:
                    vrs_dual = solution.get_VRS_dual(dmu_code)
                    work_sheet.write(row_index, column_index, vrs_dual)
                except AttributeError:
                    pass
            else:
                work_sheet.write(
                    row_index, 1, pulp.LpStatus[solution.lp_status[dmu_code]])

            row_index += 1
        return row_index

    @staticmethod
    def _get_const_multiplier(solution, dmu_code, category):
        ''' Helper method that is used for writing input and output data
            to a given output.

            Args:
                solution (Solution): solution.
                dmu_code (str): DMU code.
                category (str): category name.

            Returns:
                int: always returns 1 since we don't need to scale weights.
        '''
        return 1

    def create_sheet_input_output_data(self, work_sheet, solution,
                                       start_row_index, params_str):
        ''' Writes input and output weights to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        return self.create_sheet_input_output_data_base(
            work_sheet, solution,
            self._get_const_multiplier, 'InputOutputWeights',
            start_row_index, params_str)

    @staticmethod
    def _get_data_multiplier(solution, dmu_code, category):
        ''' Helper method that is used for writing weighted data
            to a given output.

            Args:
                solution (Solution): solution.
                dmu_code (str): DMU code.
                category (str): category name.

            Returns:
                int: a scale value to scale weights.
        '''
        return solution._input_data.coefficients[dmu_code, category]

    def create_sheet_weighted_data(self, work_sheet, solution,
                                   start_row_index, params_str):
        ''' Writes weighted data to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        return self.create_sheet_input_output_data_base(
            work_sheet, solution,
            self._get_data_multiplier, 'WeightedData',
            start_row_index, params_str)

    def create_sheet_targets(self, work_sheet, solution, start_row_index,
                             params_str):
        ''' Writes targets to a given output.

            Args:
                work_sheet: object that has name attribute and implements
                    write method, it actually writes data to some output
                    (like file, screen, etc.).
                solution (Solution): solution.
                start_row_index (int): initial row index (usually used to append
                    data to existing output).
                params_str (str): string that is usually written in the first
                    row.

            Returns:
                int: index of the last row where data were written plus 1.
        '''
        work_sheet.name = 'Targets'

        work_sheet.write(start_row_index, 0, params_str)
        work_sheet.write(start_row_index + 1, 0, 'DMU')
        work_sheet.write(start_row_index + 1, 1, 'Category')
        work_sheet.write(start_row_index + 1, 2, 'Original')
        work_sheet.write(start_row_index + 1, 3, 'Target')
        work_sheet.write(start_row_index + 1, 4, 'Radial')
        work_sheet.write(start_row_index + 1, 5, 'Non-radial')
        if self.categorical is not None:
            work_sheet.write(
                start_row_index + 1, 6,
                'Categorical: {0}'.format(self.categorical))

        ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
        row_index = start_row_index + 2
        for dmu_code in ordered_dmu_codes:
            work_sheet.write(
                row_index, 0, solution._input_data.get_dmu_user_name(dmu_code))

            if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:

                once = True
                all_lambda_vars = solution.get_lambda_variables(dmu_code)
                for category in chain(solution._input_data.input_categories,
                                      solution._input_data.output_categories):
                    work_sheet.write(row_index, 1, category)
                    original = solution._input_data.coefficients[
                        dmu_code, category]
                    work_sheet.write(row_index, 2, original)

                    target = calculate_target(category, all_lambda_vars,
                                              solution._input_data.coefficients)
                    radial_reduction = calculate_radial_reduction(
                        dmu_code, category, solution._input_data,
                        solution.get_efficiency_score(dmu_code),
                        solution.orientation)
                    non_radial_reduction = calculate_non_radial_reduction(
                        target, radial_reduction, original)
                    if abs(non_radial_reduction) < ZERO_TOLERANCE:
                            non_radial_reduction = 0

                    work_sheet.write(row_index, 3, target)
                    work_sheet.write(row_index, 4, radial_reduction)
                    work_sheet.write(row_index, 5, non_radial_reduction)

                    if once:
                        if self.categorical is not None:
                            work_sheet.write(
                                row_index, 6,
                                int(solution._input_data.coefficients[
                                    dmu_code, self.categorical]))
                        work_sheet.write(
                            row_index + 1, 0,
                            solution.get_efficiency_score(dmu_code))
                        once = False
                    row_index += 1
            else:
                work_sheet.write(
                    row_index, 1, pulp.LpStatus[solution.lp_status[dmu_code]])

            row_index += 2
        return row_index


class XLSWriter(object):
    ''' This class is responsible for writing solution information
        into a given output.

        Attributes:
            params (Parameters): parameters.
            writer: object that contains several objects that
                have name attribute and implement
                write method, it actually writes data to some output
                (like file, screen, etc.).
            ranks (list of dict of str to double):
                list that contains dictionaries that map DMU code
                to peel the onion rank.
            categorical (str): name of categorical category.
            run_date (datetime): date and time when the problem was solved.
            total_seconds (float): time (in seconds) needed to solve
                the problem.
            params_sheet (XLSSheetWithParameters): object that writes
                parameters to a given output.
            worksheets (list of func): list of functions that will be called
                to write solution information to a given output.
            start_rows (list of int): list of start row indexes for each
                element in worksheets.
            existing_sheets (list of func): contains None references in the
                beginning, but after at least one call to write_data method
                contains a copy of worksheets. It is necessary for appending
                data to the same output.
            print_params (bool): if set to true parameters are written to
                a given output. It ensures that we don't write parameters more
                than once if we should append information to the same output.

        Args:
            params (Parameters): parameters.
            writer: object that contains several objects that
                have name attribute and implement
                write method, it actually writes data to some output
                (like file, screen, etc.).
            run_date (datetime): date and time when the problem was solved.
            total_seconds (float): time (in seconds) needed to solve
                the problem.
            worksheets (list of func, optional): list of functions that will
                be called to write solution information to a given output.
                Defaults to None.
            ranks (list of dict of str to double, optional):
                list that contains dictionaries that map DMU code
                to peel the onion rank. Defaults to None.
            categorical (str, optional): name of categorical category.
                Defaults to None.
    '''
    def __init__(self, params, writer, run_date, total_seconds,
                 worksheets=None, ranks=None, categorical=None):
        self.params = params
        self.writer = writer
        self.ranks = ranks
        self.categorical = categorical
        self.run_date = run_date
        self.total_seconds = total_seconds
        self.params_sheet = None
        if worksheets is not None:
            self.worksheets = worksheets
        else:
            self.worksheets = self.get_default_worksheets()
        self.start_rows = [0]*len(self.worksheets)
        self.existing_sheets = [None]*len(self.worksheets)
        self.print_params = True

    def get_default_worksheets(self):
        ''' Returns a default list of functions that will
            be called to write solution information to a given output.

            Returns:
                list of func: list of functions.
        '''
        sheet_with_categorical_var = XLSSheetWithCategoricalVar(
            self.categorical)
        worksheets = [
            sheet_with_categorical_var.create_sheet_efficiency_scores,
            create_sheet_peers, create_sheet_peer_count,
            sheet_with_categorical_var.create_sheet_input_output_data,
            sheet_with_categorical_var.create_sheet_weighted_data,
            sheet_with_categorical_var.create_sheet_targets]
        if self.ranks:
            onion_rank_sheet = XLSSheetOnionRank(self.ranks)
            worksheets.append(onion_rank_sheet.create_sheet_onion_rank)

        self.params_sheet = XLSSheetWithParameters(
            self.params, self.run_date,
            self.total_seconds).create_sheet_parameters
        return worksheets

    def write_data(self, solution, params_str='',
                   progress_recorder=NullProgress()):
        ''' Writes given solution to a given output.

            Args:
                solution (Solution): solution.
                params_str (str, optional): string that is usually written in
                    the first row. Defaults to empty string.
                progress_recorder (NullProgress, optional): object that
                    shows progress with writing solution to a given output.
                    Defaults to NullProgress.
        '''
        for count, worksheet in enumerate(self.worksheets):
            if self.existing_sheets[count] is None:
                work_sheet = self.writer.add_sheet(
                    'Sheet_{count}'.format(count=count))
                self.existing_sheets[count] = work_sheet
            else:
                work_sheet = self.existing_sheets[count]
            self.start_rows[count] = (worksheet(work_sheet, solution,
                                      self.start_rows[count],
                                      params_str) + 1)
            progress_recorder.increment_step()

        # parameters are printed only once to file
        if self.print_params:
            work_sheet = self.writer.add_sheet(
                'Sheet_{count}'.format(count=count + 1))
            self.params_sheet(work_sheet, solution, 0, '')
            progress_recorder.increment_step()
        self.print_params = False


def _calculate_frontier_classification(sum_of_lambda_values):
    ''' Returns string that describes frontier classification. If
        sum_of_lambda_values is > 1, then classification is DRS.
        If sum_of_lambda_values is < 1, then
        classification is IRS. If sum_of_lambda_values == 1,
        then classification is CRS.

        Args:
            sum_of_lambda_values (double): sum of lambda variables
                values.

        Returns:
            str: frontier classification.
    '''
    if sum_of_lambda_values > 1:
        return 'DRS'
    elif sum_of_lambda_values < 1:
        return 'IRS'
    else:
        return 'CRS'


def create_sheet_peers(work_sheet, solution, start_row_index, params_str):
    ''' Writes peers to a given output.

        Args:
            work_sheet: object that has name attribute and implements
                write method, it actually writes data to some output
                (like file, screen, etc.).
            solution (Solution): solution.
            start_row_index (int): initial row index (usually used to append
                data to existing output).
            params_str (str): string that is usually written in the first
                row.

        Returns:
            int: index of the last row where data were written plus 1.
    '''
    work_sheet.name = 'Peers'

    work_sheet.write(start_row_index, 0, params_str)
    work_sheet.write(start_row_index + 1, 0, 'DMU')
    work_sheet.write(start_row_index + 1, 2, 'Peer')
    work_sheet.write(start_row_index + 1, 3, 'Lambda')
    work_sheet.write(start_row_index + 1, 4, 'Classification')

    ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
    row_index = start_row_index + 2
    for dmu_code in ordered_dmu_codes:
        work_sheet.write(row_index, 0, solution._input_data.get_dmu_user_name(
            dmu_code))
        if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
            lambda_vars = solution.get_lambda_variables(dmu_code)
            sum_of_lambda_values = 0
            once = True
            for dmu, lambda_value in lambda_vars.items():
                if lambda_value:
                    sum_of_lambda_values += lambda_value
            
            for dmu, lambda_value in lambda_vars.items():
                if lambda_value:
                    dmu_name = solution._input_data.get_dmu_user_name(dmu)
                    work_sheet.write(row_index, 2, dmu_name)
                    work_sheet.write(row_index, 3, lambda_value)
                    if once:
                        work_sheet.write(
                            row_index, 4,
                            _calculate_frontier_classification(
                                sum_of_lambda_values))
                        once = False
                    row_index += 1

        else:
            work_sheet.write(
                row_index, 2, pulp.LpStatus[solution.lp_status[dmu_code]])
        row_index += 1
    return row_index


def create_sheet_peer_count(work_sheet, solution, start_row_index, params_str):
    ''' Writes peer counts to a given output.

        Args:
            work_sheet: object that has name attribute and implements
                write method, it actually writes data to some output
                (like file, screen, etc.).
            solution (Solution): solution.
            start_row_index (int): initial row index (usually used to append
                data to existing output).
            params_str (str): string that is usually written in the first
                row.

        Returns:
            int: index of the last row where data were written plus 1.
    '''
    work_sheet.name = 'PeerCount'

    work_sheet.write(start_row_index, 0, params_str)
    ordered_dmu_codes = solution._input_data.DMU_codes_in_added_order
    work_sheet.write(start_row_index + 1, 0, 'Efficient Peers')

    # write names of efficient DMUs first
    column_index = 1
    for dmu_code in ordered_dmu_codes:
        if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
            if solution.is_efficient(dmu_code):
                dmu_name = solution._input_data.get_dmu_user_name(dmu_code)
                work_sheet.write(start_row_index + 1, column_index, dmu_name)
                column_index += 1

    work_sheet.write(start_row_index + 2, 0, 'DMU')
    # continue line by line
    row_index = start_row_index + 3
    nb_peers = defaultdict(int)
    for dmu_code in ordered_dmu_codes:

        dmu_name = solution._input_data.get_dmu_user_name(dmu_code)
        work_sheet.write(row_index, 0, dmu_name)

        if solution.lp_status[dmu_code] == pulp.LpStatusOptimal:
            column_index = 1
            all_lambda_vars = solution.get_lambda_variables(dmu_code)
            for dmu in ordered_dmu_codes:
                if (solution.lp_status[dmu] == pulp.LpStatusOptimal and
                        solution.is_efficient(dmu, all_lambda_vars)):
                    # get is used since some lambda
                    # # variables might not be present in categorical model!
                    lambda_value = all_lambda_vars.get(dmu, 0)
                    if lambda_value:
                        work_sheet.write(row_index, column_index, lambda_value)
                        nb_peers[dmu] += 1
                    else:
                        work_sheet.write(row_index, column_index, '-')
                    column_index += 1
        else:
            work_sheet.write(
                row_index, 1, pulp.LpStatus[solution.lp_status[dmu_code]])
        row_index += 1
    work_sheet.write(row_index, 0, 'Peer count')
    column_index = 1
    for dmu_code in ordered_dmu_codes:
        if dmu_code in nb_peers.keys():
            work_sheet.write(row_index, column_index, nb_peers[dmu_code])
            column_index += 1
    return row_index
