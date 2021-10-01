from PyQt5 import QtWidgets, uic
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import pathlib
import multiprocessing
import subprocess
import logging
from ..daq.DAQServer import DAQServer
from ..analyzers.RateAnalyzer import RateAnalyzer
from .widget import RateWidget
from .canvases import ScalarsCanvas, MplCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

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

        # Get trigger window for open studies
        self.OpenStudiesTriggerWindow = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesTriggerWindow"
        )

        self.RateWidget = self.findChild(QtWidgets.QWidget, "rateWidget")

        self.show()

    def btOpenStudiesStartClicked(self):
        print("Starting DAQ Server...")
        # if not self.serverTask:
        #     self.serverTask = threading.Thread(target=self.startDAQServer).start()
        #     print(f"Started.. in {type(self.serverTask)}")
        #     self.serverTask.start()
        # elif not self.serverTask.is_alive():
        #     self.serverTask = threading.Thread(target=self.startDAQServer)
        #     print(f"Started.. out {type(self.serverTask)}")
        #     self.serverTask.start()
        # self._DAQServer = SimpleXMLRPCServer(
        #     ("localhost", 5556), requestHandler=RequestHandler, allow_none=True
        # )
        self._DAQServer = DAQServer()
        # self.serverTask = threading.Thread(target=self.startDAQServer)
        # self.serverTask.start()
        # self.startDAQServer()
        # self.serverTask = multiprocessing.Process(target=self.startDAQServer, args=())
        # self.serverTask.start()
       # self._RareAnalyser = RateAnalyzer(logger=None, headless=False)

        print(f"Started..  {type(self.serverTask)}")

    def btOpenStudiesStopClicked(self):
        # print(f"Stop {self.serverTask.pid}")
        # self._DAQServer.server_close()
        # self._DAQServer.shutdown()
        # self.serverTask.kill()
        # self.serverTask.terminate()
        # print(
        #     f"stopped {self.serverTask.is_alive()}, {output}, {error}, {self.serverTask.pid}"
        # )
        # self.serverTask.
        # if self.serverTask.is_alive():
        #     print("Joining")
        #     self.serverTask.join(timeout=0.3)
        #     if self.serverTask.is_alive():
        #         print("Still alive")
        # print("Joinhinh")
        # self.shutdowntask = threading.Thread(target=self.shutdownDAQServer).start()
        # self.serverTask.join()
        # print("Joined")
        pass

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
        self.getCoincidence()
        self.setupChannels()
        # layout.addWidget(self.scalars_monitor)
        # self.RateWidget.addWidget()
        self._RateAnalyser = RateAnalyzer(logger=None, headless=False)
        self._RateAnalyser.server = self._DAQServer
        self._RateAnalyser.plot = self.scalars_monitor
        self._RateAnalyser.measure_rates(timewindow=10.0, meastime=1.0)
        # self.RateWidget = RateWidget(logging.getLogger(), "foo.txt")
        # self.RateWidget.table = self.findChild(
        #     QtWidgets.QTableWidget, "tblRates"
        # )
        # self.RateWidget.server = self._DAQServer
        # self.RateWidget.calculate()
        # self.RateWidget.update()
        print("... started")


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
