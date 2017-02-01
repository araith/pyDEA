''' This module contains class for performing DEA analysis with categorical DMUs
    and some helper functions.
'''
from pyDEA.core.models.model_base import ModelBase
from pyDEA.core.utils.dea_utils import check_input_and_output_categories


def get_dmus_with_fixed_hierarchical_category(coefficients,
                                              hierarchical_category,
                                              category_name,
                                              dmu_codes):
    ''' Constructs a set of DMU codes that have the value of hierarchical
        category equal to the specified category value.

        Args:
            coefficients (dict of tuple of str, str to double): dictionary
                that maps DMU codes and categories to values.
            hierarchical_category (int): specified value of hierarchical
                category.
            category_name (str): name of the category with hierarchical
                order of DMUs.
            dmu_codes (set of str): set of DMU codes.

        Returns:
            set of str: a set of DMU codes that have the value of hierarchical
                category equal to given input parameter hierarchical_category.
    '''
    return set(dmu for (dmu, category), coeff in coefficients.items()
               if int(coeff) == hierarchical_category and
               category == category_name and dmu in dmu_codes)


class ModelWithCategoricalDMUs(ModelBase):

    ''' This class implements DEA categorical analysis.

        Attributes:
            model (ModelBase): a concrete model that is used for categorical
                analysis.
            category_name (str): name of the category with hierarchical
                order of DMUs.

        Args:
            model (ModelBase): model that should be used for every
                hierarchical category.
            category_name (str): name of the category with hierarchical
                order of DMUs.
    '''
    def __init__(self, model, category_name):
        if category_name not in model.input_data.categories:
            raise ValueError('Category <{category}> does not exist'.
                             format(category=category_name))
        self.model = model
        self.category_name = category_name

    def __getattr__(self, name):
        ''' Redirects calls to all undefined methods or attributes
            to self.model.

            Attributes:
                name (str): attribute name.
        '''
        return getattr(self.model, name)

    def run(self):
        ''' Performs categorical analysis.

            Warning:
                All categorical values must be integers.

            DMUs with category 1 are considered first and compared
            only to each other. Then DMUs with category 1 and 2 are considered,
            and so on. Hence, category 1 is least favourable, category 2 is more
            favourable and so on.

            Returns:
                Solution: solution of the problem.

            Warning:
                All floating point values of categorical category will be
                truncated to integer values.
        '''
        check_input_and_output_categories(self.input_data)
        copy_of_dmu_codes = set([dmu for dmu in self.input_data.DMU_codes])
        model_solution = self._create_solution()

        tmp_set = set(int(coeff) for (dmu, category), coeff in
                      self.input_data.coefficients.items()
                      if category == self.category_name)
        sorted_hierarchical_categories = sorted(tmp_set)

        self.input_data.DMU_codes = set()
        for hierarchical_category in sorted_hierarchical_categories:
            dmu_fixed_category = get_dmus_with_fixed_hierarchical_category(
                self.input_data.coefficients,
                hierarchical_category, self.category_name,
                copy_of_dmu_codes)

            self.input_data.DMU_codes = dmu_fixed_category.union(
                self.input_data.DMU_codes)
            if len(self.input_data.DMU_codes) > 0:
                self._create_lp()
                for dmu_code in dmu_fixed_category:
                    self.run_for_one_DMU(dmu_code, model_solution)
                    self.update_dmu_str_var()

        self.input_data.DMU_codes = copy_of_dmu_codes
        return model_solution

    def run_for_one_DMU(self, dmu_code, model_solution):
        ''' Solves LP for a given DMU.

            Args:
                dmu_code (str): DMU code.
                model_solution (Solution): model solution, it will be
                    filled by this method.
        '''
        self.model.run_for_one_DMU(dmu_code, model_solution)

    def _fill_solution(self, dmu_code, model_solution):
        ''' Fills given solution for a given DMU.

            Args:
                dmu_code (str): DMU code.
                model_solution (Solution): model solution that will be
                    filled.
        '''
        self.model._fill_solution(dmu_code, model_solution)

    def _create_solution(self):
        ''' Allocates a proper solution object.

            Returns:
                Solution: allocated solution object.
        '''
        return self.model._create_solution()

    def _create_lp(self):
        ''' Creates a proper linear program.
        '''
        self.model._create_lp()

    def _update_lp(self, dmu_code):
        ''' Updates created linear program with parameters of the given
            DMU.

            Args:
                dmu_code (str): DMU code.
        '''
        self.model._update_lp(dmu_code)
