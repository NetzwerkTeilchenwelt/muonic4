from PyQt5 import QtWidgets, uic
import sys
import os
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import pathlib
import multiprocessing
import subprocess
from ..daq.DAQServer import DAQServer


class Ui(QtWidgets.QMainWindow):
    serverTask = threading.Thread()

    def __init__(self):
        super(Ui, self).__init__()
        print(f"PWD: {pathlib.Path(__file__).parent.resolve()}")
        uic.loadUi(f"{pathlib.Path(__file__).parent.resolve()}/muonic4.ui", self)

        # Get buttons for open studies
        self.btOpenStudiesStop = self.findChild(
            QtWidgets.QPushButton, "btOpenStudiesStop"
        )
        self.btOpenStudiesStart = self.findChild(
            QtWidgets.QPushButton, "btOpenStudiesStart"
        )

        self.btOpenStudiesStart.clicked.connect(self.btOpenStudiesStartClicked)
        self.btOpenStudiesStop.clicked.connect(self.btOpenStudiesStopClicked)

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
        self._DAQServer = SimpleXMLRPCServer(
            ("localhost", 5556), requestHandler=RequestHandler, allow_none=True
        )
        self.serverTask = threading.Thread(target=self.startDAQServer)
        self.serverTask.start()
        # self.startDAQServer()
        # self.serverTask = multiprocessing.Process(target=self.startDAQServer, args=())
        # self.serverTask.start()

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
        print("Joinhinh")
        self.shutdowntask = threading.Thread(target=self.shutdownDAQServer).start()
        self.serverTask.join()
        print("Joined")

    def shutdownDAQServer(self):
        print("shutdown task")
        self._DAQServer.shutdown()

    def startDAQServer(self):
        self._DAQServer.register_introspection_functions()
        self._DAQServer.register_instance(DAQServer())
        self._DAQServer.serve_forever()


class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Adapter Class for xmlrpc
    """

    rpc_paths = ("/RPC2",)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
