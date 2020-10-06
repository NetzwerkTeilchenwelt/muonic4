import logging
import serial
from .getDevice import get_Device
from time import sleep

class DAQConnection(object):
    
    """
    DAQ Connection class.

    Raises SystemError if serial connection cannot be established.

    :param logger: logger object
    :type logger: logging.Logger
    :param in_queue: input queue
    :param out_queue: output queue
    :raises: SystemError
    """

    def __init__(self, in_queue, out_queue, logger=None):
        if logger is None: 
            logger = logging.getLogger()
        self.logger = logger
        self.running = 1
        self.in_queue = in_queue
        self.out_queue = out_queue

        try:
            self.serial_port = self.get_serial_port()
        except serial.SerialException as e:
            self.logger.fatal(f"SerialException! Error: {e.message}")
            raise SystemError(e)

    def get_serial_port(self):
        """
        Check out which device (/dev/tty) is used for DAQ communication.

        Raises OSError if binary 'which_tty_daq' cannot be found.

        :returns: serial.Serial -- serial connection port
        :raises: OSError
        """

        connected = False
        serial_port = None

        while not connected: 
            dev = "/dev/" + get_Device()

            self.logger.info(f"DAQ Card found at {dev}")
            self.logger.info("Trying to connect")

            try:
                serial_port = serial.Serial(port=dev, baudrate=115200,
                                            bytesize=8, parity='N', stopbits=1,
                                            timeout=0.5, xonxoff=True)
                connected = True
            except serial.SerialException as e:
                self.logger.error(e)
                self.logger.error("Retrying in 5 seconds")
                sleep(5)
        self.logger.info("Successfully connected to DAQ card")
        return serial_port
    
    def read(self):
        """
        Gets Data from the DAQ card. Read it from the provided queue.

        :returns: None
        """

        min_sleep_time = 0.01 #seconds
        max_sleep_time = 0.2  #seconds
        sleep_time = min_sleep_time  # seconds

        while self.running:
            try:
                if self.serial_port.inWaiting():
                    while self.serial_port.inWaiting():
                        self.out_queue.put(self.serial_port.readline().strip())
                        sleep_time = max(sleep_time / 2, min_sleep_time)
                else:
                    sleep_time = min(1.5 * sleep_time, max_sleep_time)
                sleep(sleep_time)
            except (IOError, OSError):
                self.logger.error("IOError")
                self.serial_port.close()
                self.serial_port = self.get_serial_port()
        
    def write(self):
        """
        Writes messages from the in queue to the DAQ card

        :returns: None
        """

        while self.running:
            try:
                while self.in_queue.qsize():
                    try:
                        out_str = str(self.in_queue.get(0)) + str("\r")
                        self.serial_port.write(out_str.encode("ascii"))
                    except (queue.Empty, serial.SerialTimeoutException):
                        pass
            except NotImplementedError:
                self.logger.debug("Running macOS version of muonic")
                while True:
                    try:
                        out_str = str(self.in_queue.get(timeout=0.01)) + str("\r")
                        self.serial_port.write(out_str.encode("ascii"))
                    except (queue.Empty, serial.SerialTimeoutException):
                        pass
            sleep(0.1)