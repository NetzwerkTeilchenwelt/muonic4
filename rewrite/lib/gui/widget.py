from PyQt5 import QtWidgets, QtGui, QtCore
import datetime
import time
from .util import WrappedFile
from .canvases import ScalarsCanvas
from ..utils.Time import getLocalTime
class BaseWidget(QtWidgets.QWidget):
    """
    Base widget class

    :param logger: logger object
    :type logger: logging.Logger
    :param parent: parent widget
    """
    def __init__(self, logger, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.logger = logger
        self.parent = parent
        self._active = False

    def update(self, *args):
        """
        Update widget contents.

        :param args:
        :returns: None
        """
        QtWidgets.QWidget.update(*args)

    def calculate(self, *args):
        """
        Calculates data related to this widget.

        :param args:
        :returns:
        """
        pass

    def active(self, value=None):
        """
        Getter and setter for active state.

        :param value: value for the new state
        :type value: bool or None
        :returns: bool
        """
        if value is not None:
            self._active = value
        return self._active

    def start(self):
        """
        Perform setup here like resetting variables when the
        widget goes into active state

        :return: None
        """
        pass

    def stop(self):
        """
        Perform actions like saving data when the widget goes
        into inactive state

        :return:
        """
        pass

    def finish(self):
        """
        Gets called upon closing application. Implement cleanup routines like
        closing files here.

        :returns: None
        """
        pass

class RateWidget(BaseWidget):
    """
    Widget for displaying a rate plot

    :param logger: logger object
    :type logger: logging.Logger
    :param filename: filename for the rate data file
    :type filename: str
    :param parent: parent widget
    """
    SCALAR_BUF_SIZE = 5

    def __init__(self, logger, filename, parent=None):
        BaseWidget.__init__(self, logger, parent)

        # measurement start and duration
        self.measurement_duration = datetime.timedelta()
        self.start_time = getLocalTime()

        # define the begin of the time interval for the rate calculation
        self.last_query_time = 0
        self.query_time = time.time()
        self.time_window = 0
        self.show_trigger = True
        self.server = None

        # lists of channel and trigger scalars
        # 0..3: channel 0-3
        # 4:    trigger
        self.previous_scalars = self.new_scalar_buffer()
        self.scalar_buffer = self.new_scalar_buffer()

        # maximum and minimum seen rate across channels and trigger
        self.max_rate = 0
        self.min_rate = 0

        # we will write the column headers of the data into
        # data_file in the first run
        self.first_run = True

        # are we in first cycle after start button is pressed?
        self.first_cycle = False

        # data file options
        self.data_file = WrappedFile(filename)

        # rates store
        self.rates = None

        # initialize plot canvas
        self.scalars_monitor = ScalarsCanvas(self, logger)



        # table column fields
        self.rate_fields = dict()
        self.scalar_fields = dict()



        # info fields
        self.info_fields = dict()


        #call by hand
        #self.setup_layout()

    def new_scalar_buffer(self):
        """
        Return new zeroed list of self.SCALAR_BUF_SIZE

        :returns: list of int
        """
        return [0] * self.SCALAR_BUF_SIZE

    def setup_layout(self, table):
        """
        Sets up all the layout parts of the widget

        :returns: None
        """
        layout = QtWidgets.QGridLayout(self)

        plot_box = QtWidgets.QGroupBox("")
        plot_layout = QtWidgets.QGridLayout(plot_box)
        plot_layout.addWidget(self.scalars_monitor,0,0,1,2)

        #self.table = QtGui.QTableWidget(5, 2, self)
        self.table = table
        self.table.setEnabled(False)
        self.table.setColumnWidth(0, 85)
        self.table.setColumnWidth(1, 60)
        self.table.setHorizontalHeaderLabels(["rate [1/s]", "counts"])
        self.table.setVerticalHeaderLabels(["channel 0", "channel 1",
                                            "channel 2", "channel 3",
                                            "trigger"])
        self.table.horizontalHeader().setStretchLastSection(True)

        # add table widget items for channel and trigger values
        for i in range(self.SCALAR_BUF_SIZE):
            self.rate_fields[i] = QtWidgets.QTableWidgetItem('--')
            self.rate_fields[i].setFlags(QtCore.Qt.ItemIsSelectable |
                                         QtCore.Qt.ItemIsEnabled)
            self.scalar_fields[i] = QtWidgets.QTableWidgetItem('--')
            self.scalar_fields[i].setFlags(QtCore.Qt.ItemIsSelectable |
                                           QtCore.Qt.ItemIsEnabled)
            self.table.setItem(i, 0, self.rate_fields[i])
            self.table.setItem(i, 1, self.scalar_fields[i])

         # add widgets for info fields
        for key in ["start_date", "daq_time", "max_rate"]:
            self.info_fields[key] = QtWidgets.QLineEdit(self)
            self.info_fields[key].setReadOnly(True)
            self.info_fields[key].setDisabled(True)

    def calculate(self):
        """
        Get the rates from the observed counts by dividing by the
        measurement interval.

        """
        scalars = self.server.read_scalars()

        # if this is the first time calculate is called, we want to set all
        # counters to zero. This is the beginning of the first bin.
        if self.first_cycle:
            self.logger.debug("Buffering muon counts for the first bin " +
                              "of the rate plot.")
            self.previous_scalars = scalars
            self.first_cycle = False
            return True

        # initialize temporary buffers for the scalar diffs
        scalar_diffs = self.new_scalar_buffer()

        # calculate differences and store current scalars for reuse
        # in the next cycle
        for i in range(self.SCALAR_BUF_SIZE):
            scalar_diffs[i] = scalars[i] - self.previous_scalars[i]
            self.previous_scalars[i] = scalars[i]

        time_window = self.query_time - self.last_query_time

        # rates for scalars of channels and trigger
        self.rates = [(_scalar / time_window) for _scalar in scalar_diffs]
        # current time window
        self.rates += [time_window]
        # scalars for channels and trigger
        self.rates += [_scalar for _scalar in scalar_diffs]

        self.time_window += time_window

        # add scalar diffs for channels and trigger to buffer
        self.scalar_buffer = [x + scalar_diffs[i]
                              for i, x in enumerate(self.scalar_buffer)]

        # get minimum and maximum rate
        min_rate = min(self.rates[:5])
        max_rate = max(self.rates[:5])

        # update minimum and maximum rate if needed
        if min_rate < self.min_rate:
            self.min_rate = min_rate
        if max_rate > self.max_rate:
            self.max_rate = max_rate

        # write the rates to data file. we have to catch IOErrors, can occur
        # if program is exited
        if self.active():
            try:
                utcdt = datetime.datetime.utcfromtimestamp(self.query_time)
                self.data_file.write(
                    "%s %f %f %f %f %f %f %f %f %f %f %f \n" %
                    (utcdt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                     self.rates[0], self.rates[1], self.rates[2],
                     self.rates[3], self.rates[4],
                     scalar_diffs[0], scalar_diffs[1],
                     scalar_diffs[2], scalar_diffs[3], scalar_diffs[4],
                     self.rates[5]))

                self.logger.debug("Rate plot data was written to %s" %
                                  repr(self.data_file))
            except ValueError:
                self.logger.warning("ValueError, Rate plot data was not " +
                                    "written to %s" % repr(self.data_file))

    def update(self):
        """
        Display newly available data

        :returns: None
        """
        if not self.active():
            return

        #self.query_daq_for_scalars()

        if self.time_window == 0:
            return

        self.update_info_field("daq_time", "%.2f s" % self.time_window)
        self.update_info_field("max_rate", "%.3f 1/s" % self.max_rate)

        for i in range(4):
            self.update_fields(i, get_setting("active_ch%d" % i))
        self.update_fields(4, self.show_trigger)

        channel_config = [get_setting("active_ch%d" % i) for i in range(4)]

        self.scalars_monitor.update_plot(self.rates, self.show_trigger,
                                         channel_config)

    def update_fields(self, channel, enabled, disable_only=False):
        """
        Update table fields for a channel, channel 4 is the trigger channel.

        :param channel: the channel index
        :type channel: int
        :param enabled: enable fields
        :type enabled: bool
        :param disable_only: do not set text if 'enabled' is True
        :type disable_only: bool
        :returns: None
        """
        if channel > self.SCALAR_BUF_SIZE:
            return

        if enabled:
            if not disable_only:
                self.rate_fields[channel].setText(
                    "%.3f" % (self.scalar_buffer[channel] /
                              self.time_window))
                self.scalar_fields[channel].setText(
                    "%d" % (self.scalar_buffer[channel]))
        else:
            self.rate_fields[channel].setText("off")
            self.scalar_fields[channel].setText("off")

    def update_info_field(self, key, text=None, enable=True):
        """
        Set text of info field with 'key' or
        trigger enable state if 'text' is None

        :param key: the key of the info field
        :type key: str
        :param text: the text to set
        :type text: str
        :param enable: enable
        :type enable: bool
        :returns: None
        """
        if text is not None:
            self.info_fields[key].setText(text)
        else:
            self.info_fields[key].setDisabled(not enable)

    def start(self):
        """
        Starts the rate measurement and opens the data file.

        :returns: None
        """
        if self.active():
            return

        self.logger.debug("Start Button Clicked")

        self.active(True)

        self.start_time = getLocalTime()

        # self.start_button.setEnabled(False)
        # self.stop_button.setEnabled(True)
        self.table.setEnabled(True)

        time.sleep(0.2)

        self.first_cycle = True
        self.time_window = 0

        # reset scalar buffer
        self.scalar_buffer = self.new_scalar_buffer()

        # open file for writing and add comment
        self.data_file.open("a")

        # write column headers if this is the first run
        if self.first_run:
            self.data_file.write("year month day hour minutes second milliseconds" +
                                 " | R0 | R1 | R2 | R3 | R trigger | " +
                                 " chan0 | chan1 | chan2 | chan3 | trigger | Delta_time\n")
            self.first_run = False

        # determine type of measurement
        if self.parent.is_widget_active("decay"):
            measurement_type = "rate+decay"
        elif self.parent.is_widget_active("velocity"):
            measurement_type = "rate+velocity"
        else:
            measurement_type = "rate"

        self.data_file.write("# new %s measurement run from: %s\n" %
                             (measurement_type,
                              self.start_time.strftime("%a %d %b %Y %H:%M:%S UTC")))

        # update table fields
        for i in range(4):
            self.update_fields(i, get_setting("active_ch%d" % i),
                               disable_only=True)

        self.update_fields(4, self.show_trigger, disable_only=True)

        # update info fields
        self.update_info_field("start_date", enable=True)
        self.update_info_field("daq_time", enable=True)
        self.update_info_field("max_rate", enable=True)

        self.update_info_field("start_date",
                               self.start_time.strftime("%d.%m.%Y %H:%M:%S"))
        self.update_info_field("daq_time", "%.2f" % self.time_window)
        self.update_info_field("max_rate", "%.2f" % self.max_rate)

        # reset plot
        self.scalars_monitor.reset(show_pending=True)

    def stop(self):
        """
        Stops the rate measurement and closes the data file.

        :returns: None
        """
        if not self.active():
            return

        self.active(False)

        stop_time = getLocalTime()

        self.measurement_duration += stop_time - self.start_time

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.table.setEnabled(False)

        self.update_info_field("start_date", enable=False)
        self.update_info_field("daq_time", enable=False)
        self.update_info_field("max_rate", enable=False)

        self.data_file.write("# stopped run on: %s\n" %
                             stop_time.strftime("%a %d %b %Y %H:%M:%S UTC"))
        self.data_file.close()

    def finish(self):
        """
        Cleanup, close and rename data file

        :returns: None
        """
        if self.active():
            stop_time = getLocalTime()

            self.measurement_duration += stop_time - self.start_time

            self.data_file.write("# stopped run on: %s\n" %
                                 stop_time.strftime("%a %d %b %Y %H:%M:%S UTC"))
            self.data_file.close()

        # only rename if file actually exists
        if os.path.exists(self.data_file.get_filename()):
            try:
                self.logger.info(("The rate measurement was active " +
                                  "for %f hours") %
                                 get_hours_from_duration(
                    self.measurement_duration))
                rename_muonic_file(self.measurement_duration,
                                   self.data_file.get_filename())
            except (OSError, IOError):
                pass
