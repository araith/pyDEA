''' This module contains peel the onion model.
'''

import copy
from pulp import LpStatusOptimal


def restore_base(model, first_solution, copy_of_dmu_codes, max_slack_solution):
    ''' Helper function used for restoring DMU codes and first solution.

        Args:
            model (ModelBase): model used in the peel the onion.
            first_solution (Solution): first solution of the peel the
                onion.
            copy_of_dmu_codes (list of str): list of original DMU codes.
            max_slack_solution (Solution): solution obtained by two phase
                model if any.
    '''
    model.input_data.DMU_codes = copy_of_dmu_codes
    if max_slack_solution:
        model.second_solution = max_slack_solution
    assert(first_solution)


def peel_the_onion_method(model):
    ''' Runs the peel the onion model and returns solution that corresponds to
        the first run and ranking of all DMUs.

        Args:
            model (ModelBase): DEA model that must be called in the peel
                the onion.

        Returns:
            tuple of Solution, dict of str to int, bool: tuple with the first
                solution of the problem, dictionary that maps DMU code to peel
                the onion rank, boolean value which is true if all peel the
                onion runs were successful, false otherwise.
    '''
    copy_of_dmu_codes = copy.deepcopy(model.input_data.DMU_codes)
    current_rank = 1
    ranks = dict()
    for dmu_code in model.input_data.DMU_codes:
        ranks[dmu_code] = 'Infeasible/unbounded'

    first_solution = None
    max_slack_solution = None
    while model.input_data.DMU_codes:
        solution = model.run()
        if current_rank == 1:
            first_solution = solution
            try:
                max_slack_solution = model.second_solution
            except AttributeError:
                pass
        dmus_to_remove = []
        not_efficient_dmus = []

        one_is_infeasible = False
        for dmu_code in model.input_data.DMU_codes:
            if solution.lp_status[dmu_code] != LpStatusOptimal:
                one_is_infeasible = True
            elif solution.is_efficient(dmu_code):
                ranks[dmu_code] = current_rank
                dmus_to_remove.append(dmu_code)
            else:
                not_efficient_dmus.append(dmu_code)

        if one_is_infeasible:
            restore_base(model, first_solution, copy_of_dmu_codes,
                         max_slack_solution)
            return first_solution, ranks, False
        for dmu_code in dmus_to_remove:
            model.input_data.DMU_codes.remove(dmu_code)
        if len(dmus_to_remove) == 0 and len(not_efficient_dmus) > 0:
            for dmu in not_efficient_dmus:
                ranks[dmu] = current_rank
            break
        current_rank += 1

    restore_base(model, first_solution, copy_of_dmu_codes, max_slack_solution)
    return first_solution, ranks, True
