from enum import Enum

class PressureType(Enum):
    """
    Type of measured pressure. Plaindata or mBar
    """
    PLAIN = 0
    MBAR = 1

class PressureRecord():
    """
    Holds Pressure information

    incoming format: 'BA 1495'
    or: "mBar now reads  = 1015.0  (use cmd 'SA' when done)"

    """

    def __init__(self, msg):
        self.msg_bak = msg
        if msg != None:
            counter_from_msg = msg.split()
            self.valid = True
        else:
            self.valid = False
            return
        if msg.startswith('BA'):
            self.valid = True
            self.pressure = msg.split()[1]
            self.pressure_type = PressureType.PLAIN
            return
            
        if msg.startswith('mBar'):  
            self.valid = True
            self.pressure = msg.split()[4]
            self.pressure_type = PressureType.MBAR
            return
        
        self.valid = False  
        
    def __repr__(self):
        if self.valid: 
            return f"{self.pressure} {self.pressure_type.name}"
        return ""
    __str__ = __repr__

if __name__ == "__main__":
    p1 = PressureRecord("BA 1495")
    print(p1)
    p2 = PressureRecord("mBar now reads  = 1015.0  (use cmd 'SA' when done)")
    print(p2)