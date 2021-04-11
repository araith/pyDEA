''' This module contains classes responsible for displaying input data
    in a table (TableFrame and TableFrameWithInputOutputBox).
    It also contains many classes necessary for TableFrameWithInputOutputBox.

    Attributes:
        CELL_WIDTH (int): constant that defined width of a cell in a table
'''
from tkinter import S, N, E, W, END, VERTICAL, HORIZONTAL, ALL
from tkinter import IntVar, DISABLED, StringVar, NORMAL
from tkinter.ttk import Frame, Entry, Scrollbar, Checkbutton

from pyDEA.core.gui_modules.scrollable_frame_gui import MouseWheel
from pyDEA.core.utils.dea_utils import is_valid_coeff, NOT_VALID_COEFF, VALID_COEFF
from pyDEA.core.utils.dea_utils import WARNING_COEFF, EMPTY_COEFF, CELL_DESTROY
from pyDEA.core.utils.dea_utils import CHANGE_CATEGORY_NAME, INPUT_OBSERVER
from pyDEA.core.utils.dea_utils import OUTPUT_OBSERVER, on_canvas_resize
from pyDEA.core.utils.dea_utils import validate_category_name, calculate_nb_pages
from pyDEA.core.gui_modules.custom_canvas_gui import StyledCanvas
from pyDEA.core.data_processing.read_data import convert_to_dictionary

CELL_WIDTH = 10


class TableFrame(Frame):
    ''' This class is a base class that defines minimal functionality of
        a table.

        Attributes:
            parent (Tk object): parent of this widget.
            nb_rows (int): number of rows of the table.
            nb_cols (int): number of columns of the table.
            cells (list of list of Entry): list with Entry widgets
                (or derivatives of Entry)
                that describes the table and its content.
            canvas (Canvas): canvas that holds all widgets
                (it is necessary to make the table scrollable).
            frame_with_table (Frame): frame that holds all widgets.

        Args:
            parent (Tk object): parent of this widget.
            nb_rows (int, optional): number of rows of the table,
                defaults to 20.
            nb_cols (int, optional): number of columns of the table,
                defaults to 5.
    '''
    def __init__(self, parent, data, nb_rows=20, nb_cols=5):
        Frame.__init__(self, parent)
        self.data = data
        self.parent = parent
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols
        self.cells = []
        self.canvas = None
        self.frame_with_table = None
        self.create_widgets()

    def create_widgets(self):
        ''' Creates all widgets.
        '''
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        yScrollbar = Scrollbar(self, orient=VERTICAL)
        yScrollbar.grid(row=0, column=1, sticky=N+S)
        xScrollbar = Scrollbar(self, orient=HORIZONTAL)
        xScrollbar.grid(row=1, column=0, sticky=E+W)

        canvas = StyledCanvas(self, yscrollcommand=yScrollbar.set,
                              xscrollcommand=xScrollbar.set, bd=0)
        self.canvas = canvas
        canvas.grid(row=0, column=0, sticky=N+S+W+E)

        frame_with_table = Frame(canvas)
        self.frame_with_table = frame_with_table
        frame_with_table.grid(sticky=N+S+W+E, pady=15, padx=3)

        for i in range(2, self.nb_rows + 2):
            cols = []
            for j in range(1, self.nb_cols + 1):
                ent = self.create_entry_widget(frame_with_table)
                ent.grid(row=i, column=j, sticky=N+S+E+W)
                cols.append(ent)
            self.cells.append(cols)

        canvas.create_window(0, 0, window=frame_with_table, anchor='nw')
        canvas.update_idletasks()

        yScrollbar['command'] = canvas.yview
        xScrollbar['command'] = canvas.xview
        self._update_scroll_region()

        MouseWheel(self).add_scrolling(canvas, yscrollbar=yScrollbar)

    def create_entry_widget(self, parent):
        ''' Creates Entry widget.

            Args:
                parent (Tk object): parent of the Entry widget.

            Returns:
                Entry: created Entry widget.
        '''
        return Entry(parent, width=CELL_WIDTH)

    def add_row(self):
        ''' Adds one row to the end of the table.
        '''
        self.cells.append([])
        for j in range(self.nb_cols):
            grid_row_index = self.nb_rows + 2
            ent = self.create_entry_widget(self.frame_with_table)
            ent.grid(row=grid_row_index, column=j + 1, sticky=N+S+E+W)
            self.cells[self.nb_rows].append(ent)
        self.nb_rows += 1
        self._update_scroll_region()

    def add_column(self):
        ''' Adds one column to the end of the table.
        '''
        for i in range(self.nb_rows):
            grid_row_index = i + 2
            ent = self.create_entry_widget(self.frame_with_table)
            ent.grid(row=grid_row_index, column=self.nb_cols + 1,
                     sticky=N+S+E+W)
            self.cells[i].append(ent)
        self.nb_cols += 1
        self._update_scroll_region()

    def remove_row(self, row_index):
        ''' Removes row with a specified index from the table.
            If row_index is zero or larger than the total number of rows,
            no row is removed.

            Args:
                row_index (int): index of the row to remove.

            Returns:
                bool: True if row was deleted, False otherwise.
        '''
        # forbid deleting first row
        if self.should_remove_row(row_index):
            for j in range(self.nb_cols):
                self.before_cell_destroy(self.cells[row_index][j])
                self.cells[row_index][j].destroy()
                for i in range(row_index + 1, self.nb_rows):
                    self.cells[i][j].grid_remove()
                    self.cells[i][j].grid(row=i + 1)

            self.cells.remove(self.cells[row_index])
            self.nb_rows -= 1
            self._update_scroll_region()
            return True
        return False

    def should_remove_row(self, row_index):
        ''' Checks if row with a specified row index can be removed.

            Args:
                row_index (int): index of the row to remove.

            Returns:
                bool: True if row_index is >= 1 and < total number of rows,
                    False otherwise.
        '''
        return row_index >= 1 and row_index < self.nb_rows

    def remove_column(self, column_index):
        ''' Removes column with a specified index from the table.
            If column index is zero or larger than the total number of
            columns of the table, no column is removed.

            Args:
                column_index (int): index of the column to remove.

            Returns:
                bool: True if column was removed, False otherwise.
        '''
        # do not allow to delete first column
        if column_index > 0 and column_index < self.nb_cols:
            for i in range(self.nb_rows):
                self.cells[i][column_index].destroy()
                for j in range(column_index + 1, self.nb_cols):
                    self.cells[i][j].grid_remove()
                    self.cells[i][j].grid(column=j)

                self.cells[i].remove(self.cells[i][column_index])
            self.nb_cols -= 1
            self._update_scroll_region()
            return True
        return False

    def before_cell_destroy(self, cell):
        ''' This method is called before a table cell is destroyed.
            In this class this method does nothing, but can be redefined
            in children classes.

            Args:
                cell (Entry): cell that will be destroyed after call to
                    this method.
        '''
        pass

    def clear_all_data(self):
        ''' Clears all data from all cells.
        '''
        for i in range(self.nb_rows):
            for j in range(self.nb_cols):
                self.before_cell_clear(self.cells[i][j])
                self.cells[i][j].delete(0, END)

    def before_cell_clear(self, cell):
        ''' This method is called before data is cleared from a given cell.
            In this class this method does nothing, but can be redefined
            in children classes.

            Args:
                cell (Entry): cell that will be cleared after call
                to this method.
        '''
        pass

    def _update_scroll_region(self):
        ''' Updates scroll region. This method must be called each
            time table size or number of columns or rows change.
        '''
        # ensures that bbox will calculate border correctly
        self.frame_with_table.update()
        on_canvas_resize(self.canvas)

    def read_coefficients(self):
        ''' Converts data stored as a list to a proper dictionary
            necessary for constructing data instance.
        '''
        return convert_to_dictionary(self.data, self.check_value)

    def check_value(self, count):
        ''' This method is called in read_coefficients method to check what
            values must be returned for data instance construction.
            In this class it always returns True and can be redefined in
            children classes.
        '''
        return True


class TableFrameWithInputOutputBox(TableFrame):
    ''' Extends TableFrame with extra functionality necessary for data
        modification and choosing input and output categories.

        Attributes:
            params_frame (ParamsFrame): frame with parameters, this
                class communicates
                with params_frame when data is loaded or modified.
            combobox_text_var (StringVar): StringVar object that stores
                categorical category.
            panel_text_observer (PanelTextObserver): observer that adds star to
                label frame of the parent of this widget.
                This class notifies panel_text_observer
                when data was modified.
            frames (list of Frame): list of frames that hold Checkbuttons for
                choosing input and output categories.
            row_checkboxes (list of Checkbutton): list of Checkbuttons used
                for removing rows.
            col_checkboxes (list of Checkbutton): list of Checkbuttons used
                for removing columns.
            current_categories (list of str): list of current valid categories.
                This class might modify this list.
            str_var_for_input_output_boxes (StringVar): StringVar object that
                is used for communication
                with ParamsFrame. If the content of
                str_var_for_input_output_boxes was modified,
                it means that data was loaded from parameters file
                and input and output categories
                must be checked depending on parameters file.
            data (list of list of str or float): input data, it might
                be modified by this class.

        Args:
            parent (Tk object): parent of this widget.
            params_frame (ParamsFrame): frame with parameters, this class
                communicates
                with params_frame when data is loaded or modified.
            combobox_text_var (StringVar): StringVar object that stores
                categorical category.
            current_categories (list of str): list of current valid categories.
                This class might modify this list.
            str_var_for_input_output_boxes (StringVar): StringVar object
                that is used for communication
                with ParamsFrame. If the content of
                str_var_for_input_output_boxes was modified,
                it means that data was loaded from parameters file and input
                and output categories
                must be checked depending on parameters file.
            if_text_modified_str (StringVar): StringVar object that is used
                by PanelTextObserver, its content is modified when data
                was modified.
            data (list of list of str or float): input data, it might be
                modified by this class.
            nb_rows (int, optional): number of rows of the table, defaults
                to 20.
            nb_cols (int, optional): number of columns of the table,
                defaults to 5.
    '''
    def __init__(self, parent, params_frame,
                 combobox_text_var, current_categories,
                 str_var_for_input_output_boxes,
                 if_text_modified_str, data,
                 nb_rows=20, nb_cols=5):
        self.params_frame = params_frame
        self.combobox_text_var = combobox_text_var
        self.panel_text_observer = PanelTextObserver(if_text_modified_str)
        self.frames = []
        self.row_checkboxes = []
        self.col_checkboxes = []
        self.current_categories = current_categories
        self.str_var_for_input_output_boxes = str_var_for_input_output_boxes
        self.str_var_for_input_output_boxes.trace('w', self.on_load_categories)
        super().__init__(parent, data, nb_rows, nb_cols)

    def create_widgets(self):
        ''' Creates widgets of this class.
        '''
        super().create_widgets()
        for column_index in range(self.nb_cols - 1):
            self._create_input_output_box(column_index)
        for row_index in range(self.nb_rows):
            self.add_row_check_box(row_index)
        # add observers to add * in the first column
        for row_index in range(self.nb_rows):
            self.cells[row_index][0].panel_text_observer = self.panel_text_observer

    def create_entry_widget(self, parent):
        ''' Creates SelfValidatingEntry widget.

            Args:
                parent (Tk object): parent of the SelfValidatingEntry widget.

            Returns:
                SelfValidatingEntry: created SelfValidatingEntry widget.
        '''
        return SelfValidatingEntry(parent, self.data, self.cells, width=CELL_WIDTH)

    def deselect_all_boxes(self):
        ''' Deselects all Checkbuttons used for choosing input and
            output categories.
        '''
        for frame in self.frames:
            for child in frame.winfo_children():
                child.deselect()

    def _create_input_output_box(self, column_index):
        ''' Creates Checkbuttons used for choosing input and output categories.

            Args:
                column_index (int): index of a column for which
                    Checkbuttons must be created.
        '''
        frame_for_btns = Frame(self.frame_with_table)
        self.frames.append(frame_for_btns)
        input_var = IntVar()
        output_var = IntVar()
        input_btn = ObserverCheckbutton(
            frame_for_btns, input_var, output_var,
            self.params_frame.input_categories_frame,
            self.params_frame.output_categories_frame,
            self.current_categories, self.cells, INPUT_OBSERVER,
            self.params_frame.change_category_name,
            self.data, self.combobox_text_var,
            text='Input', state=DISABLED)
        input_btn.grid(row=1, column=0, sticky=N+W)
        output_btn = FollowingObserverCheckbutton(
            frame_for_btns, output_var, input_var,
            self.params_frame.output_categories_frame,
            self.params_frame.input_categories_frame,
            self.current_categories, self.cells, OUTPUT_OBSERVER,
            self.params_frame.change_category_name,
            self.data, self.combobox_text_var, input_btn,
            text='Output', state=DISABLED)
        output_btn.grid(row=2, column=0, sticky=N+W)
        self._add_observers(input_btn, output_btn, column_index + 1)
        var = IntVar()
        column_checkbox = CheckbuttonWithVar(frame_for_btns, var)
        column_checkbox.grid(row=0, column=0)
        self.col_checkboxes.append((column_checkbox, var))
        frame_for_btns.grid(row=1, column=column_index + 2, sticky=N)

    def _add_observers(self, input_btn, output_btn, column_index):
        ''' Adds observers to newly created cells in a given column.

            Args:
                input_btn (ObserverCheckbutton): observer used to select
                    input categories.
                output_btn (FollowingObserverCheckbutton): observer used
                    to select output categories.
                column_index (int): index of the column to cells of
                    which observers must be added.
        '''
        names_modifier = DefaultCategoriesAndDMUModifier(
            self.cells, self.current_categories)
        for row_index in range(self.nb_rows):
            self._add_observers_to_cell(self.cells[row_index][column_index],
                                        names_modifier, input_btn, output_btn)

    def _add_observers_to_cell(self, cell, names_modifier, input_btn,
                               output_btn):
        ''' Adds given observers to a given cell.

            Args:
                cell (SelfValidatingEntry): cell where observers must be added.
                names_modifier (DefaultCategoriesAndDMUModifier): observer,
                    for details see  DefaultCategoriesAndDMUModifier.
                input_btn (ObserverCheckbutton): observer used to select
                    input categories.
                output_btn (FollowingObserverCheckbutton): observer used to
                    select output categories.
        '''
        cell.observers.append(names_modifier)  # IMPORTANT:
        # this observer MUST be added first, it modifies data that
        # is used by other observers!
        cell.observers.append(input_btn)
        cell.observers.append(output_btn)
        cell.panel_text_observer = self.panel_text_observer

    def on_load_categories(self, *args):
        ''' Selects input and output categories when data is loaded from
            parameters file. Args are provided by the StringVar trace
            methods and are ignored in this method.
        '''
        for frame in self.frames:
            for child in frame.winfo_children():
                try:
                    category = child.get_category()
                except AttributeError:
                    pass
                else:
                    if (child.observer_type == INPUT_OBSERVER and
                            child.get_category() in
                            self.str_var_for_input_output_boxes.input_categories):
                        child.select()
                    if (child.observer_type == OUTPUT_OBSERVER and
                            child.get_category() in
                            self.str_var_for_input_output_boxes.output_categories):
                        child.select()

    def add_row_check_box(self, row_index):
        ''' Adds Checkbutton used for removing rows to a given row.

            Args:
                row_index (int): index of row to which Checkbutton
                    must be added.
        '''
        if row_index >= 1:
            var = IntVar()
            row_checkbox = Checkbutton(self.frame_with_table, variable=var)
            self.row_checkboxes.append((row_checkbox, var))
            row_checkbox.grid(row=row_index + 2, column=0)
        else:
            self.row_checkboxes.append((None, None))

    def add_column(self):
        ''' Adds one column to the end of table.
        '''
        super().add_column()
        self._create_input_output_box(self.nb_cols - 2)

    def add_row(self):
        ''' Adds one row to the end of table.

            Note: When data is spread across several pages, addition of
                row must also update the display of data.
                This functionality is implemented in TableModifierFrame.
        '''
        super().add_row()
        self.add_row_check_box(self.nb_rows - 1)
        names_modifier = DefaultCategoriesAndDMUModifier(
            self.cells, self.current_categories)
        for col in range(1, self.nb_cols):
            input_btn, output_btn = self.get_check_boxes(col - 1)
            self._add_observers_to_cell(self.cells[self.nb_rows - 1][col],
                                        names_modifier,
                                        input_btn, output_btn)

    def get_check_boxes(self, column_index):
        ''' Gets Checkbuttons used for selecting input and output categories
            for a given column.

            Args:
                column_index (int): index of the column for which Checkbuttons
                    must be returned.

            Returns:
                tuple of ObserverCheckbutton, FollowingObserverCheckbutton:
                    tuple of observers
                    or None, None if no observers were found.
        '''
        if column_index < 0 or column_index >= len(self.frames):
            return None, None
        input_btn = None
        output_btn = None
        for child in self.frames[column_index].winfo_children():
            try:
                observer_type = child.observer_type
            except AttributeError:
                pass
            else:
                if observer_type == INPUT_OBSERVER:
                    input_btn = child
                elif observer_type == OUTPUT_OBSERVER:
                    output_btn = child
        return input_btn, output_btn

    def remove_column(self, column_index):
        ''' Removes column with a specified index from the table.
            If column index is zero or larger than the total number of columns
            of the table, no column is removed.

            Args:
                column_index (int): index of the column to remove.

            Returns:
                bool: True if column was removed, False otherwise.
        '''
        # we must record category name before removing column,
        # because it will disappear
        if column_index < len(self.cells[0]):
            category_name = self.cells[0][column_index].get().strip()
        else:
            category_name = ''
        if super().remove_column(column_index):
            col = column_index - 1
            if category_name:
                self.params_frame.input_categories_frame.remove_category(
                    category_name)
                self.params_frame.output_categories_frame.remove_category(
                    category_name)

            if col < len(self.current_categories):
                self.current_categories[col] = ''
                # remove from data only if category is present
                if self.data:
                    column_with_data_removed = False
                    for row_index in range(len(self.data)):
                        if column_index < len(self.data[row_index]):

                            self.data[row_index].pop(column_index)
                            column_with_data_removed = True
                    if column_with_data_removed:
                        for row in range(1, self.nb_rows):
                            for j in range(column_index, self.nb_cols):
                                self.cells[row][j].data_column -= 1
                        self.panel_text_observer.change_state_if_needed()

            self.frames[col].destroy()
            for i in range(col + 1, len(self.frames)):
                self.frames[i].grid_remove()
                self.frames[i].grid(column=i + 1)
            self.frames.pop(col)
            self.col_checkboxes.pop(col)
            return True
        return False

    def remove_row(self, row_index):
        ''' Removes data row with a specified index from the table.
            Row is not physically removed.
            If row_index is zero or larger than the total number of rows,
            no row is removed.

            Args:
                row_index (int): index of the row to remove.

            Returns:
                bool: True if row was deleted, False otherwise.
        '''
        if self.should_remove_row(row_index):
            
            if self.data:
                nb_pages = calculate_nb_pages(len(self.data), self.nb_rows)
                data_index = self.get_data_index(row_index)
                nb_cols = len(self.cells[row_index])
                
                if data_index != -1 and data_index < len(self.data):
                    nb_rows_to_change = min(self.nb_rows, len(self.data) + 1)
                    self.data.pop(data_index)
                    for row in range(row_index + 1, nb_rows_to_change):
                        for col in range(0, nb_cols):
                            if self.cells[row][col].data_row != -1:
                                self.cells[row][col].data_row -= 1

                    self.panel_text_observer.change_state_if_needed()

                super().remove_row(row_index)
                if (nb_pages > 1):
                    self.add_row()
            else:
                super().remove_row(row_index)

            self.row_checkboxes[row_index][0].destroy()
            for i in range(row_index + 1, len(self.row_checkboxes)):
                self.row_checkboxes[i][0].grid_remove()
                self.row_checkboxes[i][0].grid(row=i + 1)
            self.row_checkboxes.pop(row_index)

            return True
        return False

    def get_data_index(self, row_index):
        for j in range(0, len(self.cells[row_index])):
                if self.cells[row_index][j].data_row != -1:
                    return self.cells[row_index][j].data_row
        return -1
                        
    def before_cell_destroy(self, cell):
        ''' This method is called before a table cell is destroyed.
            Notifies observers if data is not empty.

            Args:
                cell (SelfValidatingEntry): cell that will be destroyed
                    after call to this method.
        '''
        info = cell.grid_info()
        col = int(info['column'])
        row = int(info['row'])
        if len(self.data) == 0:
            cell.notify_observers(CELL_DESTROY, row, col)

    def load_visible_data(self):
        ''' Displays data in the table. First, it adds more rows to fill
            the frame, second, it displays data that fits the table.
        '''
        self.add_rows_to_fill_visible_frame()
        self.display_data()

    def display_data(self, start_row=0):
        ''' Displays data starting from a given data row.
            This method is usually called by NavigationForTableFrame when
            data spans across
            several pages and users clicks on page navigation buttons.

            Args:
                start_row (int, optional): index of input data starting
                    from which data should be displayed, defaults to 0.
        '''
        nb_data_rows = len(self.data)
        nb_displayed_rows = 0
        for row_index in range(start_row, nb_data_rows):
            values = self.data[row_index]
            # do not insert data that is not visible
            if nb_displayed_rows + 1 >= self.nb_rows:
                return
            for column_index, coeff in enumerate(values):
                # row_index + 1 - first row has categories
                self._display_one_cell(nb_displayed_rows, column_index,
                                       coeff, row_index,
                                       column_index, False)
            row_index += 1
            nb_displayed_rows += 1

        if len(self.data) > 0:
            nb_cols = len(self.data[0])
        else:
            nb_cols = self.nb_cols

        nb_rows = self.nb_rows - 1  # -1 because we add +1 to row_index
        while nb_displayed_rows < nb_rows:
            for column_index in range(nb_cols):
                self._display_one_cell(nb_displayed_rows, column_index, '',
                                       -1, -1, False)
            nb_displayed_rows += 1

    def _display_one_cell(self, row_index, column_index, value_to_dispay,
                          data_row, data_col, modify_data=True):
        ''' Displays data in a cell and sets cell's fields to proper values.

            Args:
                row_index (int): index of a row where the cell is.
                column_index (int): index of a column where the cell is.
                value_to_dispay (str): new cell value_to_dispay.
                data_row (int): row index of input data.
                data_col (int): column index of input data.
                modify_data (bool, optional): True if data was modified and
                    observers
                    must be notified, False otherwise.
        '''
        cell_row_index = row_index + 1
        self.cells[cell_row_index][column_index].modify_data = modify_data
        self.cells[cell_row_index][column_index].text_value.set(value_to_dispay)
        self.cells[cell_row_index][column_index].data_row = data_row
        self.cells[cell_row_index][column_index].data_column = data_col

    def add_rows_to_fill_visible_frame(self):
        ''' Adds rows to table to fill the frame. Usually adds a bit more and
            scroll gets activated.
            Exact number of added rows depends on operating system, height of
            widgets and screen size.
        '''
        self.canvas.update_idletasks()
        frame_height = self.canvas.winfo_height()
        while self.canvas.bbox(ALL)[3] <= frame_height - 20:
            self.add_row()
        self._update_scroll_region()

    def check_value(self, count):
        ''' This method is called in read_coefficients method to check what
            values must be returned for data instance construction.

            Args:
                count (int): data column index.
            Returns:
                bool: True if the category in the given column index is not
                    an empty string,
                    False otherwise.
        '''
        if self.current_categories[count]:
            return True
        return False

    def clear_all_data(self):
        ''' Clears all data from all cells and clears input data.
        '''
        self.data.clear()
        super().clear_all_data()
        self.current_categories.clear()
        # reset modify data back to true
        for cell_row in self.cells:
            for cell in cell_row:
                cell.modify_data = True

    def before_cell_clear(self, cell):
        ''' This method is called before data is cleared from a given cell.
            It sets fields of the given cell to initial values.

            Args:
                cell (SelfValidatingEntry): cell that will be cleared after
                    call to this method.
        '''
        cell.modify_data = False
        cell.data_row = -1
        cell.data_column = -1


class ObserverCheckbutton(Checkbutton):
    ''' This class implements Checkbutton for choosing input/output categories.

        Attributes:
            var (IntVar): variable that is set to 1 when Checkbutton is
                selected, to 0 otherwise.
            opposite_var (IntVar): variable of the other Checkbutton that
                must deselected if this Checkbutton is selected.
            parent (Tk object): frame that holds this Checkbutton.

                Warning:
                    it is important for the parent to be gridded in the
                    same column
                    as the entire column of table entries is gridded, because
                    this class uses parent grid column index to determine
                    the column where the category name can be read from.

            category_frame (CategoriesCheckBox): frame that displays selected
                input or output categories.

                Note:
                    if this Checkbutton is used to select input categories,
                    category_frame must be CategoriesCheckBox object that
                    displays selected input categories.
                    if this Checkbutton is used to select output categories,
                    category_frame  must be CategoriesCheckBox object that
                    displays selected output categories.

            opposite_category_frame (CategoriesCheckBox): frame that displays
                selected input or output categories. If category_frame
                displays input categories, then opposite_category_frame
                must display output categories, and vice versa.
            current_categories (list of str): list of categories. This class
                might modify this list by removing invalid categories and
                adding the valid ones.
            cells (list of list of SelfValidatingEntry): all entry widgets
                collected in list.
            data (list of list of str or float): input data.
            observer_type (int): describes type of the observer, for possible
                values see dea_utils.
            change_category_name (callable function): this function is
                called when name of a category was changed.
            combobox_text_var (StringVar): variable of the combobox used for
                selecting categorical category.

        Arguments are the same as attributes.
    '''
    def __init__(self, parent, var, opposite_var, category_frame,
                 opposite_category_frame,
                 current_categories, cells,
                 observer_type, change_category_name, data,
                 combobox_text_var, *args, **kw):
        Checkbutton.__init__(self, parent, variable=var,
                             command=self._process, *args, **kw)
        self.var = var
        self.opposite_var = opposite_var
        self.parent = parent
        self.category_frame = category_frame
        self.opposite_category_frame = opposite_category_frame
        self.current_categories = current_categories
        self.cells = cells
        self.data = data
        self.observer_type = observer_type
        self.change_category_name = change_category_name
        self.combobox_text_var = combobox_text_var

    def _process(self):
        ''' This method is called when user clicks on Checkbutton.
            Makes sure that the same category can be only input or only
            output, but not both, and that selected category cannot also
            be selected as a categorical category.
        '''
        category_name = self.get_category()
        if self.var.get() == 1:
            self.opposite_var.set(0)

            if category_name:
                self.category_frame.add_category(category_name)
                self.opposite_category_frame.remove_category(category_name)
            if category_name == self.combobox_text_var.get():
                self.combobox_text_var.set('')
        elif category_name:
            self.category_frame.remove_category(category_name)

    def deselect(self):
        ''' Deselects Checkbutton.

            Note:
                method _process() is not called in this case.
        '''
        self.var.set(0)

    def select(self):
        ''' Selects Checkbutton.

            Note:
                method _process() is not called in this case.
        '''
        self.var.set(1)

    def change_state_if_needed(self, entry, entry_state, row, col):
        ''' Changes state of Checkbutton when data or categories were modified.
            Also modifies current_categories if needed.
            This widget becomes disabled if invalid category name value or input
            data value were provided by user.

            Args:
                entry (SelfValidatingEntry): Entry widget whose content was
                    modified.
                entry_state (int): state of the Entry widget after content
                    modification, for possible values see dea_utils module.
                row (int): row index of entry widget. It is the real grid value,
                    we need to subtract 2 to get internal index.
                col (int): column index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.

        '''
        if entry_state == CHANGE_CATEGORY_NAME:
            old_name = ''
            internal_col = col - 2
            if internal_col < len(self.current_categories):
                old_name = self.current_categories[internal_col]

            category_name = validate_category_name(
                self.cells[0][col - 1].text_value.get().strip(),
                internal_col, self.current_categories)

            if category_name:

                index = len(self.current_categories)
                while index <= internal_col:
                    self.current_categories.append('')
                    index += 1
                self.current_categories[internal_col] = category_name

                if old_name:
                    # change category name in params_frame
                    self.change_category_name(old_name.strip(), category_name)
                self.change_state_based_on_data(entry, entry_state, row, col)
                entry.config(foreground='black')

            else:
                # if category name is empty, disable
                self.disable(internal_col, old_name)
                entry.config(foreground='red')

        else:
            self.change_state_based_on_data(entry, entry_state, row, col)

    def change_state_based_on_data(self, entry, entry_state, row, col):
        ''' Changes state of Checkbutton when data was modified.

            Args:
                entry (SelfValidatingEntry): Entry widget whose content
                    was modified.
                entry_state (int): state of the Entry widget after content
                    modification, for possible values see dea_utils module.
                row (int): row index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.
                col (int): column index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.
        '''
        internal_col = col - 2
        # IMPORTANT: read from cells, not from current_categories, they might
        # be empty at this stage
        category_name = self.cells[0][col - 1].text_value.get().strip()
        nb_rows = len(self.data)
        if nb_rows == 0:
            self.disable(internal_col, category_name)
            return
        elif len(self.data[0]) == 0:
            self.disable(internal_col, category_name)
            return

        has_one_valid_entry = False
        for row_index in range(nb_rows):
            # can happen if some values are empty
            while col - 1 >= len(self.data[row_index]):
                self.data[row_index].append('')
            try:
                # col - 1  - first column contains DMU names
                data_elem = float(self.data[row_index][col - 1])
            except ValueError:
                state = NOT_VALID_COEFF
            else:
                state = is_valid_coeff(data_elem)
            if state == NOT_VALID_COEFF:
                has_one_valid_entry = False
                self.disable(internal_col, category_name)
                return
            elif state == VALID_COEFF or state == WARNING_COEFF:
                has_one_valid_entry = True

        if has_one_valid_entry:
            self.config(state=NORMAL)
            if category_name:
                if category_name not in self.current_categories:
                    assert internal_col < len(self.current_categories)
                    self.current_categories[internal_col] = category_name
                if entry_state != CELL_DESTROY and self.var.get() == 1:
                    self.category_frame.add_category(category_name)
            return

    def disable(self, internal_col, category_name):
        ''' Disables Checkbutton.

            Args:
                internal_col (int): internal column index.
                category_name (str): name of category.
        '''
        self.config(state=DISABLED)
        if category_name:
            if self.var.get() == 1:
                self.category_frame.remove_category(category_name)
            if self.opposite_var.get() == 1:
                self.opposite_category_frame.remove_category(category_name)
            if category_name in self.current_categories:
                assert(internal_col < len(self.current_categories))
                self.current_categories[internal_col] = ''
            if category_name == self.combobox_text_var.get():
                self.combobox_text_var.set('')

    def get_category(self):
        ''' Finds category name stored in the corresponding Entry widget
            based on where parent of Checkbutton was gridded.

            Returns:
                str: category name, might be empty string.
        '''
        info = self.parent.grid_info()
        # convertion to int is necessary for Windows
        # for some reason in Windows grid info is stored as str
        col = int(info['column'])
        return self.cells[0][col - 1].text_value.get().strip()


class FollowingObserverCheckbutton(ObserverCheckbutton):
    ''' This class follows state of another ObserverCheckbutton that is
        used to select input or output categories.
        This class is used in order to skip checking if data is valid
        second time. The first Checkbutton has already performed this check.

        Attributes:
            var (IntVar): variable that is set to 1 when Checkbutton
                is selected, to 0 otherwise.
            opposite_var (IntVar): variable of the other Checkbutton that
                must deselected if this Checkbutton is selected.
            parent (Tk object): frame that holds this Checkbutton.

                Warning:
                    it is important for the parent to be gridded in the
                    same column as the entire column of table entries
                    is gridded, because this class uses parent grid column
                    index to determine the column
                    where the category name can be read from.

            category_frame (CategoriesCheckBox): frame that displays
                selected input or output categories.

                Note:
                    if this Checkbutton is used to select input categories,
                    category_frame must be CategoriesCheckBox object that
                    displays selected input categories.
                    if this Checkbutton is used to select output categories,
                    category_frame
                    must be CategoriesCheckBox object that displays selected
                    output categories.

            opposite_category_frame (CategoriesCheckBox): frame that displays
                selected input or output categories. If category_frame displays
                input categories, then opposite_category_frame
                must display output categories, and vice versa.
            current_categories (list of str): list of categories. This class
                might modify this list by removing invalid categories and
                adding the valid ones.
            cells (list of list of SelfValidatingEntry): all entry widgets
                collected in list.
            data (list of list of str or float): input data.
            observer_type (int): describes type of the observer, for
                possible values see dea_utils.
            change_category_name (callable function): this function is called
                when name of a category was changed.
            combobox_text_var (StringVar): variable of the combobox used for
                selecting categorical category.
            main_box (ObserverCheckbutton): Checkbutton that changes state
                first. This Checkbutton changes its state to the same state
                as main_box, but does not do extra things
                that have been already performed by main_box
                (changes to current_categories, for example).
    '''
    def __init__(self, parent, var, opposite_var, category_frame,
                 opposite_category_frame,
                 current_categories, cells,
                 observer_type, params_frame, data,
                 combobox_text_var, main_box, *args, **kw):
        super().__init__(parent, var, opposite_var, category_frame,
                         opposite_category_frame, current_categories, cells,
                         observer_type, params_frame, data,
                         combobox_text_var, *args, **kw)
        self.main_box = main_box

    def change_state_if_needed(self, entry, entry_state, row, col):
        ''' Changes state of Checkbutton when data was modified depending on
            the state of main_box.

            Args:
                entry (SelfValidatingEntry): Entry widget whose content
                    was modified.
                entry_state (int): state of the Entry widget after content
                    modification, for possible values see dea_utils module.
                row (int): row index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.
                col (int): column index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.
        '''
        category_name = self.get_category()
        if str(self.main_box.cget('state')) == DISABLED:
            self.disable(col - 2, category_name)
        else:
            self.config(state=NORMAL)
            if entry_state != CELL_DESTROY and self.var.get() == 1:
                self.category_frame.add_category(category_name)


class DefaultCategoriesAndDMUModifier(object):
    ''' This class is responsible for adding automatic category and DMU names
        if user starts typing data without providing such names first.

        Attributes:
            cells (list of list of SelfValidatingEntry): list of all Entry
                widgets with data.
            current_categories (list of str): list of categories.

        Args:
            cells (list of list of SelfValidatingEntry): list of all Entry
                widgets with data.
            current_categories (list of str): list of categories.
    '''
    def __init__(self, cells, current_categories):
        self.cells = cells
        self.current_categories = current_categories

    def change_state_if_needed(self, entry, entry_state, row, col):
        ''' Writes automatic category and DMU names if they were not
            specified before.

            Args:
                entry (SelfValidatingEntry): Entry widget the content
                    of which was modified.
                entry_state (int): constant that describes entry state,
                    for details see dea_utils module.
                row (int): row index of entry widget. It is the real grid value,
                    we need to subtract 2 to get internal index.
                col (int): column index of entry widget. It is the real grid
                    value, we need to subtract 2 to get internal index.
        '''
        if (entry_state != EMPTY_COEFF and entry_state != CELL_DESTROY and
                entry_state != CHANGE_CATEGORY_NAME):
            internal_row_index = row - 2
            dmu_name = self.cells[internal_row_index][0].text_value.get().strip()
            if not dmu_name:
                self.cells[internal_row_index][0].text_value.set(
                    'DMU{0}'.format(internal_row_index))
            category_name = self.cells[0][col - 1].text_value.get().strip()
            if not category_name:
                internal_col_index = col - 2
                name = 'Category{0}'.format(internal_col_index)
                if internal_col_index >= len(self.current_categories):
                    index = len(self.current_categories) - 1
                    while index != internal_col_index:
                        self.current_categories.append('')
                        index += 1

                # category name MUST be written first, because next line calls
                # ObserverCheckbutton
                self.cells[0][col - 1].text_value.set(name)


class SelfValidatingEntry(Entry):
    ''' This class implement Entry widget that knows how to highlight
        invalid data. It also notifies other widgets if the content of
        Entry changes. Other widgets must implement method
        change_state_if_needed().
        Such widgets should be appended to the list of listening widgets
        called observers.

        Attributes:
            text_value (StringVar): textvariable of Entry widget that
                calls method on_text_changed when the content on Entry changes.
            observers (list of objects that implement method change_state_if_needed):
                list of widgets or other objects that must be notified if the
                content of Entry changes.
            data_row (int): row index in data table which should be modified
                when the content of Entry changes.
            data_column (int): column index in data table which should be
                modified when the content of Entry changes.
            data (list of list of srt or float): data that will be modified.
            modify_data (bool): True if data should be modified, False
                otherwise. It is usually set to False when data is uploaded
                from file.
            panel_text_observer (PanelTextObserver): object that is notified
                when data changes.
                This object is responsible for adding star to file name when
                data was modified.
            all_cells (list of list of SelfValidatingEntry): refernce where all cells 
                are stored.
                    Warning: all cells must be created before any cell content
                        can be modified.

        Args:
            parent (Tk object): parent of this Entry widget.
            data (list of list of srt or float): input data that will
                be modified.
            all_cells (list of list of SelfValidatingEntry): refernce where all cells 
                are stored.
                    Warning: all cells must be created before any cell content
                        can be modified.
    '''
    def __init__(self, parent, data, all_cells, *args, **kw):
        self.text_value = StringVar(master=parent)
        self.text_value.trace("w", self.on_text_changed)
        super().__init__(parent, *args, **kw)
        self.config(textvariable=self.text_value)
        self.observers = []
        self.all_cells = all_cells
        self.data_row = -1
        self.data_column = -1
        self.data = data
        self.modify_data = True
        self.panel_text_observer = None

    def on_text_changed(self, *args):
        ''' This method is called each time the content of Entry is modified.
            It highlights invalid data, changes data if needed and notifies
            other objects when data was changed.
            Args are provided by StringVar trace method, but are not used.
        '''
        info = self.grid_info()
        # phisical grid indeces
        col = int(info['column'])
        row = int(info['row'])

        self.notify_panel_observer()
        if row == 2:  # possibly name of category is modified
            self.notify_observers(CHANGE_CATEGORY_NAME, row, col)
        elif col == 1 and row > 2:  # column with DMU names, strings are allowed
            self.modify_data_if_needed(row, col)
        elif col > 1 and row > 2:  # everything left
            self.modify_data_if_needed(row, col)
            try:
                value = float(self.text_value.get().strip())
            except ValueError:
                self.modify_data = True
                self.config(foreground='red')
                if len(self.text_value.get().strip()) == 0:
                    self.notify_observers(EMPTY_COEFF, row, col)
                else:
                    self.notify_observers(NOT_VALID_COEFF, row, col)
                return
            text_status = is_valid_coeff(value)
            if text_status == NOT_VALID_COEFF:
                self.config(foreground='red')
            elif text_status == WARNING_COEFF:
                self.config(foreground='orange')
            else:
                self.config(foreground='black')

            self.notify_observers(text_status, row, col)
        self.modify_data = True

    def modify_data_if_needed(self, row, col):
        ''' Modifies data if modify_data is set to True.
            Adds empty strings to data when user modifies Entry for which
            data_row or/and data_column are equal to -1. Updates data with new
            values entered by user.

            Args:
                row (int): row where Entry is gridded
                col (int): column where Entry is gridded

        '''
        if self.modify_data:
            if self.data_row != -1 and self.data_column != -1:
                self.data[self.data_row][self.data_column] = self.text_value.get().strip()
            else:

                row_for_data = len(self.data)
                added_rows = False
                # -2 because row is physical grid index, not cell index
                row_count = len(self.all_cells) - 1
                for cells_row in reversed(self.all_cells):
                    if cells_row[0].data_row != -1:
                        break
                    row_count -= 1
                if row_count == -1:
                    row_count = 0
                while row_count < row - 2:
                    self.data.append([])
                    added_rows = True
                    row_count += 1
                if added_rows:
                    self.data_row = len(self.data) - 1
                else:
                    assert row_count >= row - 2
                    self.data_row = len(self.data) - 1 - (row_count - (row - 2))
                col_for_data = len(self.data[self.data_row])
                added_cols = False
                max_nb_col = 0
                nb_rows = len(self.data)
                for r_ind in range(nb_rows):
                    row_len = len(self.data[r_ind])
                    if row_len > max_nb_col:
                        max_nb_col = row_len
                max_nb_col = max(max_nb_col, col)
                c_ind = col_for_data
                while c_ind < max_nb_col:
                    self.data[self.data_row].append('')
                    grid_col = len(self.data[self.data_row])
                    self.all_cells[row - 2][grid_col - 1].data_row = self.data_row
                    self.all_cells[row - 2][grid_col - 1].data_column = c_ind
                    self.notify_observers(EMPTY_COEFF, row, grid_col)
                    added_cols = True
                    c_ind += 1
                    if (col_for_data < col):
                        col_for_data += 1
                
                if added_cols:
                    for r_ind in range(nb_rows):
                        while len(self.data[r_ind]) < max_nb_col:
                            self.data[r_ind].append('')
                            grid_col = len(self.data[r_ind])
                            if r_ind >= self.data_row - (row - 3):  # 3 is the first physical 
                            # row with data on the page
                                grid_row = row - (self.data_row - r_ind)
                                
                                self.all_cells[grid_row - 2][grid_col - 1].data_row = r_ind
                                self.all_cells[grid_row - 2][grid_col - 1].data_column = grid_col - 1
                                self.notify_observers(EMPTY_COEFF, grid_row, grid_col)

                    self.data_column = col_for_data - 1
                else:
                    self.data_column = col - 1
                self.data[self.data_row][self.data_column] = self.text_value.get().strip()

    def notify_panel_observer(self):
        ''' Notifies panel observer that data was modified.
        '''
        if self.panel_text_observer is not None and self.modify_data is True:
            self.panel_text_observer.change_state_if_needed()

    def notify_observers(self, entry_state, row, col):
        ''' Notifies all observers stored in list of observers that data
            was modified.

            Args:
                entry_state (int): state of the Entry widget that describes if
                    data is valid after modification, for possible values see
                    dea_utils module.
                row (int): row where Entry is gridded.
                col (int): column where Entry is gridded.
        '''
        for observer in self.observers:
            observer.change_state_if_needed(self, entry_state, row, col)


class PanelTextObserver(object):
    ''' This class changes StringVar value that is traced in other classes.

        Attributes:
            if_text_modified_str (StringVar): StringVar object that
                changes value when this observer is notified.
    '''
    def __init__(self, if_text_modified_str):
        self.if_text_modified_str = if_text_modified_str

    def change_state_if_needed(self):
        ''' Changes value of internal StringVar object.
        '''
        self.if_text_modified_str.set('*')


class CheckbuttonWithVar(Checkbutton):
    ''' Custom Checkbutton widget that provides deselect method.

        Attributes:
            var (IntVar): 0 if not selected, 1 otherwise.

        Args:
            parent (Tk object): parent of this widget.
            var (IntVar): variable that controls if Checkbutton is selected.
    '''
    def __init__(self, parent, var, *args, **kw):
        super().__init__(parent, variable=var, *args, **kw)
        self.var = var

    def deselect(self):
        ''' Deselects Checkbutton.
        '''
        self.var.set(0)
