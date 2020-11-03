
class DataRecord():
    """
    Record to hold a DataRecords from the DAQ card. Basically just a string wrapper.
    """

    msg = ""

    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg
    __str__ = __repr__
