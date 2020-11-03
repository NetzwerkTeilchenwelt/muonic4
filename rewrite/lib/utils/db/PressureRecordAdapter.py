from mongoengine import BooleanField, EmbeddedDocument, StringField, DecimalField
from ...common.PressureRecord import PressureType, PressureRecord


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

    def set(self):
        rec = PressureRecord("")
        if self.pressure_type == "PLAIN":
            rec.pressure_type = PressureType.PLAIN
        else:
            rec.pressure_type = PressureType.MBAR

        rec.valid = self.valid
        rec.pressure = self.pressure
        return rec
