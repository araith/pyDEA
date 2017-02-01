import os
import shutil

from pyDEA.core.data_processing.solution_text_writer import TxtWriter, SolutionTextWriter
from pyDEA.core.utils.dea_utils import format_data


class SimpleWriter(object):

    def __init__(self):
        self.text = []

    def write(self, data):
        self.text.append(data)


def test_add_sheet():
    folder_name = os.path.join('tests', 'tmp_test_solution_writer')
    txt_writer = TxtWriter(folder_name)
    file_name = 'sheet1_test'
    txt_writer.add_sheet(file_name)
    assert len(txt_writer.tabs) == 1
    assert len(txt_writer.tab_writers) == 1
    assert os.path.exists(os.path.join(folder_name, 'sheet1_test.csv')) is True
    txt_writer.add_sheet('hahasecond')
    assert len(txt_writer.tabs) == 2
    assert len(txt_writer.tab_writers) == 2
    assert os.path.exists(os.path.join(folder_name, 'hahasecond.csv')) is True
    for file_ref in txt_writer.tabs:
        file_ref.close()
    shutil.rmtree(folder_name)


def test_save():
    folder_name = os.path.join('tests', 'tmp_test_solution_writer2')
    txt_writer = TxtWriter(folder_name)
    txt_writer.add_sheet('1')
    txt_writer.add_sheet('2')
    txt_writer.add_sheet('3')
    assert len(txt_writer.tab_writers) == 3
    names = []
    for i in range(3):
        name = 'name{0}'.format(i + 1)
        txt_writer.tab_writers[i][1].name = name
        names.append(name)
    # name does not matter, it is picked up from tab_writers
    txt_writer.save('haha')
    for name in names:
        assert os.path.exists(os.path.join(
            folder_name, '{0}.csv'.format(name))) is True
    shutil.rmtree(folder_name)


def test_existing_folder():
    folder_name = os.path.join('tests', 'tmp_test_solution_writer3')
    txt_writer = TxtWriter(folder_name)
    txt_writer = TxtWriter(folder_name)  # second call should not fail,
    # and should refer to the same folder
    assert os.path.exists(folder_name)
    shutil.rmtree(folder_name)


def test_write():
    saved_text = SimpleWriter()
    writer = SolutionTextWriter(';', saved_text.write)
    writer.write(0, 0, 'text')
    assert len(saved_text.text) == 2
    assert saved_text.text[0] == '\n'
    assert saved_text.text[1] == 'text'
    writer.write(0, 1, '1.5')
    assert len(saved_text.text) == 4
    assert saved_text.text[2] == ';'
    assert saved_text.text[3] == format_data('1.5')
    writer.write(1, 0, 10.5)
    assert len(saved_text.text) == 6
    assert saved_text.text[4] == '\n'
    assert saved_text.text[5] == format_data(10.5)
