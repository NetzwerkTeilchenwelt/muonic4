from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtCore import Qt
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import pathlib
import multiprocessing
import subprocess
import logging
import datetime
from time import time
import zmq

from ..analyzers.PulseAnalyzer import PulseAnalyzer

#from src_bak.muonic3.gui.plot_canvases import PulseWidthCanvas
from ..daq.DAQServer import DAQServer
from ..analyzers.RateAnalyzer import RateAnalyzer
from .widget import RateWidget
from .canvases import ScalarsCanvas, MplCanvas, PulseWidthCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

class RateWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    daq_time = 10.0

    def __init__(self, server):
        QObject.__init__(self)
        self._DAQServer = server
        self._RateAnalyser = RateAnalyzer(logger=None, headless=False)
        self._RateAnalyser.server = self._DAQServer
        self._RateAnalyser.progress = self.progress
        self._RateAnalyser.finished = self.finished
    def run(self):
        self._RateAnalyser.measure_rates(timewindow=self.daq_time, meastime=1.0)

class PulseWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(tuple)
    progressBar = pyqtSignal(float)
    daq_time = 0.5

    def __init__(self, server):
        QObject.__init__(self)
        self._DAQServer = server
        self._PulseAnalyzer = PulseAnalyzer(logger=None, headless=False)
        self._PulseAnalyzer.server = self._DAQServer
        self._PulseAnalyzer.progress = self.progress
        self._PulseAnalyzer.finished = self.finished
        self._PulseAnalyzer.progressBar = self.progressBar

    def run(self):
        self._PulseAnalyzer.measure_pulses(meastime=self.daq_time)


class Ui(QtWidgets.QMainWindow):
    serverTask = threading.Thread()
    SCALAR_BUF_SIZE = 5
    def __init__(self):
        super(Ui, self).__init__()
        #print(f"PWD: {pathlib.Path(__file__).parent.resolve()}")
        uic.loadUi(f"{pathlib.Path(__file__).parent.resolve()}/muonic4.ui", self)

        # Get buttons for open studies
        self.btnOpenStudiesRateStart = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesRateStart"
        )

        self.btnOpenStudiesRateStop = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesRateStop"
        )


        self.btnOpenStudiesRateStart.clicked.connect(
            self.btnOpenStudiesRateStartClicked)
        self.btnOpenStudiesRateStop.clicked.connect(
            self.btnOpenStudiesRateStopClicked)

        self.btnOpenStudiesRateStart = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesPulseStart"
        )

        self.btnOpenStudiesRateStop = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesPulseStop"
        )


        self.btnOpenStudiesRateStart.clicked.connect(
            self.btnOpenStudiesPulseStartClicked)
        self.btnOpenStudiesRateStop.clicked.connect(
            self.btnOpenStudiesPulseStopClicked)


        # Get values for open studies
        self.ckOpenStudiesCH0Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH0Enabled"
        )
        self.OpenStudiesCH0Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH0Voltage"
        )
        self.ckOpenStudiesCH1Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH1Enabled"
        )
        self.OpenStudiesCH1Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH1Voltage"
        )
        self.ckOpenStudiesCH2Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH2Enabled"
        )
        self.OpenStudiesCH2Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH2Voltage"
        )
        self.ckOpenStudiesCH3Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH3Enabled"
        )
        self.OpenStudiesCH3Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH3Voltage"
        )


        # Get radio buttons for open studies coincidence
        self.OpenStudiesSingleCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesSingleCoincidence"
        )
        self.OpenStudiesTwoFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesTwoFoldCoincidence"
        )
        self.OpenStudiesThreeFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesThreeFoldCoincidence"
        )
        self.OpenStudiesFourFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesFourFoldCoincidence"
        )

        self.OpenStudiesReadoutInterval = self.findChild(
            QtWidgets.QDoubleSpinBox ,"OpenStudiesReadoutInterval"
        )
        # Get trigger window for open studies
        self.OpenStudiesTriggerWindow = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesTriggerWindow"
        )

        self.lnRateStartedAt = self.findChild(
            QtWidgets.QLineEdit, "lnRateStartedAt"
        )
        self.lnRateTimeDAQ = self.findChild(
            QtWidgets.QLineEdit, "lnRateTimeDAQ"
        )
        self.lnRateMax = self.findChild(
            QtWidgets.QLineEdit, "lnRateMax"
        )

        self.table = self.findChild(
            QtWidgets.QTableWidget, "tblRates"
        )

        self.RateWidget = self.findChild(QtWidgets.QWidget, "rateWidget")

        self.pulseWidget0 = self.findChild(QtWidgets.QWidget, "pulseWidget0")
        self.pulseWidget1 = self.findChild(QtWidgets.QWidget, "pulseWidget1")
        self.pulseWidget2 = self.findChild(QtWidgets.QWidget, "pulseWidget2")
        self.pulseWidget3 = self.findChild(QtWidgets.QWidget, "pulseWidget3")

        self.pulseProgressbar = self.findChild(QtWidgets.QProgressBar, "pPulses")
        self.pulseProgressbar.setVisible(False)

        self.show()

    def shutdownDAQServer(self):
        print("shutdown task")
        self._DAQServer.shutdown()

    def startDAQServer(self):
        self._DAQServer.register_introspection_functions()
        self._DAQServer.register_instance(DAQServer())
        self._DAQServer.serve_forever()

    def getCoincidence(self):
        if self.OpenStudiesSingleCoincidence:
            self.coincidence = "single"
        elif self.OpenStudiesTwoFoldCoincidence:
            self.coincidence = "twofold"
        elif self.OpenStudiesThreeFoldCoincidence:
            self.coincidence = "threefold"
        elif self.OpenStudiesFourFoldCoincidence:
            self.coincidence = "fourfold"

    def setupChannels(self):
        self.ch0enabled = self.ckOpenStudiesCH0Enabled.isChecked()
        self.ch1enabled = self.ckOpenStudiesCH1Enabled.isChecked()
        self.ch2enabled = self.ckOpenStudiesCH2Enabled.isChecked()
        self.ch3enabled = self.ckOpenStudiesCH3Enabled.isChecked()

        self.ch0Threshold = int(self.OpenStudiesCH0Voltage.value())
        self.ch1Threshold = int(self.OpenStudiesCH1Voltage.value())
        self.ch2Threshold = int(self.OpenStudiesCH2Voltage.value())
        self.ch3Threshold = int(self.OpenStudiesCH3Voltage.value())


        print(f"Ch0 config: {self.ch0enabled} -> {self.ch0Threshold}")
        print(f"Ch1 config: {self.ch1enabled} -> {self.ch1Threshold}")
        print(f"Ch2 config: {self.ch2enabled} -> {self.ch2Threshold}")
        print(f"Ch3 config: {self.ch3enabled} -> {self.ch3Threshold}")
        self._DAQServer.setup_channel(self.ch0enabled, self.ch1enabled, self.ch2enabled, self.ch3enabled, self.coincidence)
        self._DAQServer.set_threashold(self.ch0Threshold,self.ch1Threshold, self.ch2Threshold, self.ch3Threshold)

    def btnOpenStudiesRateStartClicked(self):
        #self._DAQServer = DAQServer()
        print("Starting...")
        # sc = MplCanvas(self)
        # sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        self.scalars_monitor = ScalarsCanvas(self.RateWidget, logging.getLogger())

        toolbar = NavigationToolbar(self.scalars_monitor, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.scalars_monitor)
        # widget = QtWidgets.QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)
        self.RateWidget.setLayout(layout)
        self.show()
        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")


        # info fields
        self.start_time = datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S")
        self.daq_time = self.OpenStudiesReadoutInterval.value()
        self.max_rate = 0
        self.updateRateInfo()

        self.setupTable()

        self.getCoincidence()
        self.setupChannels()

        self.thread = QThread()

        self.worker = RateWorker(self._DAQServer)
        self.worker.daq_time = self.daq_time
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgressRate)
        self.thread.start()
        # layout.addWidget(self.scalars_monitor)
        # self.RateWidget.addWidget()

        # self.RateWidget = RateWidget(logging.getLogger(), "foo.txt")
        # self.RateWidget.table = self.findChild(
        #     QtWidgets.QTableWidget, "tblRates"
        # )
        # self.RateWidget.server = self._DAQServer
        # self.RateWidget.calculate()
        # self.RateWidget.update()
        print("... started")

    def setupTable(self):
        self.table.setEnabled(False)
        self.table.setColumnWidth(0, 85)
        self.table.setColumnWidth(1, 60)
        self.table.setHorizontalHeaderLabels(["rate [1/s]", "counts"])
        self.table.setVerticalHeaderLabels(["channel 0", "channel 1",
                                            "channel 2", "channel 3",
                                            "trigger"])
        self.table.horizontalHeader().setStretchLastSection(True)

         # table column fields
        self.rate_fields = dict()
        self.scalar_fields = dict()

        # add table widget items for channel and trigger values
        for i in range(self.SCALAR_BUF_SIZE):
            self.rate_fields[i] = QTableWidgetItem('--')
            self.rate_fields[i].setFlags(Qt.ItemIsSelectable |
                                         Qt.ItemIsEnabled)
            self.scalar_fields[i] = QTableWidgetItem('--')
            self.scalar_fields[i].setFlags(Qt.ItemIsSelectable |
                                           Qt.ItemIsEnabled)
            self.table.setItem(i, 0, self.rate_fields[i])
            self.table.setItem(i, 1, self.scalar_fields[i])
        self.table.setEnabled(True)
    def updateRateInfo(self):
        self.lnRateStartedAt.setText(str(self.start_time))
        self.lnRateTimeDAQ.setText(str(self.daq_time))
        self.lnRateMax.setText(str(self.max_rate))

    def reportProgressRate(self, data):
        print(f"ReportProgressRate: {data}")
        self.scalars_monitor.update_plot(data)
        max_rate = max(data[:5])
        if max_rate > self.max_rate:
            self.max_rate = max_rate
        self.updateRateInfo()
        for i in range(self.SCALAR_BUF_SIZE):
            self.scalar_fields[i].setText("%d"%data[i])
            self.rate_fields[i].setText("%.3f"%(data[i]%data[-1]))


    def btnOpenStudiesRateStopClicked(self):
        pass


    def btnOpenStudiesPulseStartClicked(self):
        print("Starting")
        self.pulses = None
        self.pulseProgressbar.setVisible(True)
        self.pulseProgressbar.setValue(0)
        self.pulse_widths = {i: [] for i in range(4)}
        self.pulse_width_canvases = []
        self.pulse_width_toolbars = []

        self.pulse_width_canvases.append(PulseWidthCanvas(self.pulseWidget0,logging.getLogger(),title="Pulse widths Ch 0"))
        self.pulse_width_canvases.append(PulseWidthCanvas(self.pulseWidget1,logging.getLogger(),title="Pulse widths Ch 1"))
        self.pulse_width_canvases.append(PulseWidthCanvas(self.pulseWidget2,logging.getLogger(),title="Pulse widths Ch 2"))
        self.pulse_width_canvases.append(PulseWidthCanvas(self.pulseWidget3,logging.getLogger(),title="Pulse widths Ch 3"))

        self.pulse_width_toolbars.append(NavigationToolbar(self.pulse_width_canvases[0], self.pulseWidget0))
        self.pulse_width_toolbars.append(NavigationToolbar(self.pulse_width_canvases[1], self.pulseWidget1))
        self.pulse_width_toolbars.append(NavigationToolbar(self.pulse_width_canvases[2], self.pulseWidget2))
        self.pulse_width_toolbars.append(NavigationToolbar(self.pulse_width_canvases[3], self.pulseWidget3))


        layout0 = QtWidgets.QVBoxLayout()
        layout0.addWidget(self.pulse_width_toolbars[0])
        layout0.addWidget(self.pulse_width_canvases[0])
        self.pulseWidget0.setLayout(layout0)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.addWidget(self.pulse_width_toolbars[1])
        layout1.addWidget(self.pulse_width_canvases[1])
        self.pulseWidget1.setLayout(layout1)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(self.pulse_width_toolbars[2])
        layout2.addWidget(self.pulse_width_canvases[2])
        self.pulseWidget2.setLayout(layout2)
        layout3 = QtWidgets.QVBoxLayout()
        layout3.addWidget(self.pulse_width_toolbars[3])
        layout3.addWidget(self.pulse_width_canvases[3])
        self.pulseWidget3.setLayout(layout3)


        self.show()

        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")
        self.getCoincidence()
        self.setupChannels()


        self.lastUpdate = time()
        self.thread = QThread()
        self.worker = PulseWorker(self._DAQServer)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.pulseFinished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgressPulse)
        self.worker.progressBar.connect(self.reportPulseProgressBar)
        self.thread.start()


    def btnOpenStudiesPulseStopClicked(self):
        pass

    def reportProgressPulse(self, data):
        #Pulsedata: (3513.99260384, [], [(13.75, 66.25)], [], [])
        self.pulses = data

        for i, channel in enumerate(self.pulses[1:]):
            pulse_widths = self.pulse_widths.get(i, [])
            for le, fe in channel:
                if fe is not None:
                    pulse_widths.append(fe - le)
                else:
                    pulse_widths.append(0.)
            self.pulse_widths[i] = pulse_widths
        if self.thread.isRunning():
            t = time()
            dt = t - self.lastUpdate
            if dt > 10:
                self.lastUpdate = t
                for i, pwc in enumerate(self.pulse_width_canvases):
                    pwc.update_plot(self.pulse_widths[i])
                self.pulse_widths = {i: [] for i in range(4)}


    def reportPulseProgressBar(self, value):
        print(f"Current Progress: {value}")
        self.pulseProgressbar.setVisible(True)
        self.pulseProgressbar.setValue(value)

    def pulseFinished(self):
        self.pulseProgressbar.setValue(100)
        for i, pwc in enumerate(self.pulse_width_canvases):
                    pwc.update_plot(self.pulse_widths[i])
        self.pulse_widths = {i: [] for i in range(4)}





class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Adapter Class for xmlrpc
    """

    rpc_paths = ("/RPC2",)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
