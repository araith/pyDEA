from tkinter import Tk
import pytest

from pyDEA.main_gui import MainFrame

import tests.utils_for_tests as utils_for_tests


@pytest.fixture
def main_frame(request):
    parent = Tk()
    main_frame = MainFrame(parent)
    request.addfinalizer(parent.destroy)
    return main_frame


def test_run_gui(main_frame):
    filename = 'tests/params_new_format.txt'

    def get_params():
        return filename
    main_frame.params_frame._get_filename_for_load = get_params

    def get_sheet_name(names):
        return 'Sheet1'
    main_frame.data_frame.data_tab.call_dialog = get_sheet_name
    main_frame.params_frame.load_file()
    main_frame.run()
    model_solutions = main_frame.data_frame.solution_tab.model_solutions
    assert len(model_solutions) == 1
    model_solution = model_solutions[0]
    model_input = model_solution._input_data
    utils_for_tests.check_optimal_solution_status_and_sizes(model_solution,
                                                            model_input)
    dmus = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    utils_for_tests.check_efficiency_scores(dmus, [1, 0.86998617, 1, 0.95561335,
                                                   0.85,
                                                   1, 1, 0.84507042, 1,
                                                   0.524, 0.89058524],
                                            model_solution, model_input)
