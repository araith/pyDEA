''' This module contains a base class that implements envelopment model.
'''
import pulp

from pyDEA.core.models.model_base import ModelBase
from pyDEA.core.utils.dea_utils import ZERO_TOLERANCE


class EnvelopmentModelBase(ModelBase):
    ''' This class is a base class for different envelopment models.
        It implements general structure of all envelopment models.
        Concrete variations of envelopment models are passed in the
        class constructor.

        Attributes:
            _concrete_model: concrete implementation of the envelopment
                model.
            _constraint_creator: object that creates a proper
                constraint depending on presence of
                disposable variables.
            _variables (dict of str to pulp.LpVariable): dictionary of pulp
                variables than maps variable names to pulp variables.
            _constraints (dict of str to str): dictionary that maps name of
                the category to the name of the corresponding constraint.
            _should_add_efficiency (bool): if set to False, previously
                stored efficiency score is used. This variable is changed
                in two phase model.

        Args:
            input_data (InputData): object that stores all data of
                a DEA instance.
            concrete_model: concrete implementation of the envelopment
                model.
            constraint_creator: object that creates a proper
                constraint depending on presence of disposable variables.
    '''
    def __init__(self, input_data, concrete_model, constraint_creator):
        super(EnvelopmentModelBase, self).__init__(input_data)
        self._concrete_model = concrete_model
        self._constraint_creator = constraint_creator
        self._variables = dict()
        self._constraints = dict()
        self._should_add_efficiency = True

    def _create_lp(self):
        ''' Creates initial linear program.
        '''
        assert len(self.input_data.DMU_codes) != 0
        self._variables.clear()
        self._constraints.clear()
        # create LP for the first DMU - it is the easiest way to
        # adapt current code
        for elem in self.input_data.DMU_codes:
            dmu_code = elem
            break

        orientation = self._concrete_model.get_orientation()
        obj_type = self._concrete_model.get_objective_type()
        self.lp_model = pulp.LpProblem('Envelopment model: {0}-'
                                       'oriented'.format(orientation),
                                       obj_type)
        ub_obj = self._concrete_model.get_upper_bound_for_objective_variable()
        obj_variable = pulp.LpVariable('Variable in objective function',
                                       self._concrete_model.
                                       get_lower_bound_for_objective_variable(),
                                       ub_obj,
                                       pulp.LpContinuous)
        self._variables['obj_var'] = obj_variable

        self.lp_model += (obj_variable,
                          'Efficiency score or inverse of efficiency score')

        lambda_variables = pulp.LpVariable.dicts('lambda',
                                                 self.input_data.DMU_codes,
                                                 0, None, pulp.LpContinuous)
        self._variables.update(lambda_variables)
        self._add_constraints_for_outputs(lambda_variables, dmu_code,
                                          obj_variable)
        self._add_constraints_for_inputs(lambda_variables, dmu_code,
                                         obj_variable)

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        for output_category in self.input_data.output_categories:
            constraint_name = self._constraints[output_category]
            current_output = self.input_data.coefficients[(dmu_code,
                                                          output_category)]
            constraint = self.lp_model.constraints[constraint_name]
            self._concrete_model.update_output_category_coefficient(
                current_output, constraint, self._variables['obj_var'],
                output_category)
        for input_category in self.input_data.input_categories:
            current_input = self.input_data.coefficients[(dmu_code,
                                                         input_category)]
            constraint_name = self._constraints[input_category]
            constraint = self.lp_model.constraints[constraint_name]
            self._concrete_model.update_input_category_coefficient(
                current_input, constraint, self._variables['obj_var'],
                input_category)

    def _add_constraints_for_outputs(self, variables, dmu_code,
                                     obj_variable):
        ''' Adds constraints for outputs to linear program.

            Args:
                variables (dict of str to pulp.LpVariable): a dictionary
                    that maps DMU codes to pulp.LpVariable, created with
                    pulp.LpVariable.dicts.
                dmu_code (str): DMU code for which LP is being created.
                obj_variable (pulp.LpVariable): LP variable that is optimised
                    (either efficiency score or inverse of efficiency score).
        '''
        for (count, output_category) in enumerate(
                self.input_data.output_categories):
            current_output = self.input_data.coefficients[(dmu_code,
                                                          output_category)]
            output_coeff = self._concrete_model.get_output_variable_coefficient(
                obj_variable, output_category)
            sum_all_outputs = pulp.lpSum([variables[dmu] *
                                         self.input_data.coefficients
                                         [(dmu, output_category)]
                                         for dmu in self.input_data.DMU_codes])
            name = 'constraint_output_{count}'.format(count=count)
            self.lp_model += (self._constraint_creator.create(
                              -output_coeff * current_output +
                              sum_all_outputs, 0, output_category), name)
            self._constraints[output_category] = name

    def _add_constraints_for_inputs(self, variables,
                                    dmu_code, obj_variable):
        ''' Adds constraints for inputs to LP.

            Args:
                variables (dict of {str: pulp.LpVariable}): a dictionary that
                    maps DMU codes to pulp.LpVariable, created with
                    pulp.LpVariable.dicts.
                dmu_code (str): DMU code for which LP is being created.
                obj_variable (pulp.LpVariable): LP variable that is optimised
                    (either efficiency score or inverse of efficiency score).
        '''
        for (count, input_category) in enumerate(
                self.input_data.input_categories):
            current_input = self.input_data.coefficients[(dmu_code,
                                                         input_category)]
            input_coeff = self._concrete_model.get_input_variable_coefficient(
                obj_variable, input_category)
            sum_all_inputs = pulp.lpSum([variables[dmu] *
                                        self.input_data.coefficients
                                        [(dmu, input_category)]
                                        for dmu in
                                        self.input_data.DMU_codes])
            name = 'constraint_input_{count}'.format(count=count)
            self.lp_model += (self._constraint_creator.create(
                              input_coeff * current_input
                              - sum_all_inputs, 0, input_category), name)
            self._constraints[input_category] = name

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
            lambda_variables = dict()
            for dmu in self.input_data.DMU_codes:
                var = self._variables.get(dmu, None)
                if (var is not None and var.varValue is not None and
                        abs(var.varValue) > ZERO_TOLERANCE):
                    lambda_variables[dmu] = var.varValue

            if self._should_add_efficiency:
                model_solution.add_efficiency_score(
                    dmu_code, self._concrete_model.process_obj_var
                    (pulp.value(self.lp_model.objective)))
                
            model_solution.add_lambda_variables(dmu_code, lambda_variables)
            self._process_duals(dmu_code, self.input_data.input_categories,
                                model_solution.add_input_dual)
            self._process_duals(dmu_code, self.input_data.output_categories,
                                model_solution.add_output_dual)

    def _process_duals(self, dmu_code, categories, func):
        ''' Helper function that adds duals to solution using given method func.
            Helps to avoid code duplication.

            Args:
                dmu_code (str): DMU code under consideration.
                categories (list of str): list of either input or output
                    categories.
                func (function): a function that accepts DMU code, category and
                    dual variable value and adds it to solution.
        '''
        for category in categories:
            constraint_name = self._constraints[category]
            dual = self._concrete_model.process_dual_value(
                self.lp_model.constraints[constraint_name].pi)
            func(dmu_code, category, dual)
