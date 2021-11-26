"""Test library for s3 account operations."""

import time
import eos_errors as err
from ctpexception import CTPException
from csm_rest_test_lib import RestTestLib as Base

class RestS3account(Base):
    """RestS3account contains all the Rest Api calls for s3 account operations"""

    def __init__(self,account_name,account_email,password):
        super(RestS3account, self).__init__()
        self.recently_created_s3_account_user = None
        self.recent_patch_payload = None
        self.user_type = ("duplicate","newuser")
        self.account_name=account_name
        self.account_email=account_email
        self.password=password

    @Base.authenticate_and_login
    def create_s3_account(self, user_type, save_new_user=False):
        """
        This function will create new s3 account user
        :param user_type: type of user required
        :param save_new_user: to store newly created user to config
        :return: response of create user
        """
        try:
            # Building request url
            endpoint = self.config["s3accounts_endpoint"]

            # Collecting required payload to be added for request
            user_data = self.create_payload_for_new_s3_account(user_type)

            self.recently_created_s3_account_user = user_data
            if save_new_user:
                self.update_csm_config_for_user(
                    "new_s3_account_user", user_data["account_name"], user_data["password"])

            # Fetching api response
            return self.restapi.rest_call(
                "post", endpoint=endpoint, data=user_data, headers=self.headers)

        except BaseException as error:
            raise CTPException(
                err.CSM_REST_AUTHENTICATION_ERROR, error.args[0])

    def create_payload_for_new_s3_account(self, user_type):
        """
        This function will create payload according to the required type
        :param user_type: type of payload required
        :return: payload
        """
        try:
            # Creating payload for required user type
            # Creating s3accounts which are pre-defined in config
            if user_type == "duplicate":
                # creating new user to make it as duplicate
                self.create_s3_account()
                return self.recently_created_s3_account_user

            if user_type == "newuser":
                return {"account_name": self.account_name,
                        "account_email": self.account_email,
                        "password": self.password}
                        
            user_data = {"account_name": user_name,
                         "account_email": email_id,
                         "password": self.config["test_s3account_password"]}

            return user_data
        except Exception as error:
            raise CTPException(err.CSM_REST_VERIFICATION_FAILED, error.args[0])

    