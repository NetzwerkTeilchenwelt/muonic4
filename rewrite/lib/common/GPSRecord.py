class GPSRecord():
    def __init__(self, GPSDateTime, Status, PosFix, Latitude, Longitude, Altitude, NSats, PPSDelay, FPGATime, ChkSumErr):

        self.GPSDateTime = GPSDateTime.decode('utf-8')
        self.Status = Status.decode('utf-8')
        self.PosFix = PosFix.decode('utf-8')
        self.Latitude = Latitude.decode('utf-8')
        self.Longitude = Longitude.decode('utf-8')
        self.Altitude = Altitude.decode('utf-8')
        self.NSats = NSats.decode('utf-8')
        self.PPSDelay = PPSDelay.decode('utf-8')
        self.FPGATime = FPGATime.decode('utf-8')
        self.ChkSumErr = ChkSumErr.decode('utf-8')

    def __repr__(self):
        return f"{self.GPSDateTime}, {self.Status}, {self.PosFix}, {self.Latitude}, {self.Longitude}, {self.Altitude}, {self.NSats}, {self.PPSDelay}, {self.FPGATime}, {self.ChkSumErr} "

    __str__ = __repr__