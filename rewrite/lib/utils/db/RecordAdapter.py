from datetime import datetime
from ...common.Record import RecordType, Record
from .CountRecordAdapter import CountRecordAdapter
from .DataRecordAdapter import DataRecordAdapter
from .PressureRecordAdapter import PressureRecordAdapter
from .TemperatureRecordAdapter import TemperatureRecordAdapter
from mongoengine import Document, ObjectIdField, BooleanField, DateTimeField, EmbeddedDocumentField, EmbeddedDocument, StringField, DecimalField, IntField, GenericReferenceField

CHOICES = ('CONTROL', 'DATA', 'TEMPERATURE', 'PRESSURE', 'COUNTER')


class RecordAdapter(Document):
    """
    This is an adapter class which helps to save and load a record in MongoDB.


    :param _id: Object ID given by MongoDB. Explicitly declared to be able to load from dict.
    :param packageNumber: A sequential number of all packages send by a DAQ server
    :param RecType: Type of the record
    :param timestamp: Unixtimestamp
    :param payload_cnt: Count Payload
    :param payload_dat: Data Payload
    :param payload_tme: Temperature Payload
    :param payload_prs: Pressure Payload

    Sadly the payload for each type of payload needs to be in a separate field, as we need an EmbeddedDocumentField of a certain type.
    """
    meta = {
        'collection': 'records'
    }
    _id = ObjectIdField()
    packageNumber = IntField()
    type = StringField(choices=CHOICES)
    """
    :String: only valid choices here are: CONTROL, DATA, TEMPERATURE, PRESSURE, COUNTER
    """
    timestamp = DateTimeField()
    payload_cnt = EmbeddedDocumentField(CountRecordAdapter)
    payload_dat = EmbeddedDocumentField(DataRecordAdapter)
    payload_tem = EmbeddedDocumentField(TemperatureRecordAdapter)
    payload_prs = EmbeddedDocumentField(PressureRecordAdapter)

    def __init__(self, **kwargs):
        """
        Call the superclass constructor and provide functionality to construct from a dict.
        """
        super(RecordAdapter, self).__init__(**kwargs)
        self.__dict__.update(kwargs)

    @staticmethod
    def getChoice(i):
        """
        Translate RecordType aka int to string.

        :param i: RecordType to be converted.
        """
        for v in CHOICES:
            if v[0] == i:
                return v[1]

    @staticmethod
    def get(rec):
        """
        Construct a RecordAdapter from a Record

        :param rec: a record that will be converted to a RecordAdapter
        :returns: a newly constructed  RecordAdapter
        """
        if rec.type == RecordType.COUNTER:
            return RecordAdapter(packageNumber=rec.packageNumber, type=CHOICES[int(rec.type)], timestamp=datetime.fromtimestamp(
                rec.timestamp), payload_cnt=CountRecordAdapter.get(rec.payload))
        elif rec.type == RecordType.DATA:
            return RecordAdapter(packageNumber=rec.packageNumber, type=CHOICES[int(rec.type)], timestamp=datetime.fromtimestamp(
                rec.timestamp), payload_dat=DataRecordAdapter.get(rec.payload))
        elif rec.type == RecordType.TEMPERATURE:
            return RecordAdapter(packageNumber=rec.packageNumber, type=CHOICES[int(rec.type)], timestamp=datetime.fromtimestamp(
                rec.timestamp), payload_tem=TemperatureRecordAdapter.get(rec.payload))
        elif rec.type == RecordType.PRESSURE:
            return RecordAdapter(packageNumber=rec.packageNumber, type=CHOICES[int(rec.type)], timestamp=datetime.fromtimestamp(
                rec.timestamp), payload_prs=PressureRecordAdapter.get(rec.payload))

    def createRecord(self):
        """
        Creates a Record with the current data.

        :return: Record with the current data
        """
        recPayload = None
        recType = None
        if self.type == 'CONTROL':
            recType = RecordType.CONTROL
        elif self.type == 'DATA':
            recType = RecordType.DATA
            recPayload = self.payload_dat.createData()
        elif self.type == 'TEMPERATURE':
            recType = RecordType.TEMPERATURE
            recPayload = self.payload_tem.createTemperature()
        elif self.type == 'PRESSURE':
            recType = RecordType.PRESSURE
            recPayload = self.payload_prs.createPressure()
        elif self.type == 'COUNTER':
            recType = RecordType.COUNTER
            recPayload = self.payload_cnt.createCount()

        recPackageNumber = self.packageNumber
        recTimestamp = self.timestamp.timestamp()

        rec = Record(recPackageNumber, recType, recTimestamp, recPayload)
        return rec
