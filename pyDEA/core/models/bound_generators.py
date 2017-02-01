''' This module contains functions that produce proper upper bounds for
    efficiency scores for different envelopment models. Usually efficiency
    score must be within interval [0, 1]. But if a super efficiency model is
    used, then the efficiency score might be greater than 1.
'''


def generate_upper_bound_for_efficiency_score():
    ''' Returns upper bound for efficiency score for usual envelopment model.

        Note:
            This function only works with input-oriented envelopment models.

        Returns:
            double: 1, since efficiency score must be <= 1 for usual
                input-oriented envelopment model.
    '''
    return 1


def generate_supper_efficiency_upper_bound():
    ''' Returns upper bound for efficiency score for a super efficiency
        model.

        Note:
            This function only works with input-oriented envelopment models.

        Returns:
            None, since efficiency score might be greater than 1 for
            super efficiency input-oriented envelopment model.
    '''
    return None


def generate_lower_bound_for_efficiency_score():
    ''' Returns lower bound of the inverse of efficiency score for
        usual envelopment model.

        Note:
            This function only works with output-oriented envelopment models.

        Returns:
            double: 1, since inverse of efficiency score must be > 1 for
                usual output-oriented envelopment model.
    '''
    return 1


def generate_supper_efficiency_lower_bound():
    ''' Returns lower bound of the inverse of efficiency score for
        a super efficiency envelopment model.

        Note:
            This function only works with output-oriented envelopment models.

        Returns:
            double: 0, since efficiency score might be greater
                than 1 for super efficient output-oriented envelopment model.
    '''
    return 0
