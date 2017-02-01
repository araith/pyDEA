''' This module contains an abstract base class for all
    models.
'''

from pyDEA.core.data_processing.solution import Solution
from pyDEA.core.utils.dea_utils import check_input_and_output_categories


def do_nothing():
    ''' Helper function. Does nothing.
    '''
    pass


class ModelBase(object):
    ''' Abstract base class for some of the DEA models.

        Attributes:
            input_data (InputData): object that stores all input data.
            update_dmu_str_var (func): function that updates
                solution progress.
            lp_model (pulp.LpProblem): pulp LP.

        Args:
            input_data (InputData): object that stores all input data.
            update_str (func, optional): function that updates
                solution progress. Defaults to a function that does nothing.
    '''
    def __init__(self, input_data, update_str=do_nothing):
        self.input_data = input_data
        self.update_dmu_str_var = update_str
        self.lp_model = None

    def run(self):
        ''' Solves a given problem.
        '''
        check_input_and_output_categories(self.input_data)
        model_solution = self._create_solution()
        self._create_lp()
        for count, dmu_code in enumerate(self.input_data.DMU_codes):
            self.run_for_one_DMU(dmu_code, model_solution)
            # self.lp_model.writeLP("dmu_{0}.txt".format(dmu_code))
            self.update_dmu_str_var()
        return model_solution

    def _create_solution(self):
        ''' Allocates solution object.

            Returns:
                (Solution): created solution object.
        '''
        return Solution(self.input_data)

    def run_for_one_DMU(self, dmu_code, model_solution):
        ''' Solves LP for a given DMU and stores solution.

            Args:
                dmu_code (str): DMU code.
                model_solution (Solution): solution.
        '''
        self._update_lp(dmu_code)
        self.lp_model.solve()
        self._fill_solution(dmu_code, model_solution)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.
            Must be implemented in derived classes.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        raise NotImplementedError()

    def _create_lp(self):
        ''' Creates initial linear program. Must be implemented in derived
            classes.
        '''
        raise NotImplementedError()

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU. Must be implemented in derived classes.

            Args:
                dmu_code (str): DMU code.
        '''
        raise NotImplementedError()
