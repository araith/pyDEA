from tkinter import Tk
from tkinter.ttk import Frame, Progressbar
import datetime
import pytest

from pyDEA.core.gui_modules.solution_frame_gui import SolutionFrameWithText
from pyDEA.core.data_processing.parameters import Parameters
from pyDEA.core.models.peel_the_onion import peel_the_onion_method

from tests.test_CRS_env_input_oriented_model import data, model


class MockForSolutionFrameParent(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.progress_bar = Progressbar(self, mode='determinate', maximum=100)


@pytest.fixture
def sol_frame(request):
    parent = Tk()
    sol_frame = SolutionFrameWithText(MockForSolutionFrameParent(parent))
    request.addfinalizer(parent.destroy)
    return sol_frame


def test_modify_tab_names(sol_frame):
    sol_frame.add_sheet('Test1')
    sol_frame.all_tabs[0].name = 'new name'
    sol_frame.add_sheet('Test2')
    sol_frame.all_tabs[1].name = 'test2 new name'
    sol_frame.modify_tab_names()
    assert sol_frame.tab(0, 'text') == 'new name'
    assert sol_frame.tab(1, 'text') == 'test2 new name'


def test_create_tab(sol_frame):
    sol_frame.create_tab('name1')
    assert len(sol_frame.all_tabs) == 1
    assert sol_frame.tab(0, 'text') == 'name1'
    sol_frame.create_tab('name2')
    assert len(sol_frame.all_tabs) == 2
    assert sol_frame.tab(1, 'text') == 'name2'


def test_add_sheet(sol_frame):
    sol_frame.add_sheet('sheet1')
    assert sol_frame.nb_tabs == 1
    assert sol_frame.nb_filled_tabs == 1
    assert len(sol_frame.all_tabs) == 1
    sol_frame.add_sheet('sheet2')
    assert sol_frame.nb_tabs == 2
    assert sol_frame.nb_filled_tabs == 2
    assert len(sol_frame.all_tabs) == 2


def test_show_solution(sol_frame, model):
    model_solution, ranks, state = peel_the_onion_method(model)
    sol_frame.show_solution([model_solution], Parameters(), ['params to print'],
                            datetime.datetime.today(), 5, ranks=[ranks])
    assert sol_frame.nb_tabs == 8
    assert len(sol_frame.all_tabs) == 8
    assert sol_frame.nb_filled_tabs == 8
    for count, tab in enumerate(sol_frame.all_tabs):
        assert sol_frame.tab(count, 'text') == tab.name

    model_solution = model.run()
    solutions = [model_solution]
    sol_frame.show_solution(solutions, Parameters(), [
                            'params to print'], datetime.datetime.today(), 5)
    assert sol_frame.nb_tabs == 7
    assert len(sol_frame.all_tabs) == 7
    assert sol_frame.nb_filled_tabs == 7
    for count, tab in enumerate(sol_frame.all_tabs):
        assert sol_frame.tab(count, 'text') == tab.name


def test_remove_unused_tabs(sol_frame):
    sol_frame.add_sheet('sheet1')
    sol_frame.add_sheet('sheet2')
    sol_frame.nb_filled_tabs -= 1
    sol_frame.remove_unused_tabs()
    assert sol_frame.nb_tabs == 1
    assert len(sol_frame.all_tabs) == 1
    assert sol_frame.tab(0, 'text') == 'sheet1'
