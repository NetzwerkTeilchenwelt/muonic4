from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import pathlib
import multiprocessing
import subprocess
import logging
import datetime
import jsonpickle
import numpy as np
from time import time, sleep
import zmq
from ..analyzers.VelocityTrigger import VelocityTrigger
from ..analyzers.DecayTrigger import DecayTriggerThorough
from ..analyzers.PulseAnalyzer import PulseAnalyzer
from ..analyzers.fit import gaussian_fit

# from src_bak.muonic3.gui.plot_canvases import PulseWidthCanvas
from ..daq.DAQServer import DAQServer
from ..analyzers.RateAnalyzer import RateAnalyzer
from .widget import RateWidget
from .util import WrappedFile
from ..utils.Time import getLocalTime, getCurrentTimeString
from .canvases import ScalarsCanvas, MplCanvas, PulseWidthCanvas, LifetimeCanvas
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)


class RateWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)
    progressbar = pyqtSignal(float)
    daq_time = 1.0
    readout_time = 10.0

    def __init__(self, server):
        QObject.__init__(self)
        self._DAQServer = server
        self._RateAnalyser = RateAnalyzer(logger=None, headless=False)
        self._RateAnalyser.server = self._DAQServer
        self._RateAnalyser.progress = self.progress
        self._RateAnalyser.progressbar = self.progressbar
        self._RateAnalyser.finished = self.finished

    def run(self):
        self._RateAnalyser.measure_rates(timewindow=self.readout_time, meastime=self.daq_time)


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


    def run(self):
        self._PulseAnalyzer.measure_pulses(meastime=self.daq_time)

class VelocityWorker(QObject):
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


class LifetimeWorker(QObject):
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

class DAQOutputWorker(QObject):
    i = 0
    progress = pyqtSignal(str)
    def __init__(self, server, output):
        QObject.__init__(self)
        self._DAQServer = server
        self.output = output
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")

    def run(self):
        while True:
            msg = self.sock.recv_string()
            obj = jsonpickle.decode(msg)
            #print(f"OBJ Type: {type(obj)}")
            text = str(obj)
            if text != "":
                self.progress.emit(text + '\n')

class DAQOutputWriter(QObject):
    def __init__(self, server):
        QObject.__init__(self)
        self._DAQServer = server
        self.ctx  = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")
        self.file = open(f"{getCurrentTimeString()}_RAW.txt", "w")

    def run(self):
        while True:
            msg = self.sock.recv_string()
            obj = jsonpickle.decode(msg)
            #print(f"OBJ Type: {type(obj)}")
            text = str(obj)
            if text != "":
                self.file.write(text + '\n')
                self.file.flush()

class Ui(QtWidgets.QMainWindow):
    serverTask = threading.Thread()
    SCALAR_BUF_SIZE = 5

    def __init__(self):
        super(Ui, self).__init__()
        logging.getLogger('matplotlib.font_manager').disabled = True
        # print(f"PWD: {pathlib.Path(__file__).parent.resolve()}")
        uic.loadUi(f"{pathlib.Path(__file__).parent.resolve()}/muonic4.ui", self)

        self.MainTab = self.findChild(QtWidgets.QTabWidget, "MainTab")
        self.MainTab.setTabEnabled(3, False)


        # Get buttons for open studies
        self.btnOpenStudiesRateStart = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesRateStart"
        )

        self.btnOpenStudiesRateStop = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesRateStop"
        )

        self.btnOpenStudiesRateStart.clicked.connect(
            self.btnOpenStudiesRateStartClicked
        )
        self.btnOpenStudiesRateStop.clicked.connect(self.btnOpenStudiesRateStopClicked)

        self.btnOpenStudiesRateStart = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesPulseStart"
        )

        self.btnOpenStudiesRateStop = self.findChild(
            QtWidgets.QPushButton, "btnOpenStudiesPulseStop"
        )

        # self.btnOpenStudiesRateStart.clicked.connect(
        #     self.btnOpenStudiesPulseStartClicked
        # )
        # self.btnOpenStudiesRateStop.clicked.connect(self.btnOpenStudiesPulseStopClicked)

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
            QtWidgets.QDoubleSpinBox, "OpenStudiesReadoutInterval"
        )

        self.OpenStudiesMeasurementTime = self.findChild(
            QtWidgets.QDoubleSpinBox, "OpenStudiesMeasurementTime"
        )
        # Get trigger window for open studies
        self.OpenStudiesTriggerWindow = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesTriggerWindow"
        )

        self.pRates = self.findChild(
            QtWidgets.QProgressBar, "pRates"
        )
        self.pRates.setVisible(False)

        self.lnRateStartedAt = self.findChild(QtWidgets.QLineEdit, "lnRateStartedAt")
        self.lnRateTimeDAQ = self.findChild(QtWidgets.QLineEdit, "lnRateTimeDAQ")
        self.lnRateMax = self.findChild(QtWidgets.QLineEdit, "lnRateMax")

        self.table = self.findChild(QtWidgets.QTableWidget, "tblRates")

        self.RateWidget = self.findChild(QtWidgets.QWidget, "rateWidget")

        self.pulseWidget0 = self.findChild(QtWidgets.QWidget, "pulseWidget0")
        self.pulseWidget1 = self.findChild(QtWidgets.QWidget, "pulseWidget1")
        self.pulseWidget2 = self.findChild(QtWidgets.QWidget, "pulseWidget2")
        self.pulseWidget3 = self.findChild(QtWidgets.QWidget, "pulseWidget3")

        # self.pulseProgressbar = self.findChild(QtWidgets.QProgressBar, "pPulses")
        # self.pulseProgressbar.setVisible(False)


        # Get values for velocity
        self.ckVelocityCH0Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckVelocityCH0Enabled"
        )
        self.VelocityCH0Voltage = self.findChild(
            QtWidgets.QSpinBox, "VelocityCH0Voltage"
        )
        self.ckVelocityCH1Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckVelocityCH1Enabled"
        )
        self.VelocityCH1Voltage = self.findChild(
            QtWidgets.QSpinBox, "VelocityCH1Voltage"
        )
        self.ckVelocityCH2Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckVelocityCH2Enabled"
        )
        self.VelocityCH2Voltage = self.findChild(
            QtWidgets.QSpinBox, "VelocityCH2Voltage"
        )
        self.ckVelocityCH3Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckVelocityCH3Enabled"
        )
        self.VelocityCH3Voltage = self.findChild(
            QtWidgets.QSpinBox, "VelocityCH3Voltage"
        )

        self.VelocityUpperChannel0 = self.findChild(
            QtWidgets.QRadioButton, "VelocityUpperChannel0"
        )
        self.VelocityUpperChannel1 = self.findChild(
            QtWidgets.QRadioButton, "VelocityUpperChannel1"
        )
        self.VelocityUpperChannel2 = self.findChild(
            QtWidgets.QRadioButton, "VelocityUpperChannel2"
        )
        self.VelocityUpperChannel3 = self.findChild(
            QtWidgets.QRadioButton, "VelocityUpperChannel3"
        )
        self.VelocityLowerChannel0 = self.findChild(
            QtWidgets.QRadioButton, "VelocityLowerChannel0"
        )
        self.VelocityLowerChannel1 = self.findChild(
            QtWidgets.QRadioButton, "VelocityLowerChannel1"
        )
        self.VelocityLowerChannel2 = self.findChild(
            QtWidgets.QRadioButton, "VelocityLowerChannel2"
        )
        self.VelocityLowerChannel3 = self.findChild(
            QtWidgets.QRadioButton, "VelocityLowerChannel3"
        )

        self.btVelocityStart = self.findChild(
            QtWidgets.QPushButton, "btVelocityStart"
        )
        self.btVelocityStart.clicked.connect(
            self.btnVelocityStartClicked
        )
        self.btVelocityStop = self.findChild(
            QtWidgets.QPushButton, "btVelocityStop"
        )
        self.btVelocityStop.clicked.connect(
            self.btnVelocityStopClicked
        )

        self.btnVelocityFit = self.findChild(
            QtWidgets.QPushButton, "btnVelocityFit"
        )
        self.btnVelocityFit.clicked.connect(
            self.btnVelocityFitClicked
        )

        self.velocityWidget = self.findChild(
            QtWidgets.QWidget, "velocityWidget"
        )

        self.VelocityFitMin = self.findChild(
            QtWidgets.QSpinBox, "velocityFitMin"
        )

        self.VelocityFitMax = self.findChild(
            QtWidgets.QSpinBox, "velocityFitMax"
        )

        self.velocityFitParameters = self.findChild(
            QtWidgets.QPlainTextEdit, "velocityFitParameters"
        )

        self.VelocityMounCount = self.findChild(
            QtWidgets.QLineEdit, "VelocityMounCount"
        )

        self.VelocityLastMuon = self.findChild(
            QtWidgets.QLineEdit, "VelocityLastMuon"
        )

        self.VelocityProgress = self.findChild(
            QtWidgets.QProgressBar, "VelocityProgress"
        )
        self.VelocityProgress.setVisible(False)

        self.velocityMeasTime = self.findChild(
            QtWidgets.QDoubleSpinBox, "velocityMeasTime"
        )

        # Get values for lifetime
        self.ckLifetimeCH0Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckLifetimeCH0Enabled"
        )
        self.LifetimeCH0Voltage = self.findChild(
            QtWidgets.QSpinBox, "LifetimeCH0Voltage"
        )
        self.ckLifetimeCH1Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckLifetimeCH1Enabled"
        )
        self.LifetimeCH1Voltage = self.findChild(
            QtWidgets.QSpinBox, "LifetimeCH1Voltage"
        )
        self.ckLifetimeCH2Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckLifetimeCH2Enabled"
        )
        self.LifetimeCH2Voltage = self.findChild(
            QtWidgets.QSpinBox, "LifetimeCH2Voltage"
        )
        self.ckLifetimeCH3Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckLifetimeCH3Enabled"
        )
        self.LifetimeCH3Voltage = self.findChild(
            QtWidgets.QSpinBox, "LifetimeCH3Voltage"
        )


        self.btLifetimeStart = self.findChild(
            QtWidgets.QPushButton, "btnLifetimeStart"
        )
        self.btLifetimeStart.clicked.connect(
            self.btnLifetimeStartClicked
        )
        self.btLifetimeStop = self.findChild(
            QtWidgets.QPushButton, "btnLifetimeStop"
        )
        self.btLifetimeStop.clicked.connect(
            self.btnLifetimeStopClicked
        )

        self.btnLifetimeFit = self.findChild(
            QtWidgets.QPushButton, "btnLifetimeFit"
        )
        self.btnLifetimeFit.clicked.connect(
            self.btnLifetimeFitClicked
        )

        self.lifetimeWidget = self.findChild(
            QtWidgets.QWidget, "LifetimeWidget"
        )

        self.LifetimeMeasurementTime = self.findChild(
            QtWidgets.QDoubleSpinBox, "LifetimeMeasurementTime"
        )

        self.LifetimeMinSpace = self.findChild(
            QtWidgets.QSpinBox, "LifetimeMinSpace"
        )

        self.LifetimeMinWidth = self.findChild(
            QtWidgets.QSpinBox, "LifetimeMinWidth"
        )

        self.LifetimeMaxWidth = self.findChild(
            QtWidgets.QSpinBox, "LifetimeMaxWidth"
        )

        self.LifeteimeMinWidtheminus = self.findChild(
            QtWidgets.QSpinBox, "LifeteimeMinWidtheminus"
        )

        self.LifetimeMaxWidtheminus = self.findChild(
            QtWidgets.QSpinBox, "LifetimeMaxWidtheminus"
        )

        self.LifetimeMounCount = self.findChild(
            QtWidgets.QLineEdit, "LifetimeMounCount"
        )

        self.LifetimeLastMuon = self.findChild(
            QtWidgets.QLineEdit, "LifetimeLastMuon"
        )

        self.LifetimeFitMin = self.findChild(
            QtWidgets.QSpinBox, "LifetimeFitMin"
        )

        self.LifetimeFitMax = self.findChild(
            QtWidgets.QSpinBox, "LifetimeFitMax"
        )

        self.LifetimeFitParameters = self.findChild(
            QtWidgets.QPlainTextEdit, "LifetimeFitParameters"
        )

        self.lifetimeProgress = self.findChild(
            QtWidgets.QProgressBar, "lifetimeProgress"
        )

        self.lifetimeProgress.setVisible(False)

        self.DAQOutput = self.findChild(
            QtWidgets.QPlainTextEdit, "DAQOutput"
        )

        self.writeDAQOutput = self.findChild(QtWidgets.QCheckBox, "chkRawOutput")

        self.DAQCommand = self.findChild(
            QtWidgets.QLineEdit, "DAQCommand"
        )

        self.btnSendDAQCommand = self.findChild(
            QtWidgets.QPushButton, "btnSendDAQCommand"
        )
        self.btnSendDAQCommand.clicked.connect(
            self.btnSendDAQCommandClicked
        )

        self.GPSText = self.findChild(
            QtWidgets.QPlainTextEdit, "GPSText"
        )

        self.btnShowGPS = self.findChild(
            QtWidgets.QPushButton, "btnShowGPS"
        )
        self.btnShowGPS.clicked.connect(
            self.btnShowGPSClicked
        )

        self.GPSDateTime = self.findChild(QtWidgets.QLineEdit, "GPSDateTime")
        self.Status = self.findChild(QtWidgets.QLineEdit, "GPSStatus")
        self.PosFix = self.findChild(QtWidgets.QLineEdit, "GPSPosFix")
        self.Latitude = self.findChild(QtWidgets.QLineEdit, "GPSLatitude")
        self.Longitude = self.findChild(QtWidgets.QLineEdit, "GPSLongitude")
        self.Altitude = self.findChild(QtWidgets.QLineEdit, "GPSAltitude")
        self.NSats = self.findChild(QtWidgets.QLineEdit, "GPSNSats")
        self.PPSDelay = self.findChild(QtWidgets.QLineEdit, "GPSPPSDelay")
        self.FPGATime = self.findChild(QtWidgets.QLineEdit, "GPSFPGATime")
        self.ChkSumErr = self.findChild(QtWidgets.QLineEdit, "GPSChkSumErr")

        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")

        self.DAQThread = QThread()
        self.DAQWorker = DAQOutputWorker(self._DAQServer, self.DAQOutput)
        self.DAQWorker.moveToThread(self.DAQThread)

        self.DAQThread.started.connect(self.DAQWorker.run)
        self.DAQWorker.progress.connect(self.updateDAQ)
        # self.DAQWorker.finished.connect(self.DAQThread.quit)
        # self.DAQWorker.finished.connect(self.DAQWorker.deleteLater)
        # self.DAQThread.finished.connect(self.DAQThread.deleteLater)

        self.DAQThread.start()

        #get Git Rev


        self.show()

    def startOutputWrite(self):
        if not self.writeDAQOutput.isChecked():
           return

        if hasattr(self,"DAQWriteThread"):
            return
        self.DAQWriteThread = QThread()
        self.DAQOutputWriter = DAQOutputWriter(self._DAQServer)
        self.DAQOutputWriter.moveToThread(self.DAQWriteThread)
        self.DAQWriteThread.started.connect(self.DAQOutputWriter.run)
        self.DAQWriteThread.start()


    def shutdownDAQServer(self):
        print("shutdown task")
        self._DAQServer.shutdown()

    def startDAQServer(self):
        self._DAQServer.register_introspection_functions()
        self._DAQServer.register_instance(DAQServer())
        self._DAQServer.serve_forever()

    def getCoincidence(self):
        if self.OpenStudiesSingleCoincidence.isChecked():
            self.coincidence = "single"
        elif self.OpenStudiesTwoFoldCoincidence.isChecked():
            self.coincidence = "twofold"
        elif self.OpenStudiesThreeFoldCoincidence.isChecked():
            self.coincidence = "threefold"
        elif self.OpenStudiesFourFoldCoincidence.isChecked():
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
        self._DAQServer.setup_channel(
            self.ch0enabled,
            self.ch1enabled,
            self.ch2enabled,
            self.ch3enabled,
            self.coincidence,
        )
        self._DAQServer.set_threashold(
            self.ch0Threshold, self.ch1Threshold, self.ch2Threshold, self.ch3Threshold
        )

    def btnOpenStudiesRateStartClicked(self):
        # self._DAQServer = DAQServer()
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
        self.startOutputWrite()
        # info fields
        self.start_time = getLocalTime()
        self.daq_time = self.OpenStudiesMeasurementTime.value()
        self.readout_time = self.OpenStudiesReadoutInterval.value()
        if self.daq_time == 0:
            self.show_progress = False
            self.daq_time = float(2**32)
        else:
            self.show_progress = True
        self.max_rate = 0
        self.updateRateInfo()

        self.setupTable()

        self.getCoincidence()
        self.setupChannels()
        self._DAQServer.do("DC")
        self._DAQServer.do("CE")
        self._DAQServer.do("WC 03 04")
        self._DAQServer.do("WC 02 0A")

        self.threadRate = QThread()

        self.workerRate = RateWorker(self._DAQServer)
        self.workerRate.daq_time = self.daq_time
        self.workerRate.readout_time = self.readout_time
        self.workerRate.moveToThread(self.threadRate)

        self.threadRate.started.connect(self.workerRate.run)
        self.workerRate.finished.connect(self.threadRate.quit)
        self.workerRate.finished.connect(self.workerRate.deleteLater)
        self.workerRate.finished.connect(self.rateFinished)
        self.threadRate.finished.connect(self.threadRate.deleteLater)

        self.workerRate.progress.connect(self.reportProgressRate)
        self.workerRate.progressbar.connect(self.reportProgressBarRate)
        if self.show_progress:
            self.pRates.setVisible(True)
        self.threadRate.start()
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
        self.startPulesMeasurement()
        sleep(3)

    def reportProgressBarRate(self, p):
        self.pRates.setValue(float(p))

    def rateFinished(self):
        self.pRates.setValue(100.0)

    def setupTable(self):
        self.table.setEnabled(False)
        self.table.setColumnWidth(0, 320/3)
        self.table.setColumnWidth(1, 320/3)
        self.table.setColumnWidth(2, 320/3)
        #self.table.setColumnWidth(1, 60)
        self.table.setHorizontalHeaderLabels(["Rate [1/s]", "Counts"])
        self.table.setVerticalHeaderLabels(
            ["Channel 0", "Channel 1", "Channel 2", "Channel 3", "Trigger"]
        )
        #self.table.horizontalHeader().setStretchLastSection(True)
        #self.table.horizontalHeader().setSectionResizeMode( 0, QtWidgets.QHeaderView.ResizeToContents)
       # self.table.horizontalHeader().setSectionResizeMode( 1, QtWidgets.QHeaderView.ResizeToContents)
       # self.table.horizontalHeader().setSectionResizeMode( 2, QtWidgets.QHeaderView.ResizeToContents)

        # table column fields
        self.rate_fields = dict()
        self.scalar_fields = dict()

        # add table widget items for channel and trigger values
        for i in range(self.SCALAR_BUF_SIZE):
            self.rate_fields[i] = QTableWidgetItem("--")
            self.rate_fields[i].setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.scalar_fields[i] = QTableWidgetItem("--")
            self.scalar_fields[i].setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(i, 0, self.rate_fields[i])
            self.table.setItem(i, 1, self.scalar_fields[i])
        self.table.setEnabled(True)

    def updateRateInfo(self):
        self.lnRateStartedAt.setText(str(self.start_time.strftime("%d.%m.%Y %H:%M:%S")))
        deltaT = getLocalTime() - self.start_time
        self.lnRateTimeDAQ.setText(str(deltaT.total_seconds()))
        self.lnRateMax.setText(str(self.max_rate))

    def reportProgressRate(self, data):
        print(f"ReportProgressRate: {data}")
        self.scalars_monitor.update_plot(data)
        max_rate = max(data[:5])
        if max_rate > self.max_rate:
            self.max_rate = max_rate
        self.updateRateInfo()
        for i in range(self.SCALAR_BUF_SIZE):
            try:
                current_val = int(self.scalar_fields[i].text())
            except:
                current_val = 0
            self.scalar_fields[i].setText("%d" % int(current_val + data[i]))
            self.rate_fields[i].setText("%.3f" % (data[i] % data[-1]))

    def btnOpenStudiesRateStopClicked(self):
        self.thread.quit()


    def startPulesMeasurement(self):
        print("Starting Pulses")
        self.pulses = None
        # self.pulseProgressbar.setVisible(True)
        # self.pulseProgressbar.setValue(0)
        self.pulse_widths = {i: [] for i in range(4)}
        self.pulse_width_canvases = []
        self.pulse_width_toolbars = []

        self.pulse_width_canvases.append(
            PulseWidthCanvas(
                self.pulseWidget0, logging.getLogger(), title="Pulse widths Ch 0"
            )
        )
        self.pulse_width_canvases.append(
            PulseWidthCanvas(
                self.pulseWidget1, logging.getLogger(), title="Pulse widths Ch 1"
            )
        )
        self.pulse_width_canvases.append(
            PulseWidthCanvas(
                self.pulseWidget2, logging.getLogger(), title="Pulse widths Ch 2"
            )
        )
        self.pulse_width_canvases.append(
            PulseWidthCanvas(
                self.pulseWidget3, logging.getLogger(), title="Pulse widths Ch 3"
            )
        )

        self.pulse_width_toolbars.append(
            NavigationToolbar(self.pulse_width_canvases[0], self.pulseWidget0)
        )
        self.pulse_width_toolbars.append(
            NavigationToolbar(self.pulse_width_canvases[1], self.pulseWidget1)
        )
        self.pulse_width_toolbars.append(
            NavigationToolbar(self.pulse_width_canvases[2], self.pulseWidget2)
        )
        self.pulse_width_toolbars.append(
            NavigationToolbar(self.pulse_width_canvases[3], self.pulseWidget3)
        )

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

        # try:
        #     self._DAQServer = DAQServer()
        # except zmq.error.ZMQError:
        #     print("reusing old server")
        self.startOutputWrite()
        # self.getCoincidence()
        # self.setupChannels()

        self.lastUpdatePulse = time()
        self.threadPulse = QThread()
        self.workerPulse = PulseWorker(self._DAQServer)
        self.daq_timePulse = self.OpenStudiesMeasurementTime.value()
        self.workerPulse.daq_time = self.daq_timePulse
        self.workerPulse.moveToThread(self.threadPulse)

        self.threadPulse.started.connect(self.workerPulse.run)
        self.workerPulse.finished.connect(self.threadPulse.quit)
        self.workerPulse.finished.connect(self.workerPulse.deleteLater)
        self.workerPulse.finished.connect(self.pulseFinished)
        self.threadPulse.finished.connect(self.threadPulse.deleteLater)
        self.workerPulse.progress.connect(self.reportProgressPulse)
        # self.workerPulse.progressBar.connect(self.reportPulseProgressBar)
        self.threadPulse.start()
        print("Pulse thread started")

    def btnOpenStudiesPulseStartClicked(self):
        pass

    def btnOpenStudiesPulseStopClicked(self):
        self.thread.quit()


    def reportProgressPulse(self, data):
        # Pulsedata: (3513.99260384, [], [(13.75, 66.25)], [], [])
        print(f"ReportProgressPulse: {data}")
        self.pulses = data

        for i, channel in enumerate(self.pulses[1:]):
            # print(f"Channel {i}: {channel}")
            pulse_widths = self.pulse_widths.get(i, [])
            # print(f"Pulse widths: {pulse_widths}")
            for le, fe in channel:
                if fe is not None:
                    pulse_widths.append(fe - le)
                else:
                    pulse_widths.append(0.0)
            self.pulse_widths[i] = pulse_widths
        if self.threadPulse.isRunning():
            t = time()
            dt = t - self.lastUpdatePulse
            if dt > 10:
                self.lastUpdatePulse = t
                for i, pwc in enumerate(self.pulse_width_canvases):
                    pwc.update_plot(self.pulse_widths[i])
                self.pulse_widths = {i: [] for i in range(4)}

    def reportPulseProgressBar(self, value):
        print(f"Current Progress: {value}")
        # self.pulseProgressbar.setVisible(True)
        # self.pulseProgressbar.setValue(value)

    def pulseFinished(self):
        # self.pulseProgressbar.setValue(100)
        for i, pwc in enumerate(self.pulse_width_canvases):
            pwc.update_plot(self.pulse_widths[i])
        self.pulse_widths = {i: [] for i in range(4)}

    def setupVelocityChannels(self):
        self.ch0enabled = self.ckVelocityCH0Enabled.isChecked()
        self.ch1enabled = self.ckVelocityCH1Enabled.isChecked()
        self.ch2enabled = self.ckVelocityCH2Enabled.isChecked()
        self.ch3enabled = self.ckVelocityCH3Enabled.isChecked()

        self.ch0Threshold = int(self.VelocityCH0Voltage.value())
        self.ch1Threshold = int(self.VelocityCH1Voltage.value())
        self.ch2Threshold = int(self.VelocityCH2Voltage.value())
        self.ch3Threshold = int(self.VelocityCH3Voltage.value())

        print(f"Ch0 config: {self.ch0enabled} -> {self.ch0Threshold}")
        print(f"Ch1 config: {self.ch1enabled} -> {self.ch1Threshold}")
        print(f"Ch2 config: {self.ch2enabled} -> {self.ch2Threshold}")
        print(f"Ch3 config: {self.ch3enabled} -> {self.ch3Threshold}")
        self._DAQServer.setup_channel(
            self.ch0enabled,
            self.ch1enabled,
            self.ch2enabled,
            self.ch3enabled,
            "twofold",
        )
        self._DAQServer.set_threashold(
            self.ch0Threshold, self.ch1Threshold, self.ch2Threshold, self.ch3Threshold
        )

    def getUpperLower(self):
        self.upper_channel = 0
        if self.VelocityUpperChannel0.isChecked():
            self.upper_channel = 0
        elif self.VelocityUpperChannel1.isChecked():
            self.upper_channel = 1
        elif self.VelocityUpperChannel2.isChecked():
            self.upper_channel = 2
        elif self.VelocityUpperChannel3.isChecked():
            self.upper_channel = 3

        self.lower_channel = 1
        if self.VelocityLowerChannel0.isChecked():
            self.lower_channel = 0
        elif self.VelocityLowerChannel1.isChecked():
            self.lower_channel = 1
        elif self.VelocityLowerChannel2.isChecked():
            self.lower_channel = 2
        elif self.VelocityLowerChannel3.isChecked():
            self.lower_channel = 3

        print(f"got upper: {self.upper_channel} lower: {self.lower_channel}")

    def btnVelocityStartClicked(self):
        print("start clicked")
        self.VelocityProgress.setVisible(True)
        self.binning = (0., 30, 25)
        # default fit range
        self.fit_range = (self.binning[0], self.binning[1])

        self.event_data = []
        self.last_event_time = None
        self.active_since = None

        self.getUpperLower()
        # measurement duration and start time
        self.measurement_duration = datetime.timedelta()
        self.start_time = getLocalTime()
        self.mu_file = WrappedFile(f"{self.start_time}_V.txt")

        self.velocity_canvas = LifetimeCanvas(self.velocityWidget , logging.getLogger(), binning = self.binning)
        toolbar = NavigationToolbar(self.velocity_canvas, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.velocity_canvas)
        self.velocityWidget.setLayout(layout)
        self.show()

        self.trigger = VelocityTrigger(logging.getLogger())
        self.start_time = getLocalTime()
        self.mu_file.open("a")
        self.mu_file.write("# new velocity measurement run from: %s\n" %
                               self.start_time.strftime("%a %d %b %Y %H:%M:%S UTC"))
        self.muon_counter = 0

        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")

        self.startOutputWrite()
        self.setupVelocityChannels()

        self.thread = QThread()
        self.worker = VelocityWorker(self._DAQServer)
        self.worker.daq_time = float(self.velocityMeasTime.value())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.velocityFinished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgressVelocity)
        self.worker.progressBar.connect(self.reportProgressBarVelocity)
        self.thread.start()
        self.startPulesMeasurement()

    def btnVelocityStopClicked(self):
        self.thread.quit()

    def calculateVelocity(self, pulses):
        if pulses is None:
            return

        flight_time = self.trigger.trigger(pulses,
                                           upper_channel=self.upper_channel+1,
                                           lower_channel=self.lower_channel+1, debug=False)

        if flight_time is not None and flight_time > 0:
            self.event_data.append(flight_time)
            self.muon_counter += 1
            self.last_event_time = getLocalTime()
            logging.getLogger().info("measured flight time %s" % flight_time)

    def reportProgressVelocity(self, data):

        self.calculateVelocity(data)
        if not self.event_data:
            print("Eventdata empty")
            return

        self.VelocityMounCount.setText(f"{self.muon_counter}")
        self.VelocityLastMuon.setText(f'{self.last_event_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')
        self.velocity_canvas.update_plot(self.event_data)
        for flight_time in self.event_data:
            self.mu_file.write("%s Flight time %s\n" % (
                self.last_event_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                repr(flight_time)))

        self.event_data = []

    def reportProgressBarVelocity(self, progress):
        self.VelocityProgress.setVisible(True)
        self.VelocityProgress.setValue(progress)

    def velocityFinished(self):
        stop_time = getLocalTime()
        self.measurement_duration += stop_time - self.start_time
        self.VelocityProgress.setValue(100)
        logging.getLogger().info("Muon velocity mode now deactivated, returning to " +
                         "previous setting (if available)")

        self.mu_file.write("# stopped run on: %s\n" %
                           stop_time.strftime("%a %d %b %Y %H:%M:%S UTC"))
        self.mu_file.close()

    def btnVelocityFitClicked(self):
        self.fit_range = (float(self.VelocityFitMin.value()), float(self.VelocityFitMax.value()))
        logging.getLogger().debug("Using fit range of %s" % repr(self.fit_range))
        fit_results = gaussian_fit(
            bincontent=np.asarray(self.velocity_canvas.heights),
            binning=self.binning, fitrange=self.fit_range)

        print(f"fitresult: {fit_results}")
        if fit_results is not None:
            params = self.velocity_canvas.show_fit(*fit_results)
            self.velocityFitParameters.setPlainText(f"""
            A:{round(params[0][0],2)} +- {round(params[1][0],2)}
            sigma:{round(params[0][1],2)} +- {round(params[1][1],2)}
            mu:{round(params[0][2],2)} +- {round(params[1][2],2)}
             """)


    def setupLifetimeChannels(self):
        self.ch0enabled = self.ckLifetimeCH0Enabled.isChecked()
        self.ch1enabled = self.ckLifetimeCH1Enabled.isChecked()
        self.ch2enabled = self.ckLifetimeCH2Enabled.isChecked()
        self.ch3enabled = self.ckLifetimeCH3Enabled.isChecked()

        self.ch0Threshold = int(self.LifetimeCH0Voltage.value())
        self.ch1Threshold = int(self.LifetimeCH1Voltage.value())
        self.ch2Threshold = int(self.LifetimeCH2Voltage.value())
        self.ch3Threshold = int(self.LifetimeCH3Voltage.value())

        print(f"Ch0 config: {self.ch0enabled} -> {self.ch0Threshold}")
        print(f"Ch1 config: {self.ch1enabled} -> {self.ch1Threshold}")
        print(f"Ch2 config: {self.ch2enabled} -> {self.ch2Threshold}")
        print(f"Ch3 config: {self.ch3enabled} -> {self.ch3Threshold}")
        self._DAQServer.setup_channel(
            self.ch0enabled,
            self.ch1enabled,
            self.ch2enabled,
            self.ch3enabled,
            "twofold",
        )
        self._DAQServer.set_threashold(
            self.ch0Threshold, self.ch1Threshold, self.ch2Threshold, self.ch3Threshold
        )

    def btnLifetimeStartClicked(self):
        print("start clicked")
        self.min_single_pulse_width = 0
        self.max_single_pulse_width = 100000  # inf
        self.min_double_pulse_width = 0
        self.max_double_pulse_width = 100000  # inf
        self.muon_counter = 0
        self.single_pulse_channel = 0
        self.double_pulse_channel = 1
        self.veto_pulse_channel = 2
        self.decay_min_time = 0

        # ignore first bin because of after pulses,
        # see https://github.com/achim1/muonic/issues/39
        self.binning = (0, 10, 21)

        # default fit range
        self.fit_range = (1.5, 10.)

        self.event_data = []
        self.last_event_time = None
        self.active_since = None

         # measurement duration and start time
        self.measurement_duration = datetime.timedelta()
        self.start_time = getLocalTime()

        self.mu_file = WrappedFile(f"{getCurrentTimeString()}_D.txt")


        self.previous_coinc_time_03 = "00"
        self.previous_coinc_time_02 = "0A"

        self.lifetime_canvas = LifetimeCanvas(self.lifetimeWidget, logging.getLogger(), binning=self.binning)
        toolbar = NavigationToolbar(self.lifetime_canvas, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.lifetime_canvas)
        self.lifetimeWidget.setLayout(layout)
        self.lifetimeProgress.setVisible(False)
        self.show()
        self.lastUpdate = time()

        # decay trigger
        self.trigger = DecayTriggerThorough(logging.getLogger())

        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")
        self.startOutputWrite()
         # configure DAQ card with coincidence/veto settings
        self.setupLifetimeChannels()
        self._DAQServer.do("DC")
        self._DAQServer.do("CE")
        self._DAQServer.do("WC 03 04")
        self._DAQServer.do("WC 02 0A")

        # this should set the veto to none (because we have a
        # software veto) and the coincidence to single,
        # so we take all pulses
        self._DAQServer.do("WC 00 0F")

        self.start_time = getLocalTime()
        self.mu_file.open("a")
        self.mu_file.write("# new decay measurement run from: %s\n" %
                            self.start_time.strftime("%a %d %b %Y %H:%M:%S UTC"))


        self.thread = QThread()
        self.worker = LifetimeWorker(self._DAQServer)
        self.worker.daq_time = float(self.LifetimeMeasurementTime.value())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.lifeteimFinished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgressLifetime)
        self.worker.progressBar.connect(self.reportProgressBarLifetime)
        self.thread.start()
        self.startPulesMeasurement()

    def lifeteimFinished(self):
        self.LifetimeStop()
        self.lifetimeProgress.setValue(100)
        pass

    def calculateDecay(self, pulses):
        """
        Trigger muon decay

        :param pulses: extracted pulses
        :type pulses: list
        :returns: None
        """
        decay = self.trigger.trigger(
            pulses, single_channel=self.single_pulse_channel+1,
            double_channel=self.double_pulse_channel+1,
            veto_channel=self.veto_pulse_channel+1,
            min_decay_time=float(self.LifetimeMinSpace.value()),
            min_single_pulse_width=self.min_single_pulse_width,
            max_single_pulse_width=self.max_single_pulse_width,
            min_double_pulse_width=self.min_double_pulse_width,
            max_double_pulse_width=self.max_double_pulse_width)

        if decay is not None:
            when = getLocalTime()
            self.event_data.append((decay / 1000,
                                    when.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]))
            self.muon_counter += 1
            self.last_event_time = when
            logging.getLogger().info("We have found a decaying muon with a " +
                             "decay time of %f at %s" % (decay, when))

    def reportProgressLifetime(self, data):
        print(f"Got lifetime data:  {data}")
        self.calculateDecay(data)
        if not self.event_data:
            return

        self.LifetimeMounCount.setText(f"{self.muon_counter}")
        self.LifetimeLastMuon.setText(f'{self.last_event_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')

        if self.thread.isRunning():
            t = time()
            dt = t- self.lastUpdate
            if dt>10:
                decay_times = [decay_time[0] for decay_time in self.event_data]
                print(f"update data: {decay_times} -> {self.event_data}")
                self.lifetime_canvas.update_plot(decay_times)
                self.lastUpdate = t
                for decay in self.event_data:
                    decay_time = decay[1]  # .replace(' ', '_')
                    self.mu_file.write("%s Decay %s\n" % (repr(decay_time),
                                                        repr(decay[0])))
                self.event_data = []





    def reportProgressBarLifetime(self, progress):
        print(f"Lifetime progress: {progress}")
        self.lifetimeProgress.setVisible(True)
        self.lifetimeProgress.setValue(progress)

    def LifetimeStop(self):
        stop_time = getLocalTime()
        self.measurement_duration += stop_time - self.start_time

        # reset coincidence times
        self._DAQServer.do("WC 03 " + self.previous_coinc_time_03)
        self._DAQServer.do("WC 02 " + self.previous_coinc_time_02)

        logging.getLogger().info("Muon decay mode now deactivated, returning to " +
                         "previous setting (if available)")

        self.mu_file.write("# stopped run on: %s\n" %
                           stop_time.strftime("%a %d %b %Y %H:%M:%S UTC"))
        self.mu_file.close()

    def btnLifetimeStopClicked(self):
        self.LifetimeStop()
        self.thread.quit()

    def btnLifetimeFitClicked(self):
        self.fit_range = (float(self.LifetimeFitMin.value()), self.LifetimeFitMax.value())
        logging.getLogger().debug("Using fit range of %s" % repr(self.fit_range))
        fit_results = gaussian_fit(
            bincontent=np.asarray(self.lifetime_canvas.heights),
            binning=self.binning, fitrange=self.fit_range)

        print(f"fitresult: {fit_results}")
        if fit_results is not None:
            params = self.lifetime_canvas.show_fit(*fit_results)
            self.LifetimeFitParameters.setPlainText(f"""
            A:{round(params[0][0],2)} +- {round(params[1][0],2)}
            sigma:{round(params[0][1],2)} +- {round(params[1][1],2)}
            mu:{round(params[0][2],2)} +- {round(params[1][2],2)}
             """)

    def btnSendDAQCommandClicked(self):
        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")
        self._DAQServer.do(self.DAQCommand.text())


    def btnShowGPSClicked(self):
        try:
            self._DAQServer = DAQServer()
        except zmq.error.ZMQError:
            print("reusing old server")
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")
        self._DAQServer.get_gps_info()
        msg = self.sock.recv_string()
        obj = jsonpickle.decode(msg)
        print(f"Got GPS: {obj}")
        obj = jsonpickle.decode(obj.payload)

        self.GPSDateTime.setText(str(obj.GPSDateTime))
        self.Status.setText(str(obj.Status))
        self.PosFix.setText(str(obj.PosFix))
        self.Latitude.setText(str(obj.Latitude))
        self.Longitude.setText(str(obj.Longitude))
        self.Altitude.setText(str(obj.Altitude))
        self.NSats.setText(str(obj.NSats))
        self.PPSDelay.setText(str(obj.PPSDelay))
        self.FPGATime.setText(str(obj.FPGATime))
        self.ChkSumErr.setText(str(obj.ChkSumErr))


    def updateDAQ(self, msg):
        self.DAQOutput.moveCursor(QTextCursor.End)
        self.DAQOutput.insertPlainText(msg)

class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Adapter Class for xmlrpc
    """

    rpc_paths = ("/RPC2",)


# app = QtWidgets.QApplication(sys.argv)
# window = Ui()
# app.exec_()
