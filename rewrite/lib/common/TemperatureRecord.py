

class TemperatureRecord():
    """
    Holds Temperature information

    incoming format: TH TH=22.2
    """

    def __init__(self, msg):
        self.msg_bak = msg
        if msg != None:
            counter_from_msg = msg.split()
            self.valid = True
        else:
            self.valid = False
            return
        if not msg.startswith('TH'):
            self.valid = False
            return

        self.temperature = float(msg.split("=")[1])

    def __repr__(self):
        if self.valid:
            return f"{self.temperature}"
        return ""
    __str__ = __repr__
