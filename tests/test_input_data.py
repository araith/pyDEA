import pytest

from pyDEA.core.data_processing.input_data import InputData


@pytest.fixture
def data(request):
    data = InputData()
    data.add_coefficient('dmu1', 'x1', 2.4)
    data.add_coefficient('dmu1', 'x2', 5)
    data.add_coefficient('dmu1', 'q', -12)
    data.add_coefficient('dmu2', 'x1', 3)
    return data


def test_input_data_add_valid_coefficient(data):
    assert len(data.DMU_codes) == 2
    assert len(data.categories) == 3
    assert len(data.input_categories) == 0
    assert len(data.output_categories) == 0
    assert len(data.coefficients) == 4
    assert len(data.DMU_code_to_user_name) == 2
    assert len(data._DMU_user_name_to_code) == 2
    assert 'x1' in data.categories
    assert 'x2' in data.categories
    assert 'q' in data.categories
    assert data.coefficients[data._DMU_user_name_to_code['dmu1'], 'x1'] == 2.4
    assert data.coefficients[data._DMU_user_name_to_code['dmu1'], 'x2'] == 5
    assert data.coefficients[data._DMU_user_name_to_code['dmu1'], 'q'] == -12
    assert data.coefficients[data._DMU_user_name_to_code['dmu2'], 'x1'] == 3
    assert data.DMU_codes_in_added_order == [
        data._DMU_user_name_to_code['dmu1'],
        data._DMU_user_name_to_code['dmu2']]


def test_input_data_add_the_same_coefficient():
    data = InputData()
    data.add_coefficient('dmu1', 'x1', 2.4)
    with pytest.raises(KeyError) as excinfo:
        data.add_coefficient('dmu1', 'x1', 5.4)
    assert str(excinfo.value) == ("'Pair ({dmu}, x1) is already recorded'".
                                  format(dmu=[x for x in data.DMU_codes][0]))


def test_input_data_get_dmu_user_name(data):
    assert data.get_dmu_user_name('dmu_1') == 'dmu1'
    assert data.get_dmu_user_name('dmu_4') == 'dmu2'


def test_input_data_add_input_category(data):
    data.add_input_category('x1')
    data.add_input_category('x2')
    assert len(data.input_categories) == 2
    assert 'x1' in data.input_categories
    assert 'x2' in data.input_categories


def test_input_data_add_existing_input_category(data):
    data.add_input_category('x1')
    data.add_input_category('x1')
    assert len(data.input_categories) == 1
    assert 'x1' in data.input_categories


def test_input_data_add_non_existing_category(data):
    with pytest.raises(KeyError) as excinfo:
        data.add_input_category('ha')
    assert str(excinfo.value) == "'ha is not present in categories list'"


def test_input_data_add_output_category_to_input(data):
    data.add_output_category('q')
    with pytest.raises(ValueError) as excinfo:
        data.add_input_category('q')
    assert str(excinfo.value) == ('Category: q was previously added'
                                  ' to output categories')


def test_input_data_add_output_category(data):
    data.add_output_category('x1')
    data.add_output_category('x2')
    assert len(data.output_categories) == 2
    assert 'x1' in data.output_categories
    assert 'x2' in data.output_categories


def test_input_data_add_existing_output_category(data):
    data.add_output_category('q')
    data.add_output_category('q')
    assert len(data.output_categories) == 1
    assert 'q' in data.output_categories


def test_input_data_add_non_existing_output_category(data):
    with pytest.raises(KeyError) as excinfo:
        data.add_output_category('aha')
    assert str(excinfo.value) == "'aha is not present in categories list'"


def test_input_data_add_input_category_to_output(data):
    data.add_input_category('x1')
    with pytest.raises(ValueError) as excinfo:
        data.add_output_category('x1')
    assert str(excinfo.value) == ('Category: x1 was previously added'
                                  ' to input categories')


def test_input_data_list_of_dmu_codes_order():
    data = InputData()
    data.add_coefficient('dmu1', 'x1', 2.4)
    data.add_coefficient('dmu1', 'x2', 5)
    data.add_coefficient('dmu2', 'x1', 3)
    data.add_coefficient('dmu2', 'x2', 3)
    data.add_coefficient('dmu3', 'x1', 2.4)
    data.add_coefficient('dmu3', 'x2', 5)
    data.add_coefficient('dmu4', 'x1', 3)
    data.add_coefficient('dmu4', 'x2', 3)
    assert data.DMU_codes_in_added_order == [data._DMU_user_name_to_code[
                                             'dmu1'],
                                             data._DMU_user_name_to_code[
                                                 'dmu2'],
                                             data._DMU_user_name_to_code[
                                                 'dmu3'],
                                             data._DMU_user_name_to_code[
                                             'dmu4']]
