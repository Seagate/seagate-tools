
from pprint import pformat

import ctperrors as ctper




class CTPException(Exception):
    """
    Exception class for CTP failures.
    """

    def __init__(self, ctp_error, msg, **kwargs):
        """
        Create a CTPException.

        :param ctp_error: CTPError object.
        :param msg      : String error message from user.
        :param **kwargs : All other keyword arguments will be stored in self.kwargs.
        :raises TypeError: If ctp_error is not a CTPError object.
        """
        if not isinstance(ctp_error, ctper.CTPError):
            raise TypeError("'ctp_error' has to be of type 'CTPError'!")

        self.ctp_error = ctp_error
        self.message = msg
        self.kwargs = kwargs  # Dictionary of 'other' information

    def __str__(self):
        """
        Return human-readable string representation of this exception
        """
        return "CTPException: EC({})\nError Desc: {}\nError Message: {}\nOther info:\n{}".format(self.ctp_error.code,
                                                                                                 self.ctp_error.desc,
                                                                                                 self.message,
                                                                                                 pformat(self.kwargs))


class CTPExceptionFailedDevs(CTPException):
    """
    Exception class for CTP failures with failed devices.
    """

    def __init__(self, ctp_error, msg, devices, **kwargs):
        """
        Create a CTPExceptionFailedDevs.

        :param ctp_error: CTPError object.
        :param msg      : String error message from user.
        :param **kwargs : All other keyword arguments will be stored in self.kwargs.
        :param devices   : Failed device / list of failed devices.
        :raises TypeError: If ctp_error is not a CTPError object.
        """
        super(CTPExceptionFailedDevs, self).__init__(ctp_error, msg, **kwargs)
        self.devices = devices
        if not isinstance(devices, (list, tuple)):
            self.devices = [devices]

    def __str__(self):
        """
        Return human-readable string representation of this exception
        """
        return super(CTPExceptionFailedDevs, self).__str__() + "\nDevices: {}".format(self.devices)


def report_ctp_error(err_object, err_msg, devices=None):
    if devices is not None:
        raise CTPExceptionFailedDevs(err_object, err_msg, devices)
    else:
        raise CTPException(err_object, err_msg)
