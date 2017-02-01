from tkinter.ttk import Frame
from tkinter import Tk
import datetime
import os
import pytest

from pyDEA.core.gui_modules.solution_tab_frame_gui import SolutionTabFrame
from pyDEA.core.utils.dea_utils import TEXT_FOR_FILE_LBL
from pyDEA.core.data_processing.parameters import Parameters

from tests.test_CRS_env_input_oriented_model import data
from tests.test_CRS_env_input_oriented_model import model


class TabParentMock(Frame):

    def __init__(self, parent):
        super().__init__(parent)

    def change_solution_tab_name(self, new_tab_name):
        pass


class SolutionTabFrameMock(SolutionTabFrame):

    def ask_file_name_to_save(self):
        return "test_solution_output.xls"


@pytest.fixture
def solution_tab(request):
    main_parent = Tk()
    parent = TabParentMock(main_parent)
    solution_tab = SolutionTabFrameMock(parent)
    request.addfinalizer(main_parent.destroy)
    return solution_tab


def test_update_data_file_name(solution_tab):
    data_file_name = 'new name'
    solution_tab.update_data_file_name(data_file_name)
    assert (solution_tab.data_from_file_lbl.cget('text') ==
            TEXT_FOR_FILE_LBL + data_file_name)


def test_on_save_solution_no_solutions_exist(solution_tab):
    solution_tab.on_save_solution()
    assert solution_tab.model_solutions is None


def test_on_save_solution_ok(solution_tab, model):
    model_solution = model.run()
    solutions = [model_solution]
    params = Parameters()
    param_strs = ['param_strs']
    run_date = datetime.datetime.today()
    solution_tab.show_solution(solutions, params, param_strs, run_date, 5)
    assert solution_tab.model_solutions == solutions
    assert solution_tab.params == params
    assert solution_tab.param_strs == param_strs
    assert solution_tab.run_date == run_date
    assert solution_tab.total_seconds == 5

    solution_tab.on_save_solution()
    assert os.path.isfile(solution_tab.ask_file_name_to_save())
    os.remove(solution_tab.ask_file_name_to_save())
