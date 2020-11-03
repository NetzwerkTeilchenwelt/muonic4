from ...common.CountRecord import CountRecord
from mongoengine import BooleanField, EmbeddedDocument, DecimalField, IntField


class CountRecordAdapter(EmbeddedDocument):
    """
    Adapter class to store Counts in MongoDB

    :param valid (Bool): validity of the record.
    :param counts_ch[X] (int): Counts in channel X
    :param counts_trigger (int): trigger counts recieved
    :param counts_time (Real): the time of the record
    """
    valid = BooleanField()
    """
    Set to true if the underlying record is valid
    """
    counts_ch0 = IntField()
    """
    Counts in channel 0
    """
    counts_ch1 = IntField()
    """
    Counts in channel 1
    """
    counts_ch2 = IntField()
    """
    Counts in channel 2
    """
    counts_ch3 = IntField()
    """
    Counts in channel 3
    """
    counts_trigger = IntField()
    """
    Trigger counts
    """
    counters_time = DecimalField()
    """
    Counts in the time register of the DAQ card. Basically a timestamp
    """

    @staticmethod
    def get(rec):
        """
        Creates a CountRecordAdapter from a CountRecord

        :param rec: CountRecord to convert
        """
        return CountRecordAdapter(valid=rec.valid,
                                  counts_ch0=rec.counts_ch0,
                                  counts_ch1=rec.counts_ch1,
                                  counts_ch2=rec.counts_ch2,
                                  counts_ch3=rec.counts_ch3,
                                  counts_trigger=rec.counts_trigger,
                                  counters_time=rec.counters_time)

    def createCount(self):
        """
        Creates a CountRecord from the current object

        :returns: CountRecord from the current CountRecordAdapter
        """
        rec = CountRecord("")
        rec.valid = self.valid
        rec.counts_ch0 = self.counts_ch0
        rec.counts_ch1 = self.counts_ch1
        rec.counts_ch2 = self.counts_ch2
        rec.counts_ch3 = self.counts_ch3
        rec.counts_trigger = self.counts_trigger
        rec.counters_time = self.counters_time
        return rec
