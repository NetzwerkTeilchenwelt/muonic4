from ...common.TemperatureRecord import TemperatureRecord
from mongoengine import BooleanField, EmbeddedDocument, DecimalField


class TemperatureRecordAdapter(EmbeddedDocument):
    valid = BooleanField()
    temperature = DecimalField()

    @staticmethod
    def get(rec):
        return TemperatureRecordAdapter(
            valid=rec.valid, temperature=rec.temperature)

    def set(self):
        rec = TemperatureRecord("")
        rec.valid = self.valid
        rec.temperature = self.temperature
        return rec
