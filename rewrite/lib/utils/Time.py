from dateutil import tz
import datetime

def getLocalTime():
    #utcTime = datetime.datetime.utcnow()

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.datetime.utcnow()

    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)

def getTimeString(time):
    return f"{time}"[:-5]

def getCurrentTimeString():
    return datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")
    # return getTimeString(getLocalTime())