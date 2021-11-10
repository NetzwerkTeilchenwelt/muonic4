import logging
import jsonpickle
import zmq
from datetime import datetime
import xmlrpc.client

class GPSAnalyzer():
    """
    Class that manages GPS infos
    """

    def __init__(self, logger=None, headless=True):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")

        if headless:
            self.server = xmlrpc.client.ServerProxy("http://localhost:5556")

        self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = self.starttime+"_GPS.txt"
        self.headless = headless
        self.running = False

    def getGPSInfos(self):
        self.server.setRunning(True)
        self.server.get_gps_info()
        msg = self.sock.recv_string()
        obj = jsonpickle.decode(msg)
        print(f"Got GPS: {obj}")