''' This module contains classes that implement VRS multiplier model,
    multiplier model with disposable variables and with various
    kind of weight restrictions.
'''
import pulp

from pyDEA.core.models.multiplier_model_base import MultiplierModelBase
from pyDEA.core.data_processing.solution import SolutionWithVRS


class MultiplierModelVRSDecorator(MultiplierModelBase):
    ''' This class is a concrete implementation of VRS multiplier model.

        Attributes:
            _model_to_decorate (MultiplierModelBase): multiplier model.
            _vrs_variable (pulp.LpVariable): VRS variable.
            multiplier (int): 1 for input-oriented model, -1 for output-
                oriented model.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model
                that needs to be decorated with VRS constraint.
    '''
    def __init__(self, model_to_decorate):
        self._model_to_decorate = model_to_decorate
        self._vrs_variable = None
        self.multiplier = 1
        if (self._model_to_decorate._concrete_model.get_orientation() ==
                'output'):
            self.multiplier = -1

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model

        self._vrs_variable = pulp.LpVariable('VRS_variable', None, None,
                                             pulp.LpContinuous)
        self._model_to_decorate.lp_model.objective += self._vrs_variable

        for dmu_constraint in self._model_to_decorate._dmu_constraint_names.keys():
            self._model_to_decorate.lp_model.constraints[dmu_constraint] += (
                self.multiplier * self._vrs_variable)

    def _update_lp(self, dmu_code):
        ''' Updates LP with coefficients corresponding to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._update_lp(dmu_code)

    def _create_solution(self):
        ''' Creates SolutionWithVRS instead of usual Solution in order to
            add extra information about VRS dual variable.

            Returns:
                SolutionWithVRS: solution that is able to store extra
                    information about VRS dual variable.
        '''
        basic_solution = super()._create_solution()
        return SolutionWithVRS(basic_solution)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Adds value of dual variable corresponding to VRS constraint to
            model_solution.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)
        model_solution.add_VRS_dual(dmu_code, self._vrs_variable.varValue)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self._model_to_decorate._get_efficiency_score(lambda_variable)


class MultiplierModelWithDisposableCategories(MultiplierModelBase):
    ''' Implements multiplier model with disposable categories.

        Attributes:
            _model_to_decorate (MultiplierModelBase): multiplier model.
            weakly_disposable_categories (set of str): set of weakly
                disposable categories.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            weakly_disposable_categories (set of str): set of weakly
                disposable categories.
    '''
    def __init__(self, model_to_decorate, weakly_disposable_categories):
        self._model_to_decorate = model_to_decorate
        assert(weakly_disposable_categories)
        self.weakly_disposable_categories = weakly_disposable_categories

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model
        self._change_lower_bound(self._model_to_decorate._input_variables)
        self._change_lower_bound(self._model_to_decorate._output_variables)

    def _update_lp(self, dmu_code):
        ''' Updates LP with coefficients corresponding to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._update_lp(dmu_code)

    def _change_lower_bound(self, variables):
        ''' Changes lower bound for variables corresponding to weakly
            disposable categories.

            Args:
                variables (dict of str to pulp.LpVariable): dictionary of
                    pulp variables than maps variable names to pulp variables.
        '''
        for category, var in variables.items():
            if category in self.weakly_disposable_categories:
                var.lowBound = None

    def _create_solution(self):
        ''' Creates solution object.

            Returns:
                Solution: allocated solution.
        '''
        return self._model_to_decorate._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self._model_to_decorate._get_efficiency_score(lambda_variable)


class MultiplierModelWithNonDiscVarsForDecoration(MultiplierModelBase):
    ''' Abstract base class that implements multiplier model with
        non-discretionary variables.

        Attributes:
            _model_to_decorate (MultiplierModelBase): multiplier model.
            categories (set of str): set of non-discretionary categories.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            categories (set of str): set of non-discretionary categories.
    '''
    def __init__(self, model_to_decorate, categories):
        assert(categories)
        self._model_to_decorate = model_to_decorate
        self.categories = categories

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model
        for elem in self.input_data.DMU_codes:
            dmu_code = elem
            break
        variables = self._get_variables()
        sum_vars = pulp.lpSum(
            [var * self._model_to_decorate.input_data.coefficients[
                dmu_code, category]
                for category, var in variables.items()
                if category in self.categories])
        self.lp_model.objective += -sum_vars
        for category, var in variables.items():
            if category in self.categories:
                var.lowBound = 0
        self.lp_model.constraints['equality_constraint'] = self._get_equality_constraint(
            dmu_code)

    def _update_lp(self, dmu_code):
        ''' Updates LP with coefficients corresponding to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._concrete_model.update_objective(
            self.input_data, dmu_code, self._input_variables,
            self._output_variables, self.lp_model)
        in_vars = self._get_input_variables()
        out_vars = self._get_output_variables()
        self._model_to_decorate._concrete_model.update_equality_constraint(
            self.input_data, dmu_code, in_vars, out_vars, self.lp_model)
        variables = self._get_variables()
        for category, var in variables.items():
            if category in self.categories:
                self.lp_model.objective[var] = (
                    -self._model_to_decorate.input_data.coefficients[
                        dmu_code, category])

    def _get_variables(self):
        ''' Returns proper variables.

            Returns:
                dict of str to pulp.LpVariable: dictionary of
                    pulp variables than maps variable names to pulp variables.

        '''
        raise NotImplementedError()

    def _get_input_variables(self):
        ''' Returns pulp variables that correspond to input categories.

            Returns:
                dict of str to pulp.LpVariable: dictionary of
                    pulp variables than maps variable names to pulp variables.
        '''
        return self._model_to_decorate._input_variables

    def _get_output_variables(self):
        ''' Returns pulp variables that correspond to output categories.

            Returns:
                dict of str to pulp.LpVariable: dictionary of
                    pulp variables than maps variable names to pulp variables.
        '''
        return self._model_to_decorate._output_variables

    def _get_equality_constraint(self, dmu_code):
        ''' Returns equality constraint.

            Args:
                dmu_code (str): DMU code.

            Returns:
                pulp.LpConstraint: equality constraint.
        '''
        coeffs = self._model_to_decorate.input_data.coefficients
        variables = self._get_variables()
        sum_vars = pulp.lpSum([coeffs[dmu_code, category] * value
                              for category, value in variables.items()
                              if category not in self.categories])
        assert(sum_vars)
        return sum_vars == 1

    def _create_solution(self):
        ''' Creates solution object.

            Returns:
                Solution: allocated solution.
        '''
        return self._model_to_decorate._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self._model_to_decorate._get_efficiency_score(lambda_variable)


class MultiplierModelInputOrientedWithNonDiscVars(
        MultiplierModelWithNonDiscVarsForDecoration):
    ''' Implements input-oriented multiplier model with non-discretionary
        variables.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            categories (set of str): set of non-discretionary categories.

        Raises:
            ValueError: if categories contain more values that total
                number of input categories.
    '''
    def __init__(self, model_to_decorate, categories):
        super(MultiplierModelInputOrientedWithNonDiscVars, self).__init__(
            model_to_decorate, categories)
        if (len(categories) >=
                len(self._model_to_decorate.input_data.input_categories)):
            raise ValueError('Too many non-discretionary categories')

    def _get_variables(self):
        ''' See base class.
        '''
        return self._model_to_decorate._input_variables

    def _get_input_variables(self):
        ''' See base class.
        '''
        out_dict = {key: var for key, var in
                    self._model_to_decorate._input_variables.items()
                    if key not in self.categories}
        return out_dict


class MultiplierModelOutputOrientedWithNonDiscVars(
        MultiplierModelWithNonDiscVarsForDecoration):
    ''' Implements output-oriented multiplier model with non-discretionary
        variables.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            categories (set of str): set of non-discretionary categories.

        Raises:
            ValueError: if categories contain more values that total
                number of output categories.
    '''
    def __init__(self, model_to_decorate, categories):
        super(MultiplierModelOutputOrientedWithNonDiscVars, self).__init__(
            model_to_decorate, categories)
        if (len(categories) >=
                len(self._model_to_decorate.input_data.output_categories)):
            raise ValueError('Too many non-discretionary categories.'
                             ' At least one output must be discretionary')

    def _get_variables(self):
        ''' See base class.
        '''
        return self._model_to_decorate._output_variables

    def _get_output_variables(self):
        ''' See base class.
        '''
        return {key: var for key, var in
                self._model_to_decorate._output_variables.items()
                if key not in self.categories}


class MultiplierModelWithWeigthRestrictionsBase(MultiplierModelBase):
    ''' Abstract base class that implements basic operations
        of multiplier model with weight restrictions.

        Attributes:
            _model_to_decorate (MultiplierModelBase): multiplier model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
    '''
    def __init__(self, model_to_decorate, bounds):
        self._model_to_decorate = model_to_decorate
        self.bounds = bounds

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model
        for elem in self.input_data.DMU_codes:
            dmu_code = elem
            break

        for category, (lower_bound, upper_bound) in self.bounds.items():

            multiplier = self._get_multiplier(dmu_code, category)
            variable = self._model_to_decorate._input_variables.get(category,
                                                                    None)
            if variable is None:
                variable = self._model_to_decorate._output_variables[category]

            if lower_bound:
                constraint_name = ('{0}_lower_bound_constraint_on_'
                                   'category_{1}'.format(
                                   self._get_constraint_prefix_name(),
                                   category))
                self.lp_model += (multiplier * variable >= lower_bound,
                                  constraint_name)
                self._store_vars_lb(category, constraint_name, variable)

            if upper_bound:
                constraint_name = ('{0}_upper_bound_constraint_on_'
                                   'category_{1}'.format(
                                   self._get_constraint_prefix_name(),
                                   category))
                self.lp_model += (multiplier * variable <= upper_bound,
                                  constraint_name)
                self._store_vars_ub(category, constraint_name, variable)

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._update_lp(dmu_code)

    def _store_vars_lb(self, category, constraint_name, variable):
        ''' Stores a given variable in an internal data structure if needed.

            Args:
                category (str): category name.
                constraint_name (str): constraint name.
                variable (pulp.LpVariable): variable.
        '''
        pass

    def _store_vars_ub(self, category, constraint_name, variable):
        ''' Stores a given variable in an internal data structure if needed.

            Args:
                category (str): category name.
                constraint_name (str): constraint name.
                variable (pulp.LpVariable): variable.
        '''
        pass

    def _create_solution(self):
        ''' Creates solution object.

            Returns:
                Solution: allocated solution.
        '''
        return self._model_to_decorate._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self._model_to_decorate._get_efficiency_score(lambda_variable)

    def _get_multiplier(self, input_category):
        ''' Returns a proper multiplier given input category.

            Args:
                input_category (str): input category.

            Returns:
                double: multiplier.
        '''
        raise NotImplementedError()

    def _get_constraint_prefix_name(self):
        ''' Returns prefix of a constraint name.

            Returns:
                str: prefix of a constraint name.
        '''
        raise NotImplementedError()


class MultiplierModelWithAbsoluteWeightRestrictions(
        MultiplierModelWithWeigthRestrictionsBase):
    ''' Implements multiplier model with absolute weight restrictions.
    '''
    def _get_multiplier(self, dmu_code, category):
        ''' See base class.
        '''
        return 1

    def _get_constraint_prefix_name(self):
        ''' See base class.
        '''
        return 'Absolute'


class MultiplierModelWithVirtualWeightRestrictions(
        MultiplierModelWithWeigthRestrictionsBase):
    ''' Implements multiplier model with virtual weight restrictions.

        Attributes:
            lb_weight_rest_variables (dict of str to tuple of pulp.LpVariable,
                str): dictionary that maps category name to a tuple of pulp
                variable and constraint name.
            ub_weight_rest_variables (dict of str to tuple of pulp.LpVariable,
                str): dictionary that maps category name to a tuple of pulp
                variable and constraint name.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
    '''
    def __init__(self, model_to_decorate, bounds):
        super().__init__(model_to_decorate, bounds)
        self.lb_weight_rest_variables = dict()
        self.ub_weight_rest_variables = dict()

    def _create_lp(self):
        ''' See base class.
        '''
        self.lb_weight_rest_variables.clear()
        self.ub_weight_rest_variables.clear()
        super()._create_lp()

    def _get_multiplier(self, dmu_code, category):
        ''' See base class.
        '''
        return self._model_to_decorate.input_data.coefficients[
            dmu_code, category]

    def _get_constraint_prefix_name(self):
        ''' See base class.
        '''
        return 'Virtual'

    def _update_lp(self, dmu_code):
        ''' See base class.
        '''
        self._model_to_decorate._update_lp(dmu_code)
        for category, (lower_bound, upper_bound) in self.bounds.items():

            multiplier = self._get_multiplier(dmu_code, category)

            if lower_bound:
                variable, constraint_name = self.lb_weight_rest_variables[
                    category]
                self.lp_model.constraints[constraint_name][variable] = multiplier

            if upper_bound:
                variable, constraint_name = self.ub_weight_rest_variables[
                    category]
                self.lp_model.constraints[constraint_name][variable] = multiplier

    def _store_vars_lb(self, category, constraint_name, variable):
        ''' See base class.
        '''
        self.lb_weight_rest_variables[category] = (variable, constraint_name)

    def _store_vars_ub(self, category, constraint_name, variable):
        ''' See base class.
        '''
        self.ub_weight_rest_variables[category] = (variable, constraint_name)


class MultiplierModelWithPriceRatioConstraints(MultiplierModelBase):
    ''' Implements multiplier model with price ratio restrictions.

        Attributes:
            _model_to_decorate (MultiplierModelBase): multiplier model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.

        Args:
            model_to_decorate (MultiplierModelBase): multiplier model.
            bounds (dict of str to tuple of double,
                double or dict of tuple of str, str to tuple of double, double:
                dictionary with parsed values of constraints):
                dictionary with parsed values of constraints.
    '''
    def __init__(self, model_to_decorate, bounds):
        self._model_to_decorate = model_to_decorate
        self.bounds = bounds

    def __getattr__(self, name):
        return getattr(self._model_to_decorate, name)

    def _create_lp(self):
        ''' Creates initial LP.
        '''
        self._model_to_decorate._create_lp()
        self.lp_model = self._model_to_decorate.lp_model
        for (category_in_nom, category_in_denom), (lower_bound, upper_bound) in self.bounds.items():

            variable_in_nom = self._model_to_decorate._input_variables.get(
                category_in_nom, None)
            if variable_in_nom is None:
                variable_in_nom = self._model_to_decorate._output_variables[
                    category_in_nom]

            variable_in_denom = self._model_to_decorate._input_variables.get(
                category_in_denom, None)
            if variable_in_denom is None:
                variable_in_denom = self._model_to_decorate._output_variables[
                    category_in_denom]

            if lower_bound:
                self.lp_model += (variable_in_nom >= variable_in_denom *
                                  lower_bound,
                                  'Price ratio lower bound constraint'
                                  ' on categories {0} and {1}'.format(
                                  category_in_nom,
                                  category_in_denom))
            if upper_bound:
                self.lp_model += (variable_in_nom <= variable_in_denom *
                                  upper_bound,
                                  'Price ratio upper bound constraint on'
                                  ' category {0} and {1}'.format(
                                  category_in_nom,
                                  category_in_denom))

    def _update_lp(self, dmu_code):
        ''' Updates existing linear program with coefficients corresponding
            to a given DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self._model_to_decorate._update_lp(dmu_code)

    def _create_solution(self):
        ''' Creates solution object.

            Returns:
                Solution: allocated solution.
        '''
        return self._model_to_decorate._create_solution()

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution with data calculated for one DMU.

            Args:
                dmu_code (str): DMU code for which the LP was solved.
                model_solution (Solution): object where solution for one DMU
                    will be written.
        '''
        self._model_to_decorate._fill_solution(dmu_code, model_solution)

    def _get_efficiency_score(self, lambda_variable):
        ''' Returns efficiency score based on a given lambda variable.

            Args:
                lambda_variable (double): value of the lambda variable.

            Returns:
                double: efficiency spyDEA.core.
        '''
        return self._model_to_decorate._get_efficiency_score(lambda_variable)
