from datetime import datetime
from ...common.Record import RecordType
from .CountRecordAdapter import CountRecordAdapter
from .DataRecordAdapter import DataRecordAdapter
from .PressureRecordAdapter import PressureRecordAdapter
from .TemperatureRecordAdapter import TemperatureRecordAdapter
from mongoengine import Document, BooleanField, DateTimeField, EmbeddedDocumentField, EmbeddedDocument, StringField, DecimalField, IntField, GenericReferenceField

CHOICES = ('CONTROL', 'DATA', 'TEMPERATURE', 'PRESSURE', 'COUNTER')


class RecordAdapter(Document):
    meta = {
        'collection': 'records'
    }
    packageNumber = IntField()
    type = StringField(choices=CHOICES)
    timestamp = DateTimeField()
    payload_cnt = EmbeddedDocumentField(CountRecordAdapter)
    payload_dat = EmbeddedDocumentField(DataRecordAdapter)
    payload_tem = EmbeddedDocumentField(TemperatureRecordAdapter)
    payload_prs = EmbeddedDocumentField(PressureRecordAdapter)

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
