''' This module contains classes that implement various
    objects for storing solutions.

    Attributes:
        _solution_id (int): global variable used for generating
            solution IDs.
'''

from pulp import LpStatus, LpStatusOptimal
import pickle
import os

from pyDEA.core.utils.dea_utils import is_efficient, TMP_FOLDER

_solution_id = 0


class Solution(object):
    ''' This class implements basic solution.

        Attributes:
            _solution_id (int): solution ID.
            orientation (str): problem orientation, can take values
                input or output.
            _input_data (InputData): object that stores input data.
            efficiency_scores (dict of str to double): dictionary that maps
                DMU code to efficiency spyDEA.core.
            lp_status (dict of str to pulp.LpStatus): dictionary that maps
                DMU code to LP status (optimal, unbounded, etc).
            input_duals (dict of str to dict of str to double): dictionary
                that maps DMU code to another dictionary that maps input
                category name to value of dual variable.
            output_duals (dict of str to dict of str to double): dictionary
                that maps DMU code to another dictionary that maps output
                category name to value of dual variable.
            return_to_scale (dict of str to str): dictionary that maps DMU code
                to the return-to-scale of the DMU

        Args:
            input_data (InputData): object that stores input data.
    '''
    def __init__(self, input_data):

        global _solution_id
        _solution_id += 1
        self._solution_id = _solution_id
        self.orientation = ''
        self._input_data = input_data

        self.efficiency_scores = dict()
        self.lp_status = dict()
        self.input_duals = dict()
        self.output_duals = dict()
        self.return_to_scale = dict()
        for dmu_code in input_data.DMU_codes:
            self.input_duals[dmu_code] = dict()
            self.output_duals[dmu_code] = dict()

        if not os.path.exists(TMP_FOLDER):
            os.makedirs(TMP_FOLDER)

    def add_efficiency_score(self, dmu_code, efficiency_score):
        ''' Adds efficiency score of a given DMU to internal
            data structure.

            Args:
                dmu_code (str): DMU code.
                efficiency_score (double): efficiency spyDEA.core.

            Raises:
                ValueError: if dmu_code does not exist or has invalid
                    value.
        '''
        self._check_efficiency_score(efficiency_score)
        self._check_if_dmu_code_exists(dmu_code)
        self.efficiency_scores[dmu_code] = efficiency_score

    def _check_efficiency_score(self, efficiency_score):
        ''' Checks if efficiency score has a valid value.

            Args:
                efficiency_score (double): efficiency spyDEA.core.

            Raises:
                ValueError: if efficiency score has invalid value.
        '''
        if efficiency_score < 0 or efficiency_score > 1:
            raise ValueError('Efficiency score must be within [0, 1]')

    def get_efficiency_score(self, dmu_code):
        ''' Returns efficiency score of a given DMU.

            Args:
                dmu_code (str): DMU code.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self.efficiency_scores[dmu_code]

    def is_efficient(self, dmu_code, lambda_variables=None):
        ''' Checks if a given DMU is efficient.

            Args:
                dmu_code (str): DMU code.
                lambda_variables (dict of str to double, optional): dictionary
                    that maps DMU codes to the corresponding value
                    of lambda variables. If it is not given, it will be loaded
                    from a pickled file.

            Returns:
                bool: True if a given DMU is efficient, False otherwise.
        '''
        if self.lp_status[dmu_code] != LpStatusOptimal:
            return False
        file_name = self._get_pickle_name(dmu_code)
        if not lambda_variables:
            lambda_variables = pickle.load(open(file_name, 'rb'))
        return is_efficient(self.get_efficiency_score(dmu_code),
                            lambda_variables.get(dmu_code, 0))

    def add_lambda_variables(self, dmu_code, variables):
        ''' Adds lambda variables corresponding to a given DMU
            to pickled file.

            Args:
                dmu_code (str): DMU code.
                variables (dict of str to double): dictionary
                    that maps DMU codes to the corresponding value
                    of lambda variables.

            Raises:
                ValueError: if DMU code does not exist or
                    if number of lambda variables is not equal
                    to total number of DMU codes, or
                    if variables contain keys that are not existing DMU codes.
        '''
        self._check_if_dmu_code_exists(dmu_code)
        self._validate_lambda_variables(variables)
        with open(self._get_pickle_name(dmu_code), 'wb') as f:
            pickle.dump(variables, f)

    def get_lambda_variables(self, dmu_code):
        ''' Returns lambda variables corresponding to a given DMU.

            Args:
                dmu_code (str): DMU code.

            Returns:
                dict of str to double: lambda variables.
        '''
        file_name = self._get_pickle_name(dmu_code)
        return pickle.load(open(file_name, 'rb'))

    def _get_pickle_name(self, dmu_code):
        ''' Generates a unique name for pickled file with lambda
            variables.

            Args:
                dmu_code (str): DMU code.

            Returns:
                str: generated file name.
        '''
        file_name = 'lambda{0}_{1}.p'.format(self._solution_id, dmu_code)
        return os.path.join(TMP_FOLDER, file_name)

    def _check_if_dmu_code_exists(self, dmu_code):
        ''' Checks if a given DMU code exists.

            Args:
                dmu_code (str): DMU code.

            Raises:
                ValueError: if a given DMU code does not exist.
        '''
        if dmu_code not in self._input_data.DMU_codes:
            raise ValueError('DMU code {dmu} does not exist'.format(
                dmu=dmu_code))

    def _validate_lambda_variables(self, variables):
        ''' Checks if variables contain existing DMU codes as keys.

            Args:
                variables (dict of str to double): dictionary
                    that maps DMU codes to the corresponding value
                    of lambda variables.

            Raises:
                ValueError: if variables contain non-existing DMU codes.
        '''
        for key in variables.keys():
            self._check_if_dmu_code_exists(key)

    def add_input_dual(self, dmu_code, input_category, dual_value):
        ''' Adds value of a dual variable associated with a given input category
            and DMU code to internal data structure.

            Args:
                dmu_code (str): DMU code.
                input_category (str): input category name.
                dual_value (double): value of a dual variable.

            Raises:
                ValueError: if a given category is not a valid input category.
        '''
        self._check_if_dmu_code_exists(dmu_code)
        if input_category not in self._input_data.input_categories:
            raise ValueError('{category} is not a valid input category'.format(
                category=input_category))
        self.input_duals[dmu_code][input_category] = dual_value

    def add_output_dual(self, dmu_code, output_category, dual_value):
        ''' Adds value of a dual variable associated with a given output
            category and DMU code to internal data structure.

            Args:
                dmu_code (str): DMU code.
                output_category (str): output category name.
                dual_value (double): value of a dual variable.

            Raises:
                ValueError: if a given category is not a valid output category.
        '''
        self._check_if_dmu_code_exists(dmu_code)
        if output_category not in self._input_data.output_categories:
            raise ValueError('{category} is not a valid output category'.format(
                             category=output_category))
        self.output_duals[dmu_code][output_category] = dual_value

    def get_input_dual(self, dmu_code, input_category):
        ''' Returns dual variable value corresponding to a given DMU and
            input category.

            Args:
                dmu_code (str): DMU code.
                input_category (str): input category name.

            Returns:
                double: dual variable value.
        '''
        return self.input_duals[dmu_code][input_category]

    def get_output_dual(self, dmu_code, output_category):
        ''' Returns dual variable value corresponding to a given DMU and
            output category.

            Args:
                dmu_code (str): DMU code.
                output_category (str): output category name.

            Returns:
                double: dual variable value.
        '''
        return self.output_duals[dmu_code][output_category]

    def add_lp_status(self, dmu_code, lp_status):
        ''' Adds LP status corresponding to a given DMU to internal
            data structure.

            Args:
                dmu_code (str): DMU code.
                lp_status (pulp.LpStatus): LP status.
        '''
        self._check_if_dmu_code_exists(dmu_code)
        self.lp_status[dmu_code] = lp_status

    def _print_for_one_dmu(self, dmu_code):
        ''' Prints on screen all information available for a given DMU.

            Args:
               dmu_code (str): DMU code.
        '''
        print('DMU: {dmu}'.format(
            dmu=self._input_data.get_dmu_user_name(dmu_code)))
        print('code: ', dmu_code)
        if self.lp_status.get(dmu_code):
            print('LP status: {status}'.format(
                status=LpStatus[self.lp_status.get(dmu_code)]))
            if self.lp_status.get(dmu_code) == LpStatusOptimal:
                print('Efficiency score: {score}'.format(
                    score=self.efficiency_scores.get(dmu_code)))
                print('Lambda variables: {vars}'.format(
                    vars=self.get_lambda_variables(dmu_code)))
                print('Input duals: {duals}'.format(
                    duals=self.input_duals.get(dmu_code)))
                print('Output duals: {duals}'.format(
                    duals=self.output_duals.get(dmu_code)))

    def print_solution(self):
        ''' Prints all data on the screen.
        '''
        for dmu_code in self._input_data.DMU_codes:
            self._print_for_one_dmu(dmu_code)


class SolutionWithVRS(object):
    ''' This class decorate Solution with VRS variables to store their values
        for VRS DEA models.

        Attributes:
            _model_solution (Solution): solution that should be decorated
                with VRS variables.
            vrs_duals (dict of str to double): dictionary that maps DMU code
                to VRS variable value.

        Args:
            model_solution (Solution): solution that should be decorated
                with VRS variables.
    '''
    def __init__(self, model_solution):
        self._model_solution = model_solution
        self.vrs_duals = dict()

    def __getattr__(self, name):
        return getattr(self._model_solution, name)

    def add_VRS_dual(self, dmu_code, value):
        ''' Adds VRS variable value corresponding to a given DMU to
            internal data structure.

            Args:
                dmu_code (str): DMU code.
                value (double): value of the VRS variable.
        '''
        self._model_solution._check_if_dmu_code_exists(dmu_code)
        self.vrs_duals[dmu_code] = value

    def get_VRS_dual(self, dmu_code):
        ''' Returns value of a VRS variable corresponding to a given
            DMU.

            Args:
                dmu_code (str): DMU code.

            Returns:
                double: value of the VRS variable.
        '''
        return self.vrs_duals[dmu_code]

    def _print_for_one_dmu(self, dmu_code):
        ''' Prints on screen all information available for a given DMU.

            Args:
               dmu_code (str): DMU code.
        '''
        self._model_solution._print_for_one_dmu(dmu_code)
        print('VRS variable: {vrs}'.format(vrs=self.vrs_duals.get(dmu_code)))

    def print_solution(self):
        ''' Prints all data on the screen.
        '''
        for dmu_code in self._input_data.DMU_codes:
            self._print_for_one_dmu(dmu_code)


class SolutionWithSuperEfficiency(Solution):
    ''' This class redefines one method of :class:`Solution` to accept
        efficiency scores greater than 1.
    '''
    def _check_efficiency_score(self, efficiency_score):
        ''' Redefines method of :class:`Solution` to accept
            efficiency scores greater than 1.

            Args:
                efficiency_score (double): efficiency score

            Raises:
                ValueError: if efficiency score is less than 0
        '''
        if efficiency_score < 0:
            raise ValueError('Efficiency score must be >= 0')

    def _check_if_dmu_code_exists(self, dmu_code):
        ''' In the case of super efficiency, current DMU for which LP
            is being created cannot be peer to itself. This method
            does not raise
            an error if given DMU code does not belong to the set of DMUs.
        '''
        pass

    def is_efficient(self, dmu_code, lambda_variables=None):
        ''' Returns True if a given DMU is efficient,
            False otherwise.

            We have to redefine this method in the case of super efficiency,
            because now any DMU with efficiency score >= 1 is considered
            efficient.

            Args:
                dmu_code (str): internal code of DMU.
                lambda_variables (dict of str to double, optional): dictionary
                    that maps DMU codes to the corresponding value
                    of lambda variables. It is ignored in this class.

            Returns:
                bool: True if a given DMU is efficient, False otherwise.

            Example:
                >>> s = SolutionWithSuperEfficiency()
                >>> s.add_efficiency_score('dmu_1', 1.2)
                >>> s.is_efficient('dmu_1')
                True
                >>> s.add_efficiency_score('dmu_2', 0.5)
                >>> s.is_efficient('dmu_2')
                False
                >>> s.add_efficiency_score('dmu_3', 0.9999999)
                >>> s.is_efficient('dmu_3')
                False

        '''
        if self.get_efficiency_score(dmu_code) >= 1:
            return True
        return False
