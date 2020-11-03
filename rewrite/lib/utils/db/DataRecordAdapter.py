from ...common.DataRecord import DataRecord
from mongoengine import BooleanField, EmbeddedDocument, StringField


class DataRecordAdapter(EmbeddedDocument):
    """
    Adapter class for the data record.
    Basically just a string wrapper.
    """

    msg = StringField()

    @staticmethod
    def get(rec):
        """
        Create a DataRecordAdapter from a DataRecord

        :param rec:  DataRecord to convert
        """
        return DataRecordAdapter(msg=rec)

    def createData(self):
        """
        Converts the current object to a DataRecord

        :returns: DataRecord from the current DataRecordAdapter
        """
        return DataRecord(self.msg)
