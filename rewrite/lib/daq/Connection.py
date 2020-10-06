


class BaseDAQConnection(metaclass=object):
    
    """
    Base DAQ Connection class.

    Raises SystemError if serial connection cannot be established.

    :param logger: logger object
    :type logger: logging.Logger
    :raises: SystemError
    """