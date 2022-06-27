#!/usr/bin/env python3

import sys
import json
import requests
import warnings
import yaml

# Turn off ssl related python warnings
# -------------------------------------
warnings.filterwarnings('ignore')

# Cluster Details
# ----------------
Config_path = '/root/PerfProBenchmark/config.yml'
url = f'https://{sys.argv[1]}:31169'


def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_config = makeconfig(Config_path)
admin_user = configs_config.get('ADMIN_USER')
admin_passwd = configs_config.get('ADMIN_PASSWD')
s3_account = configs_config.get('S3_ACCOUNT')
account_passwd = configs_config.get('ACCOUNT_PASSWD')
email = configs_config.get('EMAIL')
access_key = configs_config.get('ACCESS_KEY')
secret_key = configs_config.get('SECRET_KEY')


# API Locations
# --------------
api_login = '/api/v2/login'
api_s3user = '/api/v2/s3_accounts'
api_logout = '/api/v2/logout'

ansible_response = dict()

# Requesting Admin Login
# ----------------------
api_url = f'{url}{api_login}'
params = {'username': admin_user, 'password': admin_passwd}
params = json.dumps(params)

response = requests.post(api_url, data=params, verify=True)
authToken = response.headers["Authorization"]
if response.status_code != 200:
    ansible_response["status"] = response.status_code
    print(json.dumps(ansible_response))
    sys.exit(0)


# Requesting s3 user creation
# ---------------------------
api_url = f"{url}{api_s3user}"
params = {"account_name": s3_account, "password": account_passwd,
          "account_email": email, "access_key": access_key, "secret_key": secret_key}
params = json.dumps(params)
response = requests.post(api_url, verify=True, headers={
                         "Authorization": authToken, "Content-Type": "application/json"}, data=params)
ansible_response["status"] = response.status_code
if response.status_code == 201:
    ansible_response["access"] = response.json()["access_key"]
    ansible_response["secret"] = response.json()["secret_key"]
print(json.dumps(ansible_response))

# Requesting Admin Logout
# -----------------------
api_url = f'{url}{api_logout}'
response = requests.post(api_url, verify=True, headers={
                         'Authorization': authToken})
