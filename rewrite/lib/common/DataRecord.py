from mongoengine import Document, StringField, BooleanField


class DataRecord(Document):
    valid = BooleanField(default=True)
    msg = StringField

    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg
    __str__ = __repr__
