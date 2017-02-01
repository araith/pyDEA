''' This module contains class responsible for displaying and
    configuring categories.

    Attributes:
        MIN_COLUMN_WIDTH (int): minimum column width.
        MIN_COLUMN_WIDTH_NAME (int): minimum text width of the column.
        HEIGHT_WITHOUT_CHECKBOXES (int): widget height.
        COUNT_TO_NAME (dict of int to str): dictionary that maps index
            to parameter name.
'''

from tkinter import W, E, S, N, LEFT, VERTICAL
from tkinter import IntVar, ALL
from tkinter.ttk import Frame, Label, Scrollbar
from tkinter.ttk import Separator, LabelFrame, Checkbutton

from pyDEA.core.gui_modules.scrollable_frame_gui import MouseWheel
from pyDEA.core.gui_modules.custom_canvas_gui import StyledCanvas

MIN_COLUMN_WIDTH = 150
MIN_COLUMN_WIDTH_NAME = 160
HEIGHT_WITHOUT_CHECKBOXES = 110
COUNT_TO_NAME = {0: 'NON_DISCRETIONARY_CATEGORIES',
                 1: 'WEAKLY_DISPOSAL_CATEGORIES'}


class CategoriesCheckBox(LabelFrame):
    ''' This class implement a widget for displaying and
        configuring categories.

        Attributes:
            parent (Tk object): widget parent.
            frame_with_boxes (Frame): frame for check buttons.
            canvas (StyledCanvas): canvas for all objects of this widget.
            options (dict of str to list of IntVar and int): dictionary
                that maps
                category name to two IntVar objects that keep track of the
                state of check buttons and grid row index.
                The first check button is used
                for checking if category is non-discretionary. The second
                check button is used for checking if category is weakly
                disposal.
            nb_entries (int): total number of categories.
            add_headers (bool): if set to True, the widget displays column
                headers, if set to False column headers are not
                displayed.
            category_objects (dict of list of Tk objects): dictionary that
                maps category name to a list with three elements. The first
                element is Label with category name, the remaining elements
                are Checkbuttons used for non-discretionary and weakly
                disposal categories.
            params (Parameters): parameters of the model.
            category_type (str): INPUT_CATEGORIES or OUTPUT_CATEGORIES,
                defines type of categories (input or output).

        Args:
            parent (Tk object): widget parent.
            label_text (str): text that will be displayed on top of this widget.
            add_headers (bool): if set to True, the widget displays column
                headers, if set to False column headers are not
                displayed.
            params (Parameters): parameters of the model.
            category_type (str): INPUT_CATEGORIES or OUTPUT_CATEGORIES,
                defines type of categories (input or output).
    '''
    def __init__(self, parent, label_text, add_headers, params,
                 category_type, *args, **kw):
        LabelFrame.__init__(self, parent, text=label_text, *args, **kw)
        self.parent = parent
        self.frame_with_boxes = None
        self.canvas = None
        self.options = dict()
        self.nb_entries = 0
        self.add_headers = add_headers
        self.category_objects = dict()
        self.params = params
        self.category_type = category_type
        self.create_widgets()

    def create_widgets(self):
        ''' Creates widgets of this object.
        '''
        yScrollbar = Scrollbar(self, orient=VERTICAL)
        yScrollbar.grid(row=2, column=3, sticky=N+S)

        canvas = StyledCanvas(self, height=HEIGHT_WITHOUT_CHECKBOXES,
                              yscrollcommand=yScrollbar.set)
        self.canvas = canvas
        canvas.grid(row=2, column=0, columnspan=3, sticky=N+E+W)

        self._config_columns(self)
        canvas.columnconfigure(0, weight=1)

        if self.add_headers:
            non_discr_lbl = Label(self, text='Non-\ndiscretionary')
            non_discr_lbl.grid(row=0, column=1, padx=3, pady=1)
            weakly_disp_lbl = Label(self, text='Weakly\ndisposable')
            weakly_disp_lbl.grid(row=0, column=2, padx=3, pady=1)
            sep = Separator(self)
            sep.grid(row=1, column=0, columnspan=3, sticky=E+W, pady=10, padx=3)

        self.frame_with_boxes = Frame(canvas)
        self._config_columns(self.frame_with_boxes)
        self.frame_with_boxes.grid(sticky=N+S+W+E, pady=15, padx=3)

        canvas.create_window(0, 0, window=self.frame_with_boxes, anchor=N+W)
        canvas.update_idletasks()

        canvas['scrollregion'] = (0, 0, 0, HEIGHT_WITHOUT_CHECKBOXES)
        yScrollbar['command'] = canvas.yview

        MouseWheel(self).add_scrolling(canvas, yscrollbar=yScrollbar)

    def add_category(self, category_name):
        ''' Adds a given category to this object. If the given
            category already exists, it won't be added again. Category
            names are assumed to be unique.

            Args:
                category_name (str): name of the category to add.
        '''
        if category_name not in self.category_objects.keys():
            categories = self.params.get_set_of_parameters(self.category_type)
            if category_name not in categories:
                categories.add(category_name)
                self.params.update_parameter(self.category_type,
                                             ';'.join(categories))
            self.nb_entries += 1
            row_index = self.nb_entries
            self.options[category_name] = [IntVar(), IntVar(), row_index]

            box = Label(self.frame_with_boxes, text=category_name,
                        justify=LEFT, wraplength=MIN_COLUMN_WIDTH_NAME - 10)
            box.grid(row=row_index, column=0, sticky=W, padx=7, pady=5)
            btn = []
            for count in range(2):
                check_btn = Checkbutton(self.frame_with_boxes,
                                        variable=
                                        self.options[category_name][count])
                check_btn.config(command=(lambda count=count:
                                          self.on_select_box(box, count)))
                btn.append(check_btn)
                btn[count].grid(row=row_index, column=count + 1, pady=5)

            self.category_objects[category_name] = (box, btn[0], btn[1])
            nd_categories = self.params.get_set_of_parameters(
                'NON_DISCRETIONARY_CATEGORIES')
            if category_name in nd_categories:
                btn[0].invoke()

            wd_categories = self.params.get_set_of_parameters(
                'WEAKLY_DISPOSAL_CATEGORIES')
            if category_name in wd_categories:
                btn[1].invoke()
            self.update_scroll_region()

    def change_category_name(self, old_name, new_name):
        ''' Changes category name if such a category is present.

            Args:
                old_name (str): previous category name that should
                    be changed.
                new_name (str): new category name.
        '''
        if old_name in self.category_objects.keys():
            self.category_objects[new_name] = self.category_objects.pop(
                old_name)
            self.category_objects[new_name][0].config(text=new_name)
            self.options[new_name] = self.options.pop(old_name)
            self.params.change_category_name(old_name, new_name)

    def on_select_box(self, box, count):
        ''' This method is called when the user clicks on a Checkbutton.
            It updates corresponding parameters that must be changed
            after clicking on Checkbutton.

            Args:
                box (Label): Label that stores category name.
                count (int): index of the Checkbutton that distinguishes
                    between Checkbuttons responsible for non-discretionary
                    categories and weakly disposal categories.
        '''
        param_name = COUNT_TO_NAME[count]
        category_name = box.cget('text')
        if self.options[category_name][count].get() == 1:
            value = self.params.get_parameter_value(param_name)
            if value:
                value += '; '
            self.params.update_parameter(param_name, value + category_name)
        else:
            values = self.params.get_set_of_parameters(param_name)
            if category_name in values:
                values.remove(category_name)
            new_value = '; '.join(values)
            self.params.update_parameter(param_name, new_value)

    def _destroy_category_boxes(self, category_name):
        ''' Destroys all widgets associated with a given category
            name.

            Args:
                category_name (str): category name.
        '''

        for i in range(3):
            self.category_objects[category_name][i].destroy()
        row_index = self.options[category_name][2]
        for name, option in self.options.items():
            row = option[2]
            if row > row_index:
                # re-grid all categories below removed category
                self.options[name][2] = row - 1
                for i in range(3):
                    self.category_objects[name][i].grid_remove()
                    self.category_objects[name][i].grid(row=row - 1)
        self.options.pop(category_name)
        self.params.remove_category_from_params(self.category_type,
                                                category_name)
        self.params.remove_category_from_params('WEAKLY_DISPOSAL_CATEGORIES',
                                                category_name)
        self.params.remove_category_from_params('NON_DISCRETIONARY_CATEGORIES',
                                                category_name)

    def remove_category(self, category_name):
        ''' Removes given category, destroys all widgets associated with
            this category and updates corresponding parameters.

            Args:
                category_name (str): category name.
        '''
        if category_name in self.category_objects.keys():
            self._destroy_category_boxes(category_name)
            self.category_objects.pop(category_name)
            self.update_scroll_region()
            self.nb_entries -= 1

    def remove_all_categories(self):
        ''' Removes all categories.
        '''
        for category_name in self.category_objects.keys():
            self._destroy_category_boxes(category_name)
        self.update_scroll_region()
        self.category_objects.clear()
        self.nb_entries = 0

    def _config_columns(self, frame):
        ''' Configures columns of a given frame.

            Args:
                frame (Frame): frame to configure.
        '''
        frame.columnconfigure(0, minsize=MIN_COLUMN_WIDTH_NAME)
        frame.columnconfigure(1, minsize=MIN_COLUMN_WIDTH, weight=1)
        frame.columnconfigure(2, minsize=MIN_COLUMN_WIDTH, weight=1)

    def update_scroll_region(self):
        ''' Updates scrolling region.
        '''
        self.frame_with_boxes.update()
        self.canvas['scrollregion'] = self.canvas.bbox(ALL)
