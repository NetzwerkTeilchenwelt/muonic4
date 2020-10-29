from mongoengine import BooleanField, EmbeddedDocument, StringField, DecimalField
from ...common.PressureRecord import PressureType


class PressureRecordAdapter(EmbeddedDocument):
    valid = BooleanField()
    pressure = DecimalField()
    pressure_type = StringField()

    @staticmethod
    def get(rec):
        t = ""
        if rec.pressure_type == PressureType.PLAIN:
            t = "PLAIN"
        else:
            t = "MBAR"
        return PressureRecordAdapter(valid=rec.valid, pressure=rec.pressure, pressure_type=t)
