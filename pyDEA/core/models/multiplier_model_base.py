''' This module contains MultiplierModelBase class that
    implements basic functionality of the multiplier model.
'''
import pulp

from pyDEA.core.models.model_base import ModelBase
from pyDEA.core.utils.dea_utils import is_efficient, ZERO_TOLERANCE


class MultiplierModelBase(ModelBase):
    ''' This class is a base class for different multiplier models.
        It implements general structure of all multiplier models.
        Concrete variations of multiplier models are passed in the
        class constructor.

        Attributes:
            tolerance (double): lower bound of the variables of multilier
                model.
            _concrete_model: concrete implementation of the multiplier
                model.
            _input_variables (dict of str to pulp.LpVariable): dictionary of
                pulp variables than maps variable names to pulp variables
                corresponding to input categories.
            _output_variables (dict of str to pulp.LpVariable): dictionary of
                pulp variables than maps variable names to pulp variables
                corresponding to output categories.
            _dmu_constraint_names (dict of str to str): dictionary that maps
                constraint names to DMU code.

        Args:
            input_data (InputData): object that stores all data of
                a DEA instance.
            tolerance (double): lower bound of the variables of multilier
                model.
            concrete_model: concrete implementation of the multiplier
                model.
    '''
    def __init__(self, input_data, tolerance, concrete_model):
        super(MultiplierModelBase, self).__init__(input_data)
        self.tolerance = tolerance
        self._concrete_model = concrete_model
        self._input_variables = dict()
        self._output_variables = dict()
        self._dmu_constraint_names = dict()

    def _create_lp(self):
        ''' Creates initial LP model.
        '''
        assert len(self.input_data.DMU_codes) != 0
        # create LP for the first DMU - it is the easiest way to
        # adapt current code
        for elem in self.input_data.DMU_codes:
            dmu_code = elem
            break

        self.lp_model = pulp.LpProblem(
            'Multiplier model: {orientation}-oriented'.format(
            orientation=self._concrete_model.get_orientation()),
            self._concrete_model.get_objective_type())

        self._output_variables = pulp.LpVariable.dicts(
            'mu', self.input_data.output_categories, self.tolerance, None,
            pulp.LpContinuous)
        self._input_variables = pulp.LpVariable.dicts(
            'eta', self.input_data.input_categories, self.tolerance, None,
            pulp.LpContinuous)

        self.lp_model += (self._concrete_model.get_objective_function(
            self.input_data, dmu_code, self._input_variables,
            self._output_variables),
            'Efficiency score or inverse of efficiency score')

        self._dmu_constraint_names.clear()
        for dmu in self.input_data.DMU_codes:
            output_sum = pulp.lpSum([self.input_data.coefficients[
                dmu, category] * self._output_variables[category]
                for category in self.input_data.output_categories])
            input_sum = pulp.lpSum([self.input_data.coefficients[
                dmu, category] * self._input_variables[category]
                for category in self.input_data.input_categories])
            name = 'DMU_constraint_{count}'.format(count=dmu)
            self.lp_model += (output_sum - input_sum <= 0, name)
            self._dmu_constraint_names[name] = dmu

        self.lp_model += (self._concrete_model.get_equality_constraint(
            self.input_data, dmu_code, self._input_variables,
            self._output_variables), 'equality_constraint')

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._concrete_model.update_objective(self.input_data, dmu_code,
                                              self._input_variables,
                                              self._output_variables,
                                              self.lp_model)
        self._concrete_model.update_equality_constraint(self.input_data,
                                                        dmu_code,
                                                        self._input_variables,
                                                        self._output_variables,
                                                        self.lp_model)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        model_solution.orientation = self._concrete_model.get_orientation()
        model_solution.add_lp_status(dmu_code, self.lp_model.status)
        if self.lp_model.status == pulp.LpStatusOptimal:
            for input_category in self.input_data.input_categories:
                model_solution.add_input_dual(
                    dmu_code, input_category,
                    self._input_variables[input_category].varValue)

            for output_category in self.input_data.output_categories:
                model_solution.add_output_dual(
                    dmu_code, output_category,
                    self._output_variables[output_category].varValue)
            lambda_variables = dict()
            for dmu_constraint, dmu in self._dmu_constraint_names.items():
                if self.lp_model.constraints[dmu_constraint].pi is None:
                    self.lp_model.constraints[dmu_constraint].pi = 0
                # else:
                #     print(self.lp_model.constraints[dmu_constraint].pi)
                if (abs(self.lp_model.constraints[dmu_constraint].pi) >
                        ZERO_TOLERANCE):
                    lambda_variables[dmu] = self._concrete_model.process_dual_value(
                        self.lp_model.constraints[dmu_constraint].pi)
            lambda_var = lambda_variables.get(dmu_code, 0)
            model_solution.add_efficiency_score(
                dmu_code, self._get_efficiency_score(lambda_var))
            # print('lambda_variables: {0}'.format(lambda_variables))
            model_solution.add_lambda_variables(dmu_code, lambda_variables)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        eff_score = self._concrete_model.process_obj_var(pulp.value(
            self.lp_model.objective))
        # None is possible when objective function is zero
        if eff_score is None:
            eff_score = 0
        if is_efficient(eff_score, lambda_variable):
            eff_score = 1
        return eff_score
