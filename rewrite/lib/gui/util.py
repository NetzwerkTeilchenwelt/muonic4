class WrappedFile(object):
    """
    A file wrapper which keeps track of open files.

    Raises ValueError if filename is None.

    :param filename: the filename
    :type filename: str
    :raises: ValueError
    """
    open_files = set()

    def __init__(self, filename):
        if filename is None:
            raise ValueError("filename cannot be of 'NoneType'")

        self._filename = filename
        self._file = None

    def get_filename(self):
        """
        Get the filename

        :returns: str
        """
        return self._filename

    def open(self, mode='w'):
        """
        Open file and track it.

        :param mode: the file mode
        :type mode: str
        :returns: None
        """
        self._file = open(self._filename, mode)
        WrappedFile.open_files.add(self._filename)
        return self

    @property
    def closed(self):
        """
        Returns True if the file is closed, False otherwise.

        :returns: bool
        """
        if self._file is None:
            return True
        return False

    def close(self):
        """
        Close file and un-track it.

        Raises IOError if file is not open.

        :raises: IOError
        :returns: None
        """
        if self._file is None:
            raise IOError("file '%s' is not open" % self._filename)
        self._file.close()
        self._file = None
        WrappedFile.open_files.remove(self._filename)

    def __enter__(self):
        """
        Return file on entering 'with' block

        :returns: file
        """
        return self._file

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close file on leaving 'with' block.

        Exit the runtime context related to this object. The parameters
        describe the exception that caused the context to be exited. If
        the context was exited without an exception, all three arguments
        will be None.

        :param exc_type: type of the Exception that caused the
        context to be exited
        :param exc_value: value of the Exception
        :param traceback: traceback, if any
        :returns: None
        """
        self.close()

    def __getattr__(self, attr):
        """
        Proxy all other attributes of file.

        Raises IOError if file is not open.

        :param attr: attribute name
        :type attr: str
        :raises: IOError
        :returns: mixed
        """
        if self._file is None:
            raise IOError("file '%s' is not open" % self._filename)
        return getattr(self._file, attr)

    def __repr__(self):
        """
        Representation

        :returns: str
        """
        return self._filename

    @staticmethod
    def get_open_files():
        """
        Get all open files.

        :returns: set of str
        """
        return WrappedFile.open_files

