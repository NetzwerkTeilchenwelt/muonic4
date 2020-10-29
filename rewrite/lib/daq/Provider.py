import logging
import re
import multiprocessing as mp
import queue
from .Connection import DAQConnection

from .Exceptions import DAQIOError, DAQMissingDependencyError


class DAQProvider(object):
    """
    Class providing the public API and helpers for the communication with the DAQ card
    """

    LINE_PATTERN = re.compile("^[a-zA-Z0-9+-.,:()=$/#?!%_@*|~' ]*[\n\r]*$")

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.out_queue = mp.Queue()
        self.in_queue = mp.Queue()

        self.daq = DAQConnection(self.in_queue, self.out_queue, self.logger)

        # Set up the thread to do asynchronous I/O. More can be made if
        # necessary. Set daemon flag so that the threads finish when the main
        # app finishes
        self.read_thread = mp.Process(target=self.daq.read, name="pREADER")
        self.read_thread.daemon = True
        self.read_thread.start()

        self.write_thread = mp.Process(target=self.daq.write, name="pWRITER")
        self.write_thread.daemon = True
        self.write_thread.start()

    def get(self, *args):
        """
        Get data from the DAQ card. 

        Raises DAQIOError if the queue is empty.

        :param args: queue arguments
        :type args: list
        :returns: str or None -- next item from the queue
        :raises: DAQIOError
        """
        try:
            line = self.out_queue.get(*args)
        except queue.Empty:
            raise DAQIOError("Queue is empty")
        return self.validate_line(line)

    def put(self, *args):
        """
        Senf data to the DAQ card.

        :param args: queue arguments
        :type args: list
        :returns: None
        """
        self.in_queue.put(*args)

    def data_available(self):
        """
        Tests if data is available from the DAQ card.

        :returns: int or bool
        """
        try:
            size = self.out_queue.qsize()
        except NotImplementedError:
            self.logger.debug("Running macOS version of muonic")
            size = not self.out_queue.empty()
        return size

    def validate_line(self, line):
        """
        Validate line againt regex pattern. 
        Returns None if the provided line is invalid or the line if it is valid.

        :param line: line to validate
        :type line: str
        :returns: str or None
        """
        if self.LINE_PATTERN.match(line.decode("ascii")) is None:
            line = line.rstrip('\r\n')
            self.logger.warning(f"Got invalid data from the DAQ card: {line}")
            return None
        return line
