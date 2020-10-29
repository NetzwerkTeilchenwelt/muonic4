from mongoengine import BooleanField,  EmbeddedDocument, StringField


class DataRecordAdapter(EmbeddedDocument):
    msg = StringField()

    @staticmethod
    def get(rec):
        return DataRecordAdapter(msg=rec)
