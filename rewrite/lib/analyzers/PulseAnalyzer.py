from .PulseExtractor import PulseExtractor
from time import time, sleep
import threading
import logging
import jsonpickle
import xmlrpc.client
import zmq
from datetime import datetime
from ..common.Record import RecordType, Record
from ..common.DataRecord import DataRecord


class PulseAnalyzer():
    """
    Class that manages the measurement of pulses from the DAQ card.
    """

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")  # Subscribe to all topics
        self.server = xmlrpc.client.ServerProxy("http://localhost:5556")

        # Setup the DAQ Card
        self.server.setup_channel(True, True, True, True, 'threefold')
        self.server.set_threashold(110, 110, 180, 110)

        self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = self.starttime+"_P.txt"

        self.running = False

    # def runDaemon(self):

    def measure_pulses(self, meastime=None):
        """
        Measure pulses (rising and falling edge times) of trigger events. Using PulseExtractor from muonic.
        :param meastime: Total measurement time in minutes. Default is None.
        """
        self.server.setRunning(True)
        self.server.reset_scalars()

        if isinstance(meastime, float):
            self.logger.info(
                'Starting pulse measurement. Total measurement time: %f' % meastime)
            if self.running:
                pass
            else:
                self.running = True
                self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                self.server.start_reading_data()
                # x = threading.Thread(target=self.runDaemon)
                # x.start()

            filename_pulses = self.starttime+"_P.txt"

            pe = PulseExtractor(self.logger, filename_pulses)
            pe.write_pulses(True)

            t = 0
            start_t = time()

            try:
                while t < (meastime*60):
                    msg = self.sock.recv_string()
                    obj = jsonpickle.decode(msg)
                    if obj.type == RecordType.DATA:
                        pe.extract(obj.payload.msg)
                    t = time()-start_t
                    self.logger.info(
                        'Measurement progress: %f %%' % (100*t/(meastime*60)))
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.running = False
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
            except (KeyboardInterrupt, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.running = False
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()

        elif meastime == None:
            self.logger.info(
                'Starting pulse measurement. No measurement time set.')
            if self.running:
                pass
            else:
                self.running = True
                self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                self.server.start_reading_data()

            filename_pulses = self.starttime+"_P.txt"

            pe = PulseExtractor(self.logger, filename_pulses)
            pe.write_pulses(True)

            try:
                while self.running:
                    msg = self.sock.recv_string()
                    obj = jsonpickle.decode(msg)
                    if obj.type == RecordType.DATA:
                        pe.extract(obj.payload.msg)

            except (KeyboardInterrupt, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.running = False
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
