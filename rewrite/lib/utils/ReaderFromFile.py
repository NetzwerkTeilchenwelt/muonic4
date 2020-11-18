import zmq
from datetime import datetime, timezone
from .db.RecordAdapter import RecordAdapter
import jsonpickle
import threading
import logging


class ReaderFromFile(object):
    """
    Class that read data from File and sends it as if it were coming from a DAQ card.
    This is a basic version, which can be extended.
    Inits the File connection and the zeromq socket. This needs to start before any analysis.
    """

    def __init__(self, filename, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        # connect to File
        self.filename = filename
        # setup zmq socket for the server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:1234")

    def run(self):
        """
        Get data from a certain timeframe from the db and then sends it through the socket.
        """
        # Set up the File aggregation pipeline for time based filtering
        with open(self.filename, "r") as file:
            for line in file:
                if line != "" and line != '\n':
                    print(f"Sening line: {line}")
                    self.socket.send_string(line)

    def setup_channel(self, ch0, ch1, ch2, ch3, coincidence):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug(
            f"Setting up fake channel: {ch0, ch1, ch2, ch3, coincidence}")

    def set_threashold(self, ch0, ch1, ch2, ch3):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug(f"setting fake threshold: {ch0, ch1, ch2, ch3}")

    def setRunning(self, state):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug(f"setting fake running: {state}")

    def reset_scalars(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("resettig fake scalars")

    def start_reading_data(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("starting to send data")
        x = threading.Thread(target=self.run)
        x.setDaemon(True)
        x.start()

    def read_scalars(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("reading fake scalars")

    def do(self, arg):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug(f"Doing fake {arg}")

    def get_temp_and_pressure(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("getting fake temp and pressure")

    def clear_queues(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("clearing non existing queues")

    def stop_reading_data(self):
        """
        Fake function. Just for API compatibility
        """
        self.logger.debug("stopping reading fake data")
