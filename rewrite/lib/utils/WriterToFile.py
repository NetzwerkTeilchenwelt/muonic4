import xmlrpc.client
import zmq
import logging
import jsonpickle
from .db.RecordAdapter import RecordAdapter

# from ..common.CountRecord import CountRecord
# from ..common.Record import RecordType, Record
# from ..common.PressureRecord import PressureType, PressureRecordg. list, tuple or set) of ch
# from ..common.TemperatureRecord import TemperatureRecord

from datetime import datetime
from time import time, sleep
import threading
import queue


class WriterToFile:
    """
    Writes incoming data to a file for storage
    """

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")  # Subscribe to all topics
        self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.outFile = open(self.starttime + "_F.txt", "a")

    def fileWriter(self):
        while True:
            msg = self.sock.recv_string()
            self.outFile.write(jsonpickle.decode(msg).to_json() + "\n")
            self.outFile.flush()

    def runDaemon(self):
        writerTask = threading.Thread(target=self.fileWriter).start()
