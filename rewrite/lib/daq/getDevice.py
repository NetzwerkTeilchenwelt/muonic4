def get_Device():
    """
    Reads dmesg and searches for the daq card. Then returns its name. 

    returns ttyUSB0 by default

    :returns: name of the device file in /dev/ or ttyUSB0 by default
    """
    with open("/var/log/syslog", "r") as f:
        for line in f: 
            if "cp210x" in line and "now attached to" in line: 
                return line.split()[-1]

    return "ttyUSB0"            