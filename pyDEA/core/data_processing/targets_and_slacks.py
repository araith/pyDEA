''' This module contains functions responsible for
    calculating various targets for output.
'''


def calculate_target(category, lambda_vars, coefficients):
    ''' Returns a target value for a given category.

        Args:
            category (str): category name.
            lambda_vars (dict of str to double): dictionary
                    that maps DMU codes to the corresponding value
                    of lambda variables.
            coefficients (dict of tuple of str, str to double}): dictionary
                that maps internal DMU code and category to the
                corresponding coefficient, e.g. {(DMU, category) : value}.

        Returns:
            double: target value.
    '''
    target = 0
    for dmu, value in lambda_vars.items():
        target += value * coefficients[dmu, category]
    return target


def calculate_radial_reduction(dmu_code, category, data, efficiency_score,
                               orientation):
    ''' Calculates radial reduction for a given DMU and category.

        Args:
            dmu_code (str): DMU code.
            category (str): category name.
            data (InputData): object that stores input data.
            efficiency_score (double): efficiency spyDEA.core.
            orientation (str): problem orientation, can take values
                input or output.

        Returns:
            double: radial reduction value.
    '''
    # if input-oriented, then radial reduction is
    # zero for all outputs
    # if output-oriented, then radial reduction is
    # zero for all inputs
    if orientation == 'input':
        if category in data.output_categories:
            return 0
        objective_value = efficiency_score
    elif orientation == 'output':
        if category in data.input_categories:
            return 0
        objective_value = 1/efficiency_score

    return (objective_value - 1) * data.coefficients[dmu_code, category]


def calculate_non_radial_reduction(target, radial_reduction, original):
    ''' Calculates non-radial reduction value.

        Args:
            target (double): DMU target value.
            radial_reduction (double): radial reduction value.
            original (double): coefficient corresponding to DMU and category
                of interest.

        Returns:
            double: non-radial reduction value.
    '''
    return target - original - radial_reduction
