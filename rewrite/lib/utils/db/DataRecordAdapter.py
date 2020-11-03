from ...common.DataRecord import DataRecord
from mongoengine import BooleanField, EmbeddedDocument, StringField


class DataRecordAdapter(EmbeddedDocument):
    msg = StringField()

    @staticmethod
    def get(rec):
        return DataRecordAdapter(msg=rec)

    def set(self):
        return DataRecord(self.msg)
