import xmlrpc.client
import zmq
import logging
import jsonpickle
import numpy as np

from ..common.CountRecord import CountRecord
from ..common.Record import RecordType, Record
from ..common.PressureRecord import PressureType, PressureRecord
from ..common.TemperatureRecord import TemperatureRecord
from datetime import datetime
from time import time, sleep
import threading
import queue


class RateAnalyzer():
    """
    Class that manages the measurement of muon rate.
    """

    def __init__(self, logger=None, headless=True):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

        # Setup the communication with the data well
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("")  # Subscribe to all topics
        self.headless = headless
        if headless:
            self.server = xmlrpc.client.ServerProxy("http://localhost:5556")
            self.server.setup_channel(True, True, True, True, 'threefold')
            self.server.set_threashold(110, 110, 180, 110)
        # self.server.get_gps_info()
        self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = self.starttime+"_R.txt"
        #self.file = open(self.filename, 'a')
        self.prev_rates = None
        self.outQueue = queue.Queue()
        writerTask = threading.Thread(target=self.fileWriter).start()

        self.pressure = 99
        self.temperature = 20

    def fileWriter(self):
        with open(self.filename, 'a') as f:
            while True:
                item = self.outQueue.get()
                f.write(item)
                f.write('\n')
                f.flush()

    def write_rates_to_file(self, firstline=False):
        """
        Saves data to file during rate measurements.
        """
        if firstline:
            self.logger.info(
                'Starting to write data to file %s' % self.filename)
            self.outQueue.put(
                " date | time | R0 | R1 | R2 | R3 | R_trigger | chan0 | chan1 | chan2 | chan3 | trigger | Delta_time | Pressure [mBar] | Temperature [C] \n")

    def runDaemon(self):
        while True:
            msg = self.sock.recv_string()
            obj = jsonpickle.decode(msg)
            if obj.type == RecordType.COUNTER and obj.payload.valid == True:
                print(
                    f"Package No.: {obj.packageNumber} Type: {obj.type} timestamp: {obj.timestamp} payloads: {repr(obj.payload)}")
                #print(f"date: {datetime.fromtimestamp(obj.timestamp)}")
                cntRec = obj.payload
                if self.prev_rates is None:
                    self.prev_rates = np.array(
                        [cntRec.counts_ch0, cntRec.counts_ch1, cntRec.counts_ch2, cntRec.counts_ch3, cntRec.counts_trigger])
                    self.previous_time = datetime.fromtimestamp(obj.timestamp)
                else:
                    curRates = np.array([cntRec.counts_ch0, cntRec.counts_ch1,
                                         cntRec.counts_ch2, cntRec.counts_ch3, cntRec.counts_trigger])
                    current_time = datetime.fromtimestamp(obj.timestamp)
                    self.delta_time = (
                        current_time - self.previous_time).total_seconds()
                    self.previous_time = current_time

                    deltaRates = curRates - self.prev_rates
                    self.prev_rates = curRates
                    deltaRates = deltaRates / self.delta_time
                    if self.dateandtime is None:
                        self.dateandtime = datetime.now()

                    if not self.headless :
                        send = deltaRates.tolist()
                        send.append(self.delta_time)
                        print(f"deltaRates: {deltaRates}, self.delta_time: {self.delta_time}, send: {send}")
                        self.progress.emit(send)
                    self.outQueue.put(
                        f"{self.dateandtime} {deltaRates[0]} {deltaRates[1]} {deltaRates[2]} {deltaRates[3]} {deltaRates[4]} {curRates[0]} {curRates[1]} {curRates[2]} {curRates[3]} {curRates[4]} {self.delta_time} {self.current_pressure} {self.temperature}")
            elif obj.type == RecordType.PRESSURE and obj.payload.valid == True and obj.payload.pressure_type == PressureType.MBAR:
                self.current_pressure = obj.payload.pressure
            elif obj.type == RecordType.TEMPERATURE and obj.payload.valid == True:
                self.temperature = obj.payload.temperature
                #print(f"{self.dateandtime} {curRates[0]} {curRates[1]} {curRates[2]} {curRates[3]} {curRates[4]} {deltaRates[0]} {deltaRates[1]} {deltaRates[2]} {deltaRates[3]} {deltaRates[4]}")

    def measure_rates(self, timewindow=5.0, meastime=None):
        """
        Measure rates seen by the counters.
        :param timewindow: Time between successive rate measurements in seconds. Default is 5 seconds.
        :param meastime: Total measurement time in minutes. Default is None.
        """
        if isinstance(meastime, float):
            self.logger.info('Starting rate measurement. Rate is measured every %f seconds, total measurement time: %f min' % (
                timewindow, meastime))
            self.server.setRunning(True)

            self.write_rates_to_file(firstline=True)
            self.server.reset_scalars()
            # x = threading.Thread(target=self.start_reading_data)
            # x.start()
            print("before reading data")
            self.server.start_reading_data()
            x = threading.Thread(target=self.runDaemon)
            # x.start()
            print("after reading data")

            t = 0
            try:
                while t < (meastime*60):
                    # self.server.read_scalars()
                    time_start = time()
                    sleep(timewindow)
                    self.server.read_scalars()
                    time_end = time()
                    self.dateandtime = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f")[:-3]
                    self.server.do('TH')
                    self.server.do('BA')
                    self.server.get_temp_and_pressure()
                    sleep(0.5)
                    self.delta_time = time_end-time_start
                    # self.server.calculate_rates()
                    if not x.isAlive():
                        x.start()
                    # self.write_rates_to_file()
                    if not self.headless:
                        self.progressbar.emit(100*t/(meastime*60) )
                    self.logger.info('Measurement progress: %f %%' %
                                     (100*t/(meastime*60)))
                    t += self.delta_time
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.running = False
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
                self.finished.emit()

            except (KeyboardInterrupt, AttributeError, RuntimeError, NameError, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.server.setRunning(False)
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
                self.finished.emit()


        elif meastime == None:
            self.logger.info(
                'Starting rate measurement. Rate is measured every %f seconds. No measurement time set.' % timewindow)
            self.running = True
            self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.write_rates_to_file(firstline=True)
            self.server.reset_scalars()
            # x = threading.Thread(target=self.process_incoming)
            # x.start()
            x = threading.Thread(target=self.server.process_incoming())
            x.start()

            try:
                while self.running:
                    self.server.read_scalars()
                    time_start = time()
                    sleep(timewindow)
                    self.server.read_scalars()
                    time_end = time()
                    self.dateandtime = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f")[:-3]
                    self.server.do('TH')
                    self.server.do('BA')
                    sleep(0.5)
                    self.server.get_temp_and_pressure()
                    self.delta_time = time_end-time_start

                    self.write_rates_to_file()
            except (KeyboardInterrupt, AttributeError, RuntimeError, NameError, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.server.setRunning(False)
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
                self.finished.emit()


        else:
            self.logger.error(
                'Got incorrect meastime. If you do not want to specify meastime, set it to None.')
