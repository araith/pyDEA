''' This module contains function responsible for creating several models and
    parameters in the case when RETURN_TO_SCALE or ORIENTATION is set to both.
'''

import pyDEA.core.utils.model_factory as model_factory
from pyDEA.core.data_processing.parameters import Parameters


def build_models(params, model_input):
    ''' Creates several models and parameters in the case when
        RETURN_TO_SCALE or ORIENTATION is set to both. If neither
        RETURN_TO_SCALE
        nor ORIENTATION is set to both, then no new models will be created,
        a copy of the given model and parameters will be returned.

        Args:
            params (Parameters): parameters.
            model_input (InputData): data instance.

        Returns:
            tuple of list of ModelBase, list of Parameters: tuple with two
                lists. The first list contains all created models, the
                second list contains corresponding parameters.
    '''
    model_factory.add_input_and_output_categories(params, model_input)
    rts_type = params.get_parameter_value('RETURN_TO_SCALE')
    list_of_param_objects = []
    original_params = Parameters()
    original_params.copy_all_params(params)
    list_of_param_objects.append(original_params)
    if rts_type == 'both':
        original_params.update_parameter('RETURN_TO_SCALE', 'VRS')
        params_with_crs = Parameters()
        params_with_crs.copy_all_params(original_params)
        params_with_crs.update_parameter('RETURN_TO_SCALE', 'CRS')
        list_of_param_objects.append(params_with_crs)
    orientation_type = original_params.get_parameter_value('ORIENTATION')
    nb_param_objs = len(list_of_param_objects)
    if orientation_type == 'both':
        possible_orientation = ['input', 'output']
        for count in range(nb_param_objs):
            assert(count < 2)
            param_obj = list_of_param_objects[count]
            param_obj.update_parameter('ORIENTATION',
                                       possible_orientation[count])
            new_param_obj = Parameters()
            new_param_obj.copy_all_params(param_obj)
            new_param_obj.update_parameter('ORIENTATION',
                                           possible_orientation[1 - count])
            list_of_param_objects.append(new_param_obj)

    models = []
    for param_object in list_of_param_objects:
        models.append(model_factory.create_model(param_object, model_input))
    return models, list_of_param_objects
