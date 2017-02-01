''' This module contains SupperEfficiencyModel class that
    implements super efficiency model.
'''
from pulp import LpStatusOptimal

from pyDEA.core.models.model_base import ModelBase
from pyDEA.core.data_processing.solution import SolutionWithSuperEfficiency
from pyDEA.core.data_processing.solution import SolutionWithVRS


class SupperEfficiencyModel(ModelBase):
    ''' This class implements super efficiency model.

        Attributes:
            model (ModelBase): model that should be decorated
                with super efficiency model.

        Args:
            model (ModelBase): model that should be decorated
                with super efficiency model.
    '''
    def __init__(self, model):
        self.model = model

    def __getattr__(self, name):
        return getattr(self.model, name)

    def _create_solution(self):
        ''' Allocates solution object.

            Returns:
                (SolutionWithSuperEfficiency): created solution object.
        '''
        basic_solution = self.model._create_solution()
        if type(basic_solution) == SolutionWithVRS:
            basic_solution._model_solution = \
                SolutionWithSuperEfficiency(self.model.input_data)
            return basic_solution
        return SolutionWithSuperEfficiency(self.model.input_data)

    def run_for_one_DMU(self, dmu_code, model_solution):
        ''' Solves LP for a given DMU and stores solution.

            Args:
                dmu_code (str): DMU code.
                model_solution (Solution): solution.
        '''
        if len(self.model.input_data.DMU_codes) == 1:  # special case
            self._fill_solution_one_dmu(dmu_code, model_solution)
            return
        self.model.input_data.DMU_codes.remove(dmu_code)
        self.model._create_lp()
        self.model.run_for_one_DMU(dmu_code, model_solution)
        self.model.input_data.DMU_codes.add(dmu_code)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.
            Must be implemented in derived classes.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self.model._fill_solution(dmu_code, model_solution)

    def _create_lp(self):
        ''' Creates initial linear program. Must be implemented in derived
            classes.
        '''
        self.model._create_lp()

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU. Must be implemented in derived classes.

            Args:
                dmu_code (str): DMU code.
        '''
        self.model._update_lp(dmu_code)

    def _fill_solution_one_dmu(self, dmu_code, model_solution):
        ''' Treats a special case when we want to solve a super efficiency
            model but have only one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        model_solution.orientation = self._concrete_model.get_orientation()
        model_solution.add_lp_status(dmu_code, LpStatusOptimal)

        model_solution.add_efficiency_score(dmu_code, 1)
        model_solution.add_lambda_variables(dmu_code, dict())
        for category in self.input_data.input_categories:
            model_solution.add_input_dual(dmu_code, category, 0)
        for category in self.input_data.output_categories:
            model_solution.add_output_dual(dmu_code, category, 0)

        try:
            model_solution.add_VRS_dual(dmu_code, 0)
        except AttributeError:
            pass
