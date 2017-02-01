from tkinter import StringVar, Tk
import pytest

from pyDEA.core.gui_modules.table_gui import CheckbuttonWithVar
from pyDEA.core.gui_modules.table_gui import PanelTextObserver, SelfValidatingEntry
from pyDEA.core.gui_modules.table_gui import DefaultCategoriesAndDMUModifier


class PanelObserverMock(object):

    def __init__(self):
        self.notified = False

    def change_state_if_needed(self):
        self.notified = True


def test_CheckbuttonWithVar():
    parent = Tk()
    var = StringVar(master=parent)
    var.set(1)
    box = CheckbuttonWithVar(parent, var)
    box.deselect()
    assert var.get() == '0'
    parent.destroy()


def test_PanelTextObserver():
    parent = Tk()
    var = StringVar(master=parent)
    observer = PanelTextObserver(var)
    observer.change_state_if_needed()
    assert observer.if_text_modified_str.get() == '*'
    parent.destroy()


@pytest.fixture
def entry(request):
    parent = Tk()
    data = []
    entry = SelfValidatingEntry(parent, data, [])
    request.addfinalizer(parent.destroy)
    return entry


def test_SelfValidatingEntry_notify_text_observer(entry):
    entry.grid()
    entry.panel_text_observer = PanelObserverMock()
    entry.text_value.set('some text')
    assert entry.panel_text_observer.notified is True


def test_SelfValidatingEntry_manual_entry():
    parent = Tk()
    data = []
    cells = []
    for i in range(4):
        cells.append([])
        for j in range(5):
            entry = SelfValidatingEntry(parent, data, cells)
            cells[i].append(entry)
            entry.grid(row=i + 2, column=j + 1)

    entry = cells[2][4]
    entry.text_value.set('5')
    assert str(entry.cget('foreground')) == 'black'
    assert len(entry.data) == 2
    assert len(entry.data[0]) == 5
    assert len(entry.data[1]) == 5
    print(entry.data)

    entry2 = cells[3][0]
    entry2.text_value.set('ha')
    assert len(entry.data) == 3
    assert len(entry.data[0]) == 5
    assert len(entry.data[1]) == 5
    assert len(entry.data[2]) == 5

    entry3 = cells[3][4]
    entry3.text_value.set('abc')
    assert str(entry3.cget('foreground')) == 'red'
    assert len(entry.data[2]) == 5
    assert entry.data[2][4] == 'abc'
    assert entry.data[2][0] == 'ha'
    assert entry.data[1][4] == '5'

    entry4 = cells[1][0]
    entry4.text_value.set('dmu1')
    assert len(data[0]) == 5
    assert data[0][0] == 'dmu1'

    entry5 = cells[0][1]

    entry5.text_value.set('0')
    assert len(data[0]) == 5
    assert data[0][1] == '' # data in the first row is not modifiable

    entry3.text_value.set('0')
    assert data[2][4] == '0'
    assert str(entry3.cget('foreground')) == 'orange'

    entry6 = cells[3][3]
    entry6.text_value.set('new value ')
    assert str(entry6.cget('foreground')) == 'red'
    assert len(data[2]) == 5
    assert data[2][4] == '0'
    assert data[2][0] == 'ha'
    assert data[1][4] == '5'
    assert data[2][3] == 'new value'

    entry6.text_value.set(' 0.56')
    assert len(data[0]) == 5
    assert data[2][3] == '0.56'
    assert str(entry6.cget('foreground')) == 'black'
    parent.destroy()


def test_DefaultCategoriesAndDMUModifier():
    current_categories = []
    cells = []
    parent = Tk()
    data = []
    observer = DefaultCategoriesAndDMUModifier(cells, current_categories)
    for i in range(4):
        cells.append([])
        for j in range(5):
            entry = SelfValidatingEntry(parent, data, cells)
            entry.observers.append(observer)
            cells[i].append(entry)
            entry.grid(row=i + 2, column=j + 1)

    cells[1][1].text_value.set('5')
    assert cells[1][0].text_value.get() == 'DMU1'
    assert cells[0][1].text_value.get() == 'Category0'

    cells[3][4].text_value.set('some value')
    assert cells[3][0].text_value.get() == 'DMU3'
    assert cells[0][4].text_value.get() == 'Category3'
    val = 'new category name'
    cells[0][1].text_value.set(val)
    cells[3][1].text_value.set('10')
    assert cells[0][1].text_value.get() == val
    val = '   '
    cells[0][1].text_value.set(val)
    cells[3][1].text_value.set('10')
    assert cells[0][1].text_value.get() == 'Category0'
    parent.destroy()
