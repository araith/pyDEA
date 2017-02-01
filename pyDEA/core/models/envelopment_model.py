''' This module contains concrete implementations of input- and
    output-oriented envelopment models as well as the model with
    non-discretionary variables.
'''
import pulp

from pyDEA.core.models.input_output_model_bases import InputOrientedModel
from pyDEA.core.models.input_output_model_bases import OutputOrientedModel


class EnvelopmentModelInputOriented(InputOrientedModel):
    ''' This class defines methods specific to input-oriented envelopment
        model.

        Attributes:
            upper_bound_generator (function): function that
                generates an upper bound on efficiency scores for
                envelopment model, see :mod:`refactored.bound_generators`

        Args:
            upper_bound_generator (function): function that
                generates an upper bound on efficiency scores for
                envelopment
                model, see :mod:`refactored.bound_generators`.
    '''
    def __init__(self, upper_bound_generator):
        self.upper_bound_generator = upper_bound_generator

    def get_upper_bound_for_objective_variable(self):
        ''' Returns a proper upper bound on efficiency score which
            is minimized in the case of input-oriented envelopment model.

            Returns:
                double: upper bound on efficiency spyDEA.core.
        '''
        return self.upper_bound_generator()

    def get_lower_bound_for_objective_variable(self):
        ''' Returns 0 which is the lower bound on efficiency score which
            is minimized in the case of input-oriented envelopment model.

            Returns:
                double: zero.
        '''
        return 0

    def get_objective_type(self):
        ''' Returns pulp.LpMinimize - we minimize objective function in case
            of input-oriented envelopment model.

            Returns:
                pulp.LpMaximize: type of objective function.
        '''
        return pulp.LpMinimize

    def get_output_variable_coefficient(self, obj_variable, output_category):
        ''' Returns 1, since in input-oriented model we do not multiply
            current output by anything.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to output category of the current DMU.
                output_category (str): output category for which current
                    constraint is being created.

            Returns:
                double: output variable coefficient.
        '''
        return 1

    def get_input_variable_coefficient(self, obj_variable, input_category):
        ''' Returns obj_variable, since in input-oriented model we multiply
            current input by efficiency spyDEA.core.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to input category of current DMU.
                input_category (str): input category for which current
                    constraint is being created.

            Returns:
                pulp.LpVariable: input variable coefficient.
        '''
        return obj_variable

    def update_output_category_coefficient(self, current_output, constraint,
                                           obj_var, output_category):
        ''' Updates coefficient of a given output category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): output category name.
        '''
        constraint.changeRHS(current_output)

    def update_input_category_coefficient(self, current_input, constraint,
                                          obj_var, input_category):
        ''' Updates coefficient of a given input category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): input category name.
        '''
        constraint[obj_var] = current_input


class EnvelopmentModelOutputOriented(OutputOrientedModel):

    ''' This class defines methods specific
        to output-oriented envelopment model.

        Attributes:
            lower_bound_generator (function): function that
                generates a lower bound on inverse of efficiency scores
                for envelopment
                model, see :mod:`refactored.bound_generators`

        Args:
            lower_bound_generator (function): function that
                generates a lower bound on inverse of efficiency scores for
                envelopment
                model, see :mod:`refactored.bound_generators`
    '''
    def __init__(self, lower_bound_generator):
        self.lower_bound_generator = lower_bound_generator

    def get_upper_bound_for_objective_variable(self):
        ''' Returns None, since variables of output-oriented envelopment
            model are not bounded.

            Returns:
                double: None.
        '''
        return None

    def get_lower_bound_for_objective_variable(self):
        ''' Returns a proper lower bound on the variables corresponding
            to output-oriented envelopment model.

            Returns:
                double: lower bound on variables.
        '''
        return self.lower_bound_generator()

    def get_objective_type(self):
        ''' Returns pulp.LpMinimize - we maximize objective function in case
            of output-oriented envelopment model.

            Returns:
                pulp.LpMaximize: objective function type.
        '''
        return pulp.LpMaximize

    def get_output_variable_coefficient(self, obj_variable, output_category):
        ''' Returns obj_variable, since in output-oriented model we multiply
            current output by inverse efficiency spyDEA.core.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to output category of current DMU.
                output_category (str): output category for which current
                    constraint is being created.

            Returns:
                pulp.LpVariable: output variable coefficient.
        '''
        return obj_variable

    def get_input_variable_coefficient(self, obj_variable, input_category):
        ''' Returns 1, since in output-oriented model we do not multiply
            current input by anything.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to input category of current DMU.
                input_category (str): input category for which current
                    constraint is being created.

            Returns:
                double: input variable coefficient.
        '''
        return 1

    def update_output_category_coefficient(self, current_output, constraint,
                                           obj_var, output_category):
        ''' Updates coefficient of a given output category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): output category name.
        '''
        constraint[obj_var] = -current_output

    def update_input_category_coefficient(self, current_input, constraint,
                                          obj_var, input_category):
        ''' Updates coefficient of a given input category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): input category name.
        '''
        constraint.changeRHS(-current_input)


class EnvelopmentModelInputOrientedWithNonDiscVars(
        EnvelopmentModelInputOriented):
    ''' This class redefines some methods of EnvelopmentModelInputOriented
        in order to take into account non-discretionary variables.

        Note:
            This class does not have a reference
            to InputData object. Hence, it cannot check if supplied
            non-discretionary categories are valid input categories.

        Attributes:
            non_disc_inputs (list of str): list of non-discretionary input
                categories.

        Args:
            non_disc_inputs (list of str): list of non-discretionary input
                categories.
            upper_bound_generator (function): function that
                generates an upper bound on efficiency scores for envelopment
                model, see :mod:`refactored.bound_generators`
    '''
    def __init__(self, non_disc_inputs, upper_bound_generator):
        super(EnvelopmentModelInputOrientedWithNonDiscVars, self).__init__(
            upper_bound_generator)
        assert(non_disc_inputs)
        self.non_disc_inputs = non_disc_inputs

    def get_input_variable_coefficient(self, obj_variable, input_category):
        ''' Returns proper coefficient depending on the fact if variable
            is discretionary or not.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to input category of current DMU.
                input_category (str): input category for which current
                    constraint is being created.

            Returns:
                double or pulp.LpVariable: input variable coefficient.

        '''
        if input_category in self.non_disc_inputs:
            return 1
        return obj_variable

    def update_input_category_coefficient(self, current_input, constraint,
                                          obj_var, input_category):
        ''' Updates coefficient of a given input category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): input category name.
        '''
        if input_category in self.non_disc_inputs:
            constraint.changeRHS(-current_input)
        else:
            constraint[obj_var] = current_input


class EnvelopmentModelOutputOrientedWithNonDiscVars(
        EnvelopmentModelOutputOriented):
    ''' This class redefines some methods of EnvelopmentModelOutputOriented
        in order to take into account non-discretionary variables.

        Note:
            This class does not have a reference
            to InputData object. Hence, it cannot check if supplied
            non-discretionary categories are valid output categories.

        Attributes:
            non_disc_outputs (list of str): list of non-discretionary output
                categories.

        Args:
            non_disc_outputs (list of str): list of non-discretionary output
                categories.
            lower_bound_generator (function): objects that
                generates a lower bound on inverse of efficiency scores for
                envelopment model, see :mod:`refactored.bound_generators`.
    '''
    def __init__(self, non_disc_outputs, lower_bound_generator):
        assert(non_disc_outputs)
        super(EnvelopmentModelOutputOrientedWithNonDiscVars, self).__init__(
            lower_bound_generator)
        self.non_disc_outputs = non_disc_outputs

    def get_output_variable_coefficient(self, obj_variable, output_category):
        ''' Returns a proper coefficient depending on the fact if the variable
            is discretionary or not.

            Args:
                obj_variable (pulp.LpVariable): pulp variable that corresponds
                    to output category of current DMU.
                input_category (str): output category for which current
                    constraint is being created.
            Returns:
                double or pulp.LpVariable: output variable coefficient.
        '''
        if output_category in self.non_disc_outputs:
            return 1
        return obj_variable

    def update_output_category_coefficient(self, current_output, constraint,
                                           obj_var, output_category):
        ''' Updates coefficient of a given output category with a new
            value.

            Args:
                current_output (double): new value for the coefficient.
                constraint (pulp.LpConstraint): constraint whose coefficient
                    should be updated.
                obj_var (pulp.LpVariable): variable of the envelopment
                    model that is optimised in the objective function.
                output_category (str): output category name.
        '''
        if output_category in self.non_disc_outputs:
            constraint.changeRHS(current_output)
        else:
            constraint[obj_var] = -current_output
