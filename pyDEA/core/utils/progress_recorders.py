''' This module contains classes responsible for updating solution progress.
'''


class NullProgress(object):
    ''' This class does not update solution progress. It is used in
        terminal application.
    '''
    def set_position(self, position):
        ''' Does nothing.
        '''
        pass

    def increment_step(self):
        ''' Does nothing.
        '''
        pass


class GuiProgress(NullProgress):
    ''' This class updates progress bar while a given problem is being
        solved.

        Attributes:
            progress_bar (ProgressBar): progress bar.
            step_size (double): progress bar increment.

        Args:
            progress_bar (ProgressBar): progress bar.
            nb_models (int): total number of DEA models, can take values
                1, 2 or 4.
            nb_sheets (int): number of sheets in solution.
    '''
    def __init__(self, progress_bar, nb_models, nb_sheets):
        self.progress_bar = progress_bar
        self.set_position(0)
        # 99.99 because of precision errors
        # progress bar is reset to 0 if maximum value is exceeded
        self.step_size = 99.99/(nb_models*nb_sheets)

    def set_position(self, position):
        ''' Sets position of the progress bar to a given value.

            Args:
                position (double): progress bar position.
        '''
        self.progress_bar['value'] = position
        self.progress_bar.update()

    def increment_step(self):
        ''' Increments the progress bar by a step size.
        '''
        self.progress_bar.step(self.step_size)
        self.progress_bar.update()
