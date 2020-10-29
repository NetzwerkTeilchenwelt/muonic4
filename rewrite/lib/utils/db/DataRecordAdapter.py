from mongoengine import BooleanField,  EmbeddedDocument, StringField


class DataRecordAdapter(EmbeddedDocument):
    valid = BooleanField()
    msg = StringField()

    @staticmethod
    def get(rec):
        return DataRecordAdapter(valid=rec.valid, msg=rec.msg)
