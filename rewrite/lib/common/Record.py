from enum import Enum
from uuid import uuid4

class RecordType(Enum):
    """
    Enum of the possible types of Records between DAQ and analysis.
    Enum for "type-safety"
    """
    CONTROL = 0
    DATA = 1
    TEMPERATURE = 2
    PRESSURE = 3
    COUNTER = 4


class Record(object):
    """
    The basic data-structure used to communicate between DAQ and analysis

    VERY EARLY STAGE! Everything is subject to change!

    :param RecType: Type of the record
    :param timestamp: Unixtimestamp
    :param number: Sequential number of the record
    :param id: UUID4 of the record
    :param payload: Payload to be send 
    """

    def __init__(self, RecType, timestamp, payload):
        self.type = RecType
        self.timestamp = timestamp
        self.payload = payload