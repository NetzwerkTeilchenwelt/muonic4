from mongoengine import BooleanField, EmbeddedDocument, DecimalField


class TemperatureRecordAdapter(EmbeddedDocument):
    valid = BooleanField()
    temperature = DecimalField()

    @staticmethod
    def get(rec):
        return TemperatureRecordAdapter(
            valid=rec.valid, temperature=rec.temperature)
