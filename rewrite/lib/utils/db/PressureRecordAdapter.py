from mongoengine import BooleanField, EmbeddedDocument, StringField, DecimalField
from ...common.PressureRecord import PressureType, PressureRecord


class PressureRecordAdapter(EmbeddedDocument):
    """
    Adapter class for the pressure record.


    :param valid (Bool): Validity of the record. Set to True, if the message starts with 'BA'
    :param pressure (Real): Floating point value of in the pressure record
    :param pressure_type (PressureType): Either mBar or plain data
    """
    valid = BooleanField()
    pressure = DecimalField()
    pressure_type = StringField()

    @staticmethod
    def get(rec):
        """
        Create a PressureRecordAdapter from a PressureRecord

        :param rec:  PressureRecord to convert
        """
        t = ""
        if rec.pressure_type == PressureType.PLAIN:
            t = "PLAIN"
        else:
            t = "MBAR"
        return PressureRecordAdapter(valid=rec.valid, pressure=rec.pressure, pressure_type=t)

    def createPressure(self):
        """
        Converts the current object to a PressureRecord

        :returns: PressureRecord from the current PressureRecordAdapter
        """
        rec = PressureRecord("")
        if self.pressure_type == "PLAIN":
            rec.pressure_type = PressureType.PLAIN
        else:
            rec.pressure_type = PressureType.MBAR

        rec.valid = self.valid
        rec.pressure = self.pressure
        return rec
