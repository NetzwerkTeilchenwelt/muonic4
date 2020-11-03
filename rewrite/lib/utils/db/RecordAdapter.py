from datetime import datetime
from ...common.Record import RecordType, Record
from .CountRecordAdapter import CountRecordAdapter
from .DataRecordAdapter import DataRecordAdapter
from .PressureRecordAdapter import PressureRecordAdapter
from .TemperatureRecordAdapter import TemperatureRecordAdapter
from mongoengine import Document, ObjectIdField, BooleanField, DateTimeField, EmbeddedDocumentField, EmbeddedDocument, StringField, DecimalField, IntField, GenericReferenceField

CHOICES = ('CONTROL', 'DATA', 'TEMPERATURE', 'PRESSURE', 'COUNTER')


class RecordAdapter(Document):
    meta = {
        'collection': 'records'
    }
    _id = ObjectIdField()
    packageNumber = IntField()
    type = StringField(choices=CHOICES)
    timestamp = DateTimeField()
    payload_cnt = EmbeddedDocumentField(CountRecordAdapter)
    payload_dat = EmbeddedDocumentField(DataRecordAdapter)
    payload_tem = EmbeddedDocumentField(TemperatureRecordAdapter)
    payload_prs = EmbeddedDocumentField(PressureRecordAdapter)

    def __init__(self, **kwargs):
        super(RecordAdapter, self).__init__(**kwargs)
        self.__dict__.update(kwargs)

    @staticmethod
    def getChoice(i):
        for v in CHOICES:
            if v[0] == i:
                return v[1]

    @staticmethod
    def get(rec):
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

    def set(self):
        recPayload = None
        recType = None
        if self.type == 'CONTROL':
            recType = RecordType.CONTROL
        elif self.type == 'DATA':
            recType = RecordType.DATA
            recPayload = self.payload_dat.set()
        elif self.type == 'TEMPERATURE':
            recType = RecordType.TEMPERATURE
            recPayload = self.payload_tem.set()
        elif self.type == 'PRESSURE':
            recType = RecordType.PRESSURE
            recPayload = self.payload_prs.set()
        elif self.type == 'COUNTER':
            recType = RecordType.COUNTER
            recPayload = self.payload_cnt.set()

        recPackageNumber = self.packageNumber
        recTimestamp = self.timestamp.timestamp()

        rec = Record(recPackageNumber, recType, recTimestamp, recPayload)
        return rec
