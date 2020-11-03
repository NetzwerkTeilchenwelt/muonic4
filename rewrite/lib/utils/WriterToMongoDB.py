import xmlrpc.client
import zmq
import logging
import jsonpickle
import numpy as np
from mongoengine import connect
from .db.RecordAdapter import RecordAdapter

# from ..common.CountRecord import CountRecord
# from ..common.Record import RecordType, Record
# from ..common.PressureRecord import PressureType, PressureRecordg. list, tuple or set) of ch
# from ..common.TemperatureRecord import TemperatureRecord

from datetime import datetime
from time import time, sleep
import threading
import queue


class WriterToMongoDB():
    """
    Writes incoming data to the MongoDB for storage
    """

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")  # Subscribe to all topics
        connect('muonic', host='localhost', port=27017,
                username="root", password="muonic", authentication_source='admin')

    def DBWriter(self):
        while True:
            msg = self.sock.recv_string()
            obj = jsonpickle.decode(msg)
            record = RecordAdapter.get(obj)
            record.save()

    def runDaemon(self):
        writerTask = threading.Thread(target=self.DBWriter).start()
