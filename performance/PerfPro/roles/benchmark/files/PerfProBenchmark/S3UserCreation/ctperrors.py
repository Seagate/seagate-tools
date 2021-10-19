"""
CTP error codes and descriptions

Provides an error data object to contain the error code and description.
The error object is in the format: NAME_OF_ERROR(code, description).

Helper functions:
    - get_error(): Searches through this module to find error objects based on the provided code or description.
    - validate_ctp_errors(): Checks for duplicate error codes and missing error descriptions.
        If implemented at the end it will validate the codes at runtime. (TBD)
"""

import sys

if sys.version >= '3.7':
    # Use dataclass decorator if running Python 3.7 or newer.
    from dataclasses import dataclass

    @dataclass
    class CTPError:
        code: int
        desc: str
else:
    class CTPError(object):
        def __init__(self, code, desc):
            self.code = code
            self.desc = desc

        def __str__(self):
            return "{}{}".format(self.__class__.__name__, self.__dict__)


def get_error(info):
    """ Retrieve an error from a provided error code or error description.

    :param info: Error code (int) or message (str) needed to search with.
    :return: The corresponding error or None.
    """
    gl = globals().copy()
    for _, vi in gl.items():
        if isinstance(vi, CTPError):
            if (isinstance(info, int) and info == vi.code) \
                    or (isinstance(info, str) and info.lower() in vi.desc.lower()):
                return vi
    return


def validate_ctp_errors(code=None):
    """ Validate all CTP errors by checking error codes and descriptions.
    Check if an error code is already used for a different error.
    Check if an error is missing its description.
    If no code is provided it will go through all the errors in the file and compare the codes.

    :param code: Error code (int) to validate.
    :return: Nothing if no error code is provided.
    :return: True if the code is not used. False if it is already used by a different error.
    :raises Exception: If an error code is used in more than one error.
    """
    gl = globals().copy()
    if code is None:
        for i, vi in gl.items():
            if not isinstance(vi, CTPError):
                continue
            if vi.desc is None or vi.desc == '':
                raise Exception("{}({}): Error description cannot be empty!"
                                .format(i, vi.code))
            for j, vj in gl.items():
                if i == j:
                    continue
                if isinstance(vj, CTPError) and vj.code == vi.code:
                    raise Exception("{} is duplicate error code for {} and {}"
                                    .format(vj.code, i, j))
    else:
        for _, vi in gl.items():
            if isinstance(vi, CTPError) and vi.code == code:
                return False
        return True


# List of errors below this line
# Test Case Errors
TEST_FAILED = CTPError(1, "Test Failed")
MISSING_PARAMETER = CTPError(2, "Missing Parameter")
INVALID_PARAMETER = CTPError(3, "Invalid Parameter")

# CTP Errors
CTP_CONFIG_ERROR = CTPError(1000, "CTP Config Error")

# HTTP and HTTPS Errors
HTTP_ERROR = CTPError(22000, "HTTP Error")
HTTP_CONNECTION_ERROR = CTPError(22001, "HTTP Connection Error")
HTTP_CONNECTION_REFUSED = CTPError(22002, "HTTP Connection Refused")
HTTP_LOGIN_FAILED = CTPError(22003, "HTTP Authentication Unsuccessful")
HTTP_BAD_RESPONSE = CTPError(22004, "HTTP Bad Response")
HTTP_INVALID_SESSION_KEY = CTPError(22005, "HTTP Invalid Session Key")
HTTP_READ_TIMEOUT = CTPError(22006, "HTTP Read Timeout Error")
HTTP_CHUNKED_ENC_ERROR = CTPError(22007, "HTTP Chunked Encoding Error")
HTTP_FORBIDDEN = CTPError(22008, "HTTP Forbidden")
HTTP_STATUS_FAILED = CTPError(22009, "HTTP Response Status Failed")
HTTP_TYPE_CAST = CTPError(22010, "HTTP type cast applied")

INVALID_DEVICE = CTPError(23000, "Invalid device")
INVALID_LOG_DIR = CTPError(23001, "Invalid log directory")
DUPLICATE_LOG_DIR = CTPError(23002, "Duplicate log directory")
INVALID_TEST = CTPError(23003, "Invalid test")
INVALID_PATH = CTPError(23004, "Path does not exist")
INVALID_INPUT = CTPError(23005, "Invalid input parameters")

# CLI Errors
CLI_ERROR = CTPError(24000, "CLI Error")
CLI_INVALID_COMMAND = CTPError(24001, "CLI Invalid Command")
CLI_INVALID_ACCESS_METHOD = CTPError(24002, "CLI Invalid Access Method")
CLI_COMMAND_FAILURE = CTPError(24003, "CLI Command Failure")
CLI_CONTROLLER_NOT_READY = CTPError(24004, "CLI Controller Not Ready")
CLI_NETWORK_VALIDATION_ERROR = CTPError(24005, "CLI Network Validation Error")
CLI_INVALID_NETWORK_PARAMETER = CTPError(24006, "CLI Invalid Network Parameter")
CLI_SYSTEM_NOT_READY = CTPError(24007, "CLI System Not Ready")
CLI_SYSTEM_CHECK_MISSING_PARAMETER = CTPError(24008, "CLI System Check Missing Parameter")
CLI_STATUS_FAILED = CTPError(24009, "CLI Response Status Failed")
CLI_LOGIN_FAILED = CTPError(24010, "CLI Authentication Unsuccessful")
CLI_MC_NOT_READY = CTPError(24011, "CLI MC Not Ready")
CLI_CONTROLLER_CHECK_MISSING_PARAMETER = CTPError(24012, "CLI Controller Check Missing Parameter")
CLI_COMMAND_TIMEOUT = CTPError(24013, "CLI Command Timeout")


# File operation errors
FILE_IO_ERROR = CTPError(77000, "File read-write operation failed")
FILE_NOT_FOUND = CTPError(77001, "File not found")

# BMC TIME SETUP ERRORS
BMC_TIME_SETUP_MODE_ERROR = CTPError(78001, "BMC Time Setup Select Mode Error")
BMC_TIME_SETUP_RESULT_ERROR = CTPError(78002, "BMC Time Setup Result Error")

# MFG Uses 80000-89999

# Channel Uses 90000-90999

# DVT Uses 91000-94999

# SRT Uses 95000-95999



UNKNOWN_ERROR = CTPError(99999, "Unknown error")

# End of CTPError objects. No implementation beyond this point.
# Validate all error codes listed above.
validate_ctp_errors()
