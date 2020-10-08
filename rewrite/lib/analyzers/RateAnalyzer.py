import xmlrpc.client
import zmq
import logging
from datetime import datetime
from time import time, sleep
import threading
 

class RateAnalyzer():
    def __init__(self, logger=None):
        if logger is None: 
            logger = logging.getLogger()
        self.logger = logger

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.sock.connect("tcp://127.0.0.1:1234")
        self.sock.subscribe("") # Subscribe to all topics
        self.server = xmlrpc.client.ServerProxy("http://localhost:5556")
        self.server.setup_channel(True, True, True, True, 'threefold')
        self.server.set_threashold(110, 110, 180, 110)
        self.server.get_gps_info()

    def write_rates_to_file(self, filename='', firstline=False):
        """
        Saves data to file during rate measurements.
        """
        with open(filename, 'a') as f:
            if firstline:
                self.logger.info(
                    'Starting to write data to file %s' % filename)
                f.write(
                    " date | time | R0 | R1 | R2 | R3 | R_trigger | chan0 | chan1 | chan2 | chan3 | trigger | Delta_time | Pressure [mBar] | Temperature [C] \n")
            else:
                f.write("%s %f %f %f %f %f %f %f %f %f %f %f %f %f \n" % (self.dateandtime,
                                                                          self.rates[0],
                                                                          self.rates[1],
                                                                          self.rates[2],
                                                                          self.rates[3],
                                                                          self.rates[4],
                                                                          self.server.getCounts('0'),
                                                                          self.server.getCounts('1'),
                                                                          self.server.getCounts('2'),
                                                                          self.server.getCounts('3'),
                                                                          self.server.getCounts('trigger'),
                                                                          self.delta_time,
                                                                          self.pressure_mbar,
                                                                          self.temperature))


    def calculate_rates(self):
        """
        Calculate rates during rate measurements.
        """
        counts_ch0_start, counts_ch1_start, counts_ch2_start, counts_ch3_start, counts_trigger_start = self.server.get_scalars()
        counts_ch0_end, counts_ch1_end, counts_ch2_end, counts_ch3_end, counts_trigger_end = self.server.get_scalars()

        counters_previous = [counts_ch0_start, counts_ch1_start,
                             counts_ch2_start, counts_ch3_start, counts_trigger_start]
        counters = [counts_ch0_end, counts_ch1_end,
                    counts_ch2_end, counts_ch3_end, counts_trigger_end]

        self.diff_counters = []
        self.rates = []

        for i in range(len(counters)):
            if counters[i] >= counters_previous[i]:
                self.diff_counters.append(counters[i]-counters_previous[i])
            elif counters[i] < counters_previous[i]:
                self.diff_counters.append(
                    max_counts-counters_previous[i]+counters[i])
            self.rates.append(self.diff_counters[i]/self.delta_time)


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
            self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.write_rates_to_file(
                filename=self.starttime+"_R.txt", firstline=True)
            self.server.reset_scalars()
            # x = threading.Thread(target=self.start_reading_data)
            # x.start()
            print("before reading data")
            self.server.start_reading_data()
            print("after reading data")

            t = 0
            try:
                while t < (meastime*60):
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
                    self.calculate_rates()
                    self.write_rates_to_file(filename=self.starttime+"_R.txt")
                    self.logger.info('Measurement progress: %f %%' %
                                     (100*t/(meastime*60)))
                    t += self.delta_time
                self.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.running = False
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()
            except (KeyboardInterrupt, AttributeError, RuntimeError, NameError, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.server.setRunning(False)
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()

        elif meastime == None:
            self.logger.info(
                'Starting rate measurement. Rate is measured every %f seconds. No measurement time set.' % timewindow)
            self.running = True
            self.starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.write_rates_to_file(
                filename=self.starttime+"_R.txt", firstline=True)
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
                    self.calculate_rates()
                    self.write_rates_to_file(filename=self.starttime+"_R.txt")
            except (KeyboardInterrupt, AttributeError, RuntimeError, NameError, SystemExit):
                self.server.stop_reading_data()
                self.logger.info('Measurement is stopping. Please wait!')
                sleep(5)
                self.server.setRunning(False)
                self.logger.info('Measurement stopped!')
                self.server.clear_queues()

        else:
            self.logger.error(
                'Got incorrect meastime. If you do not want to specify meastime, set it to None.')