''' This module contains the class responsible for implementing a
    two-phase model.
'''
import pulp

from pyDEA.core.models.envelopment_model_base import EnvelopmentModelBase


class MaximizeSlacksModel(EnvelopmentModelBase):
    ''' Implements a two-phase model.

        Attributes:
            strongly_disposal_input_categories (set of str): set
                of strongly disposal input categories.
            strongly_disposal_output_categories (set of str): set
                of strongly disposal output categories.
            model (EnvelopmentModelBase): envelopment model used in
                two-phase model.
            second_solution (Solution): solution obtained after second
                phase.
            lp_model_max_slack (pulp.LpProblem): pulp LP.

        Args:
            model (EnvelopmentModelBase): envelopment model.
            weakly_disposable_categories (set of str, optional): set
                of weakly disposal categories. Defaults to None.
    '''
    def __init__(self, model, weakly_disposable_categories=None):
        if weakly_disposable_categories is None:
            weakly_disposable_categories = set()
        input_categories = model.input_data.input_categories
        self.strongly_disposal_input_categories = input_categories.difference(
            weakly_disposable_categories)
        output_categories = model.input_data.output_categories
        self.strongly_disposal_output_categories = output_categories.difference(
            weakly_disposable_categories)
        self.model = model
        self.second_solution = None
        self.lp_model_max_slack = None

    def __getattr__(self, name):
        return getattr(self.model, name)

    def run_for_one_DMU(self, dmu_code, model_solution):
        ''' See base class.
        '''
        self.model.run_for_one_DMU(dmu_code, model_solution)
        lp_model_copy = self.model.lp_model
        self.model.lp_model = self.lp_model_max_slack
        self.model._update_lp(dmu_code)
        self.model.lp_model = lp_model_copy
        self.lp_model_max_slack.solve()
        self.model._should_add_efficiency = False  # keep efficiency
         # calculated previously
        assert(self.second_solution is not None)
        lp_model_copy = self.model.lp_model
        self.model.lp_model = self.lp_model_max_slack
        self.model._fill_solution(dmu_code, self.second_solution)
        # sometimes
        # we can have optimal solution in second phase for a DMU
        # for which we had unbounded solution in the first phase
        self.second_solution.efficiency_scores[dmu_code] = float('inf')
        self.model._should_add_efficiency = True
        self.fill_efficiency(model_solution)
        self.model.lp_model = lp_model_copy

    # we need to explicitly redirect all calls to model since this class
    # inherits from EnvelopmentModelBase and all methods are defined there.
    # Some of them might be redefined by children classes. To ensure children
    # redefined methods are called, we have to explicitly redirect calls to
    # stored model.
    def _create_lp(self):
        ''' See base class.
        '''
        self.model._create_lp()
        self.lp_model_max_slack = self.model.lp_model.deepcopy()

        input_slack_vars = pulp.LpVariable.dicts(
            'input_slack', self.strongly_disposal_input_categories,
            0, None, pulp.LpContinuous)
        output_slack_vars = pulp.LpVariable.dicts(
            'output_slack', self.strongly_disposal_output_categories,
            0, None, pulp.LpContinuous)

        # change objective function
        self.lp_model_max_slack.sense = pulp.LpMaximize
        self.lp_model_max_slack.objective = (
            pulp.lpSum(list(input_slack_vars.values())) +
            pulp.lpSum(list(output_slack_vars.values())))

        # change constraints
        for input_category in self.strongly_disposal_input_categories:
            name = self.model._constraints[input_category]
            self.lp_model_max_slack.constraints[name].addterm(
                input_slack_vars[input_category], 1)
            self.lp_model_max_slack.constraints[name].sense = pulp.LpConstraintEQ

        for output_category in self.strongly_disposal_output_categories:
            name = self.model._constraints[output_category]
            self.lp_model_max_slack.constraints[name].addterm(
                output_slack_vars[output_category], -1)
            self.lp_model_max_slack.constraints[name].sense = pulp.LpConstraintEQ

    def _update_lp(self, dmu_code):
        ''' See base class.
        '''
        self.model._update_lp(dmu_code)

    def _add_constraints_for_outputs(self, variables, dmu_code,
                                     obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_outputs(variables, dmu_code,
                                                obj_variable)

    def _add_constraints_for_inputs(self, variables,
                                    dmu_code, obj_variable):
        ''' See base class.
        '''
        self.model._add_constraints_for_inputs(variables, dmu_code,
                                               obj_variable)

    def _process_duals(self, dmu_code, categories, func):
        ''' See base class.
        '''
        self.model._process_duals(dmu_code, categories, func)

    def _fill_solution(self, dmu_code, model_solution):
        ''' See base class.
        '''
        self.model._fill_solution(dmu_code, model_solution)

    def _create_solution(self):
        ''' See base class.
        '''
        self.second_solution = self.model._create_solution()
        return self.model._create_solution()

    def fill_efficiency(self, model_solution):
        ''' Copies efficiency scores from the solution obtained from
            the first phase to the solution of the second phase.

            Args:
                model_solution (Solution): solution obtained from the
                    first phase.
        '''
        for dmu_code, score in model_solution.efficiency_scores.items():
            self.second_solution.add_efficiency_score(dmu_code, score)
