from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import pathlib
import multiprocessing
import subprocess
import logging
import datetime
from ..daq.DAQServer import DAQServer
from ..analyzers.RateAnalyzer import RateAnalyzer
from .widget import RateWidget
from .canvases import ScalarsCanvas, MplCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

class RateWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(list)

    def __init__(self, server):
        QObject.__init__(self)
        self._DAQServer = server
        self._RateAnalyser = RateAnalyzer(logger=None, headless=False)
        self._RateAnalyser.server = self._DAQServer
        self._RateAnalyser.progress = self.progress
        self._RateAnalyser.finished = self.finished
    def run(self):
        self._RateAnalyser.measure_rates(timewindow=10.0, meastime=1.0)

class Ui(QtWidgets.QMainWindow):
    serverTask = threading.Thread()

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

        self.RateWidget = self.findChild(QtWidgets.QWidget, "rateWidget")



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
        self._DAQServer = DAQServer()

        # info fields
        self.start_time = datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S")
        self.daq_time = self.OpenStudiesReadoutInterval.value()
        self.max_rate = 0

        self.getCoincidence()
        self.setupChannels()

        self.thread = QThread()

        self.worker = RateWorker(self._DAQServer)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
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

    def reportProgress(self, data):
        print(f"ReportProgress: {data}")
        self.scalars_monitor.update_plot(data)
        max_rate = max(data[:5])
        if max_rate > self.max_rate:
            self.max_rate = max_rate
        self.lnRateStartedAt.setText(str(self.start_time))
        self.lnRateTimeDAQ.setText(str(self.daq_time))
        self.lnRateMax.setText(str(self.max_rate))


    def btnOpenStudiesRateStopClicked(self):
        pass


class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Adapter Class for xmlrpc
    """

    rpc_paths = ("/RPC2",)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
