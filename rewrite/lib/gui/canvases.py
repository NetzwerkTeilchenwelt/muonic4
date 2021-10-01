import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class BasePlotCanvas(FigureCanvas):
    """
    Base class for plot canvases

    :param parent: the parent widget
    :param logger: logger object
    :type logger: logging.Logger
    :param ymin: minimum y-value
    :type ymin: float
    :param ymax: maximum y-value
    :type ymax: float
    :param xmin: minimum x-value
    :type xmin: float
    :param xmax: maximum x-value
    :type xmax: float
    :param xlabel: label of the x-axis
    :type xlabel: str
    :param ylabel: label of the y-axis
    :type ylabel: str
    :param grid: draw grid
    :type grid: bool
    :param spacing: left and right spacing of the subplots
    :type spacing: tuple
    """

    def __init__(self, parent, logger, ymin=0, ymax=10, xmin=0, xmax=10,
                 xlabel="xlabel", ylabel="ylabel", grid=True, title=None,
                 spacing=(0.1, 0.9)):

        self.logger = logger

        # initialization of the canvas
        self.fig = Figure(facecolor="white", figsize=(4,4), dpi=72)
        self.fig.subplots_adjust(left=spacing[0], right=spacing[1])
        FigureCanvas.__init__(self, self.fig)

        # setup subplot, axis and grid
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(ymin=ymin, ymax=ymax)
        self.ax.set_xlim(xmin=xmin, xmax=xmax)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_autoscale_on(False)
        self.ax.grid(grid)

        # store the limits for later use
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.title = None
        # force a redraw of the Figure
        self.fig.canvas.draw()
        self.setParent(parent)

    def update_plot(self, *args):
        """
        Instructions to update the plot. Needs to be implemented in subclasses.

        :Returns: None
        """
        raise NotImplementedError("implement this method")


class ScalarsCanvas(BasePlotCanvas):
    """
    A plot canvas to display scalars

    :param parent: parent widget
    :param logger: logger object
    :type logger: logging.Logger
    :param max_length: maximum number of values to plot
    :type max_length: int
    """
    DEFAULT_CHANNEL_CONFIG = [True, True, True, True]
    CHANNEL_COLORS = ['y', 'm', 'c', 'b']
    TRIGGER_COLOR = 'g'

    def __init__(self, parent, logger, max_length=40):

        BasePlotCanvas.__init__(self, parent, logger, ymin=0, ymax=20,
                                xlabel="Time (s)", ylabel="Rate (1/s)")
        self.show_trigger = True
        self.max_length = max_length
        self.channel_data = [[], [], [], []]
        self.trigger_data = []
        self.time_data = []
        self.time_window = 0
        self.reset()

    def reset(self, show_pending=False):
        """
        Reset all cached plot data

        :param show_pending: indicate pending state
        :type show_pending: bool
        :returns: None
        """
        self.ax.clear()
        self.ax.grid()
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_xlim((self.xmin, self.xmax))
        self.ax.set_ylim((self.ymin, self.ymax))

        self.channel_data = [[], [], [], []]
        self.trigger_data = []
        self.time_data = []
        self.time_window = 0

        for ch in range(4):
            self.ax.plot(self.time_data, self.channel_data[ch],
                         c=self.CHANNEL_COLORS[ch],
                         label=("ch%d" % ch), lw=3)
        if self.show_trigger:
            self.ax.plot(self.time_data, self.trigger_data, c='g',
                         label='trigger', lw=3)

        if not show_pending:
            left, width = .25, .5
            bottom, height = .35, .8
            right = left + width
            top = bottom + height
            self.ax.text(0.5 * (left + right), 0.5 * (bottom + top),
                         'Measuring...', horizontalalignment='center',
                         verticalalignment='center', fontsize=56, color='red',
                         fontweight="heavy", alpha=.8, rotation=30,
                         transform=self.fig.transFigure)

        self.fig.canvas.draw()

    def update_plot(self, data, show_trigger=True,
                    enabled_channels=DEFAULT_CHANNEL_CONFIG):
        """
        Update plot

        :param data: plot data
        :type data: list of lists
        :param show_trigger: show trigger in plot
        :type show_trigger: bool
        :param enabled_channels: enabled channels
        :type enabled_channels: list of bool
        :returne: None
        """
        # do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()
        self.show_trigger = show_trigger

        self.ax.grid()
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        self.logger.debug("result : %s" % data)

        # update lines data using the lists with new data
        self.time_window += data[5]
        self.time_data.append(self.time_window)

        for ch in range(4):
            self.channel_data[ch].append(data[ch])
            if enabled_channels[ch]:
                self.ax.plot(self.time_data, self.channel_data[ch],
                             c=self.CHANNEL_COLORS[ch],
                             label=("ch%d" % ch), lw=2, marker='v')

        self.trigger_data.append(data[4])

        if self.show_trigger:
            self.ax.plot(self.time_data, self.trigger_data,
                         c=self.TRIGGER_COLOR,
                         label='trg', lw=2, marker='x')

        try:
            # get count of active cannels
            channels = enabled_channels + [show_trigger]
            active_count = sum(channels)

            self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                           ncol=active_count, mode="expand", borderaxespad=0.,
                           handlelength=2)
        except Exception as e:
            self.logger.info("An error with the legend occurred: %s" % e)
            self.ax.legend(loc=2)

        if len(self.channel_data[0]) > self.max_length:
            for ch in range(4):
                self.channel_data[ch].remove(self.channel_data[ch][0])
            self.trigger_data.remove(self.trigger_data[0])
            self.time_data.remove(self.time_data[0])

        ma = max(max(self.channel_data[0]), max(self.channel_data[1]),
                 max(self.channel_data[2]), max(self.channel_data[3]),
                 max(self.trigger_data))

        self.ax.set_ylim(0, ma * 1.1)

        # do not set x-range if time_data consists of only one item to
        # avoid matlibplot UserWarning
        if len(self.time_data) > 1:
            self.ax.set_xlim(self.time_data[0], self.time_data[-1])

        self.fig.canvas.draw()
