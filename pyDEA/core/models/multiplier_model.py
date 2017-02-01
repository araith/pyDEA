''' This module contains classes that implement input- and
    output-oriented multiplier models.
'''
import pulp

from pyDEA.core.models.input_output_model_bases import InputOrientedModel
from pyDEA.core.models.input_output_model_bases import OutputOrientedModel


class MultiplierInputOrientedModel(InputOrientedModel):
    ''' Implements input-oriented multiplier model.
    '''
    def get_objective_type(self):
        ''' Returns pulp.LpMaximize - we maximize objective function in case
            of input-oriented multiplier model.

            Returns:
                pulp.LpMaximize.
        '''
        return pulp.LpMaximize

    def get_objective_function(self, input_data, dmu_code, input_variables,
                               output_variables):
        ''' Generates objective function of input-oriented multiplier model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.

            Returns:
                pulp.LpSum: objective function.
        '''
        return pulp.lpSum([input_data.coefficients[dmu_code, category] *
                          output_variables[category]
                          for category in input_data.output_categories])

    def update_objective(self, input_data, dmu_code, input_variables,
                         output_variables, lp_model):
        ''' Updates coefficients of the objective function of a given model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.
                lp_model (pulp.LpProblem): linear programming model.
        '''
        for category in input_data.output_categories:
            lp_model.objective[output_variables[category]] = input_data.coefficients[
                dmu_code, category]

    def get_equality_constraint(self, input_data, dmu_code, input_variables,
                                output_variables):
        ''' Generates equality constraint of input-oriented multiplier model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.

            Returns:
                pulp.LpConstraint: equality constraint.
        '''
        return pulp.lpSum([input_data.coefficients[dmu_code, category] *
                          input_variables[category]
                          for category in input_data.input_categories]) == 1

    def update_equality_constraint(self, input_data, dmu_code, input_variables,
                                   output_variables, lp_model):
        ''' Updates coefficients of the equality constraint of a given model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.
                lp_model (pulp.LpProblem): linear programming model.
        '''
        for category, var in input_variables.items():
            lp_model.constraints['equality_constraint'][var] = input_data.coefficients[
                dmu_code, category]


class MultiplierOutputOrientedModel(OutputOrientedModel):
    ''' Implements output-oriented multiplier model.
    '''
    def get_objective_type(self):
        ''' Returns pulp.LpMinimize - we minimize objective function in case
            of output-oriented multiplier model.

            Returns:
                pulp.LpMinimize.
        '''
        return pulp.LpMinimize

    def get_objective_function(self, input_data, dmu_code, input_variables,
                               output_variables):
        ''' Generates objective function of output-oriented multiplier model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.

            Returns:
                pulp.LpSum: objective function.
        '''
        return pulp.lpSum([input_data.coefficients[dmu_code, category] *
                          input_variables[category]
                          for category in input_data.input_categories])

    def update_objective(self, input_data, dmu_code, input_variables,
                         output_variables, lp_model):
        ''' Updates coefficients of the objective function of a given model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.
                lp_model (pulp.LpProblem): linear programming model.
        '''
        for category in input_data.input_categories:
            lp_model.objective[input_variables[category]] = input_data.coefficients[
                dmu_code, category]

    def get_equality_constraint(self, input_data, dmu_code, input_variables,
                                output_variables):
        ''' Generates equality constraint of output-oriented multiplier model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.

            Returns:
                pulp.LpConstraint: equality constraint.
        '''
        return pulp.lpSum([input_data.coefficients[dmu_code, category] *
                          output_variables[category]
                          for category in input_data.output_categories]) == 1

    def update_equality_constraint(self, input_data, dmu_code, input_variables,
                                   output_variables, lp_model):
        ''' Updates coefficients of the equality constraint of a given model.

            Args:
                input_data (InputData): object that stores input data.
                dmu_code (str): DMU code.
                input_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to input categories.
                output_variables (dict of str to pulp.LpVariable): dictionary
                    that maps variable name to pulp variable corresponding
                    to output categories.
                lp_model (pulp.LpProblem): linear programming model.
        '''
        for category, var in output_variables.items():
            lp_model.constraints['equality_constraint'][var] = input_data.coefficients[
                dmu_code, category]
