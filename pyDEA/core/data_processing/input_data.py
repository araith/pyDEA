''' This module contains a class for storing input data.
'''


class InputData:

    ''' This class stores input data and provides some useful methods to
        add input data and to access it.

        Attributes:
            DMU_codes (set of str): set of internal codes of DMUs.
                All codes are assigned automatically when DMUs are added.
            DMU_code_to_user_name (dict of str to str): dictionary that maps
                internal DMU codes to DMU names provided by the user.
            _DMU_user_name_to_code (dict of str to str): dictionary that
                maps DMU names to internal DMU codes. It is useful for
                adding new DMUs and for unit tests.
            DMU_codes_in_added_order (list of str): list of DMU codes
                in the order they were added.
            categories (set of str): set of all categories (input and
                output).
            coefficients (dict of tuple of str, str to double}): dictionary
                that maps internal DMU code and category to the
                corresponding coefficient, e.g. {(DMU, category) : value}.
            output_categories (set of str): set of output categories.
            input_categories (set of str): set of input categories.
            _count (int): internal variable used to generate DMU codes.
    '''
    def __init__(self):
        self.DMU_codes = set()
        self.DMU_code_to_user_name = dict()
        self._DMU_user_name_to_code = dict()  # intended to use
        # only in this class for adding new DMUs
        self.DMU_codes_in_added_order = []
        self.categories = set()  # all categories
        self.coefficients = dict()
        self.output_categories = set()
        self.input_categories = set()
        self._count = 0

    def add_coefficient(self, dmu_user_name, category_name, value):
        ''' Adds coefficient value corresponding to DMU and
            category to the internal data structure.
            Updates other containers that
            store DMUs and categories. If given pair of DMU and category already
            exist, KeyError is raised.

            Args:
                dmu_user_name (str): DMU name.
                category_name (str): category (input or output).
                value (double): coefficient value.

            Raises:
                KeyError: if a pair of dmu_user_name and category_name
                    has already been added before
        '''
        # if dmu_user_name is alread in the self._DMU_user_name_to_code
        # corresponding dmu_code is returned.
        # if dmu_user_name is not in self._DMU_user_name_to_code
        # new code will be generated and added to
        # self._DMU_user_name_to_code
        # self._generate_next_DMU_code() is executed every time,
        # so codes are not consecutive.
        dmu_code = self._DMU_user_name_to_code.setdefault(
            dmu_user_name, self._generate_next_DMU_code())

        key = (dmu_code, category_name)
        if key in self.coefficients:
            raise KeyError('Pair ({dmu}, {category}) is already recorded'.
                           format(dmu=dmu_code, category=category_name))

        self.coefficients[key] = value

        if dmu_code not in self.DMU_codes:
            self.DMU_codes_in_added_order.append(dmu_code)

        self.DMU_codes.add(dmu_code)
        self.DMU_code_to_user_name.setdefault(dmu_code, dmu_user_name)
        self.categories.add(category_name)

    def _generate_next_DMU_code(self):
        ''' Generates a code for new DMU in the following format: {dmu_number}.

            Returns:
                str: generated DMU code.
        '''
        self._count += 1
        return 'dmu_{index}'.format(index=self._count)

    def get_dmu_user_name(self, dmu_code):
        ''' Returns DMU user name given DMU code.

            Args:
                dmu_code (str): DMU code.

            Returns:
                str: DMU name.

            Raises:
                KeyError: if dmu_code does not exist.
        '''
        return self.DMU_code_to_user_name[dmu_code]

    def add_input_category(self, category_name):
        ''' Adds given category to the set of input categories.

            Args:
                category_name (str): name of the input category.

            Raises:
                KeyError: if category_name is not present among existing
                    categories.
        '''
        self._check_if_category_exists(category_name)
        if category_name in self.output_categories:
            raise ValueError('Category: {category} was previously added'
                             ' to output categories'.format(
                             category=category_name))
        self.input_categories.add(category_name)

    def add_output_category(self, category_name):
        ''' Adds given category to the set of output categories.

            Args:
                category_name (str): name of the output category.

            Raises:
                KeyError: if category_name is not present among existing
                    categories.
        '''
        self._check_if_category_exists(category_name)
        if category_name in self.input_categories:
            raise ValueError('Category: {category} was previously added'
                             ' to input categories'.format(
                             category=category_name))
        self.output_categories.add(category_name)

    def _check_if_category_exists(self, category_name):
        ''' Helper function that raises KeyError if a given category is not
            present in the list of categories.

            Args:
                category_name (str): category (input or output).

            Raises:
                KeyError: if category_name is not in the set of existing
                    categories.
        '''
        if category_name not in self.categories:
            raise KeyError('{category} is not present in categories list'.
                           format(category=category_name))

    def print_coefficients(self):
        ''' Prints all coefficients on the screen.
        '''
        for item in self.coefficients.items():
            print('DMU: {0}, category: {1}, value: {2}'.
                  format(item[0][0], item[0][1], item[1]))
        for dmu_code in self.DMU_codes:
            print('DMU code:{code}'.format(code=dmu_code))
        for item in self.DMU_code_to_user_name.items():
            print('DMU code: {code}, name: {name}'.
                  format(code=item[0], name=item[1]))
        for category in self.categories:
            print('category: {category}'.format(category=category))
