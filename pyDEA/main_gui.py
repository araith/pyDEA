''' This module should be used for running application GUI.
'''

import os
import traceback
import pkg_resources

from tkinter import Tk, BOTH, W, N, E, S, StringVar, PhotoImage
from tkinter.ttk import Frame, Button, Label, Style, Progressbar
from tkinter.messagebox import askyesno
from tkinter.messagebox import showerror

from pyDEA.core.utils.dea_utils import ObserverStringVar, bg_color, center_window
from pyDEA.core.utils.dea_utils import clean_up_pickled_files, get_logger, PACKAGE
from pyDEA.core.utils.run_routine import RunMethodGUI
from pyDEA.core.gui_modules.data_frame_gui import DataFrame
from pyDEA.core.gui_modules.params_frame_gui import ParamsFrame


class MainFrame(Frame):
    ''' This class implements main GUI of the application.

        Attributes:
            parent (Tk object): parent of this frame (Tk()).
            params_frame (ParamsFrame): frame with parameters.
            data_frame (DataFrame): frame with data and solution.
            progress_bar (Progressbar): progress bar widget.
            increment (int): progress bar increment, it is modified
                in other classes that are responsible for solving
                the problem and update progress.
            weights_status_lbl (Label): label that displays if weight
                restrictions are feasible.
            weights_status_str (StringVar): StringVar object used for
                tracking if weight restrictions are feasible.
            current_categories (list of str): list of current categories.

        Args:
            parent (Tk object): parent of this frame (Tk()).
    '''
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.params_frame = None
        self.data_frame = None
        self.progress_bar = None
        self.increment = 0
        self.weights_status_lbl = None
        self.weights_status_str = StringVar()
        self.weights_status_str.trace('w', self.on_weights_status_change)
        self.current_categories = []
        self.create_widgets()

    def create_widgets(self):
        ''' Creates all widgets that belong to this frame.
        '''
        self.parent.title('pyDEA')
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(0, weight=1, pad=5)
        self.columnconfigure(1, weight=0, pad=5)
        self.rowconfigure(0, pad=3, weight=1)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)
        self.rowconfigure(3, pad=3)

        self.current_categories = []
        data_from_params_file = StringVar()
        str_var_for_input_output_boxes = ObserverStringVar()
        self.params_frame = ParamsFrame(self, self.current_categories,
                                        data_from_params_file,
                                        str_var_for_input_output_boxes,
                                        self.weights_status_str)
        data_frame = DataFrame(self, self.params_frame, self.current_categories,
                               data_from_params_file,
                               str_var_for_input_output_boxes)
        self.data_frame = data_frame
        data_frame.grid(row=0, column=0, sticky=N+S+W+E, padx=15, pady=15)

        self.params_frame.grid(row=0, column=1, sticky=W+E+S+N, padx=15,
                               pady=15, columnspan=2)

        lbl_progress = Label(self, text='Progress')
        lbl_progress.grid(row=1, column=0, sticky=W, padx=10, pady=5)

        self.progress_bar = Progressbar(self, mode='determinate', maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky=W+E, padx=10, pady=5)

        run_btn = Button(self, text='Run', command=self.run)
        run_btn.grid(row=2, column=1, sticky=W, padx=10, pady=10)

        self.weights_status_lbl = Label(self, text='', foreground='red')
        self.weights_status_lbl.grid(row=2, column=2, padx=10, pady=5, sticky=W)

    def on_weights_status_change(self, *args):
        ''' This method is called when weight restrictions status is changed.
        '''
        self.weights_status_lbl.config(text=self.weights_status_str.get())

    def run(self):
        ''' This method is called when the user presses Run button.
            Solves the problem and displays solution.
        '''
        clean_up_pickled_files()
        params = self.params_frame.params
        run_method = RunMethodGUI(self)
        run_method.run(params)

    def construct_categories(self):
        ''' Returns current categories.

            Returns:
                (list of str): list of current categories
        '''
        return [category.strip() for category in self.current_categories
                if category]

    def on_dmu_change(self, *args):
        ''' Updates progress bar.
        '''
        self.progress_bar.step(self.increment)
        self.progress_bar.update()


def ask_quit(main_frame):
    ''' This method is called before application is closed if there is
        an unsaved solution to verify if the user wants to safe solution
        before quitting.

        Args:
            main_frame (MainFrame): main application GUI.
    '''
    if '*' in main_frame.data_frame.tab(1, option='text'):
        if askyesno("Verify", "Do you want to save solution before quitting?"):
            main_frame.data_frame.solution_tab.on_save_solution()
    clean_up_pickled_files()
    main_frame.parent.destroy()


def show_error(*args):
    logger = get_logger()
    err = traceback.format_exception(*args)
    logger.error(err)
    # show only short error message to the user without traceback
    showerror('Error', args[1])


def main():
    ''' Runs main application GUI.
    '''
    logger = get_logger()
    logger.info('pyDEA started as a GUI application.')

    root = Tk()

    root.report_callback_exception = show_error

    # load logo
    if "nt" == os.name:
        iconfile = pkg_resources.resource_filename(PACKAGE, 'pyDEAlogo.ico')
        root.wm_iconbitmap(bitmap=iconfile)
    else:
        iconfile = pkg_resources.resource_filename(PACKAGE, 'pyDEAlogo.gif')
        img = PhotoImage(file=iconfile)
        root.tk.call('wm', 'iconphoto', root._w, img)

    # change background color of all widgets
    s = Style()
    s.configure('.', background=bg_color)

    # run the application
    app = MainFrame(root)
    root.protocol("WM_DELETE_WINDOW", (lambda: ask_quit(app)))

    center_window(root,
                  root.winfo_screenwidth() - root.winfo_screenwidth()*0.15,
                  root.winfo_screenheight() - root.winfo_screenheight()*0.15)

    root.mainloop()
    logger.info('pyDEA exited.')


if __name__ == '__main__':
    main()
