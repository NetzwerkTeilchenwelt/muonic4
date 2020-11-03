
class CountRecord():
    """
    Holds the counting information

    incoming format:
    DS S0=00000000 S1=00000000 S2=00000000 S3=00000000 S4=00000000 S5=18531FFD


    :param valid (Bool): validity of the record. Will be set to True if the message starts with 'DS'
    :param counts_ch[X] (int): Counts in channel X
    :param counts_trigger (int): trigger counts recieved
    :param counts_time (Real): the time of the record
    """

    def __init__(self, msg):
        self.msg_bak = msg
        if msg != None:
            counter_from_msg = msg.split()
            self.valid = True
        else:
            self.valid = False
            return
        if not msg.startswith('DS'):
            self.valid = False
            return

        for item in counter_from_msg:
            if ("S0" in item) & (len(item) == 11):
                self.counts_ch0 = int(item[3:], 16)
            elif ("S1" in item) & (len(item) == 11):
                self.counts_ch1 = int(item[3:], 16)
            elif ("S2" in item) & (len(item) == 11):
                self.counts_ch2 = int(item[3:], 16)
            elif ("S3" in item) & (len(item) == 11):
                self.counts_ch3 = int(item[3:], 16)
            elif ("S4" in item) & (len(item) == 11):
                self.counts_trigger = int(item[3:], 16)
            elif ("S5" in item) & (len(item) == 11):
                self.counters_time = float(int(item[3:], 16))
    # def __str__(self):
    #     return f"ch0: {self.counts_ch0} ch1: {self.counts_ch1} ch2: {self.counts_ch2} ch3: {self.counts_ch3} trigger: {self.counts_trigger} time: {self.counters_time}"

    def __repr__(self):
        if not self.valid:
            return ""
        try:
            return f"ch0: {self.counts_ch0} ch1: {self.counts_ch1} ch2: {self.counts_ch2} ch3: {self.counts_ch3} trigger: {self.counts_trigger} time: {self.counters_time}"
        except:
            print(f"__repr__ error msg was: {self.msg_bak}")
            raise IOError

    __str__ = __repr__


if __name__ == "__main__":
    c = CountRecord(
        "DS S0=00000000 S1=00000000 S2=00000000 S3=00000000 S4=00000000 S5=18531FFD")
    print(repr(c))
