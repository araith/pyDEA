''' This module contains ProgressBarDecorator class responsible
    for updating progress bar during solving a DEA model.
'''

from pyDEA.core.models.model_base import ModelBase


class ProgressBarDecorator(ModelBase):
    ''' This class is responsible to trigger update of the
        progress bar while a given DEA model is being solved.

        Attributes:
            model (ModelBase): given DEA model.
            update_dmu_str_var (func): function that triggers
                update of the progress bar.
            current_dmu (StringVar): StringVar object that triggers
                progress bar update.

        Args:
            model (ModelBase): given DEA model.
            current_dmu (StringVar): StringVar object that triggers
                progress bar update.
    '''
    def __init__(self, model, current_dmu):
        self.model = model
        model.update_dmu_str_var = self.update_dmu_str_var
        self.current_dmu = current_dmu

    def update_dmu_str_var(self):
        ''' Calls set method of StringVar object that triggers
            progress bar update.
        '''
        self.current_dmu.set('update')

    def __getattr__(self, name):
        return getattr(self.model, name)

    def run(self):
        ''' See base class.
        '''
        return self.model.run()

    def _create_solution(self):
        ''' See base class.
        '''
        return self.model._create_solution()

    def _create_lp(self):
        ''' See base class.
        '''
        self.model._create_lp()

    def _update_lp(self, dmu_code):
        ''' See base class.
        '''
        self.model._update_lp(dmu_code)

    def run_for_one_DMU(self, dmu_code, model_solution):
        ''' See base class.
        '''
        self.model.run_for_one_DMU(dmu_code, model_solution)

    def _fill_solution(self, dmu_code, lp_problem, model_solution):
        ''' See base class.
        '''
        self.model._fill_solution(dmu_code, lp_problem, model_solution)
