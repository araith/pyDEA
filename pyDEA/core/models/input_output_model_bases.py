''' This module contains classes that implement methods common for input- and
    output-oriented models.
'''

from pyDEA.core.utils.dea_utils import ZERO_TOLERANCE


class InputOrientedModel(object):

    ''' This class implements methods that are the same for all input-oriented
        models.
    '''
    def get_orientation(self):
        ''' Returns orientation of the model as a string.

            Returns:
                str: a string 'input'.
        '''
        return 'input'

    def process_obj_var(self, obj_value):
        ''' Post-process objective function value if necessary.

            Args:
                obj_value (double): value of the objective function.

            Returns:
                double: value of obj_variable, since efficiency score is in
                    the interval [0, 1] for input-oriented model.
        '''
        if obj_value > 1 and obj_value <= 1 + ZERO_TOLERANCE:
            return 1.0
        return obj_value

    def process_dual_value(self, dual_value):
        ''' Post-process given value of a dual variable if necessary.

            Args:
                dual_value (double): value of the dual variable.

            Returns:
                double: dual_value since in input-oriented model we do nothing
                    with duals.
        '''
        return dual_value


class OutputOrientedModel(object):
    ''' This class implements methods that are the same for all output-oriented
        models.
    '''
    def get_orientation(self):
        ''' Returns orientation of the model as a string.

            Returns:
                str: a string 'output'.
        '''
        return 'output'

    def process_obj_var(self, obj_value):
        ''' Post-process objective function value if necessary.

            Args:
                obj_value (double): value of the objective function.

            Returns:
                double: 1/obj_variable, since in the case of output-oriented
                    models the value of objective function corresponds to
                    inverse of efficiency spyDEA.core.
        '''
        if obj_value == 0:
            return float('inf')
        return 1.0/obj_value

    def process_dual_value(self, dual_value):
        ''' Post-process given value of a dual variable if necessary.

            Args:
                dual_value (double): value of the dual variable.

            Returns:
                double: -dual_value if it is non-zero since in output-oriented
                    models.
        '''
        if dual_value:
            return -dual_value
        return dual_value
