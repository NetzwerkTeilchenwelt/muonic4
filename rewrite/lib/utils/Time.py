from dateutil import tz
import datetime

def getLocalTime():
    #utcTime = datetime.datetime.utcnow()

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.datetime.utcnow()

    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)
