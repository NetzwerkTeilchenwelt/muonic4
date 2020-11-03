from ...common.TemperatureRecord import TemperatureRecord
from mongoengine import BooleanField, EmbeddedDocument, DecimalField


class TemperatureRecordAdapter(EmbeddedDocument):
    """
    Adapter class for the temperature record.

    :param valid (Bool): Validity of the record. Set to True, if the message starts with 'TH'
    :param temperature (Real): The temperature of the record.
    """
    valid = BooleanField()
    temperature = DecimalField()

    @staticmethod
    def get(rec):
        """
        Create a TemperatureRecordAdapter from a TemperatureRecord

        :param rec:  TemperatureRecord to convert
        """
        return TemperatureRecordAdapter(
            valid=rec.valid, temperature=rec.temperature)

    def createTemperature(self):
        """
        Converts the current object to a TemperatureRecord

        :returns: TemperatureRecord from the current TemperatureRecordAdapter
        """
        rec = TemperatureRecord("")
        rec.valid = self.valid
        rec.temperature = self.temperature
        return rec
