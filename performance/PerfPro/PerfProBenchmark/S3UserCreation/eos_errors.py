"""
Created on Dec 26, 2019

@author: 730728
"""

import sys
import ctperrors as ctperr
from ctperrors import CTPError



class EOSError(CTPError):
    """
    Inherit and extend CTPError in EOSError.
    """
    def __init__(self, code, desc):
        # super().__init__(code, desc)
        self.code = code
        self.desc = desc

    def __str__(self):
        """
        print formatted error code.
        :return: string.
        """
        return "{}{}".format(self.__class__.__name__, self.__dict__)


# ===============================================================================
# def get_errors(info):
#     return errors.get_error(info)
# ===============================================================================


def validate_errors(code=None):
    """
    Validate errors as per code.
    :param code: error code.
    :type code: int.
    :return: Exception.
    :rtype: str.
    """
    return ctperr.validate_ctp_errors(code)

S3_SERVER_ERROR = EOSError(5007, "S3 Server Error")
S3_CLIENT_ERROR = EOSError(4007, "S3 Client Error")
RAS_ERROR = EOSError(6007, "RAS Error")
PROVISIONING_ERROR = EOSError(6001, "Prvsnr Execute Command Failed")
DESTRUCTIVE_ERROR = EOSError(3467, "Destructive tests error")

# CSM common errors
# CSM-CLI errors
CSM_CLI_AUTHENTICATION_ERROR = EOSError(8007, "CSM_CLI Authentication Error")
CSM_CLI_VERIFICATION_FAILED = EOSError(8008, "Unexpected output fetched for CSM-CLI")
CSM_CLI_COMMAND_FAILED = EOSError(8009, "CSM-CLI Execute Command Failed")

# CSM-REST errors
CSM_REST_AUTHENTICATION_ERROR = EOSError(8107, "CSM-REST Authentication Error")
CSM_REST_VERIFICATION_FAILED = EOSError(8108, "Unexpected output fetched for CSM-REST")


