#!/usr/bin/env python3

import sys
import json
import requests
import warnings

# Turn off ssl related python warnings
# -------------------------------------
warnings.filterwarnings('ignore')

# Cluster Details
# ----------------
url = f'https://{sys.argv[1]}:31169'
adminusr = 'cortxadmin'
adminpwd = 'Cortxadmin@123'
s3account = 'perfpro'
password = "Seagate@1"
email = "perfpro@seagate.com"
access_key = "AKIA_KN5IwWHRsqgHI9qUA0kuQ"
secret_key = "+yk3nsSwVDhIqybtEmUaWkD+ypcHsGcZnWKMxYBS"

# API Locations
# --------------
api_login = '/api/v2/login'
api_s3user = '/api/v2/s3_accounts'
api_logout = '/api/v2/logout'

ansible_response = dict()

# Requesting Admin Login
# ----------------------
api_url = f'{url}{api_login}'
params = {'username': adminusr, 'password': adminpwd}
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
params = {"account_name": s3account, "password": password,
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
