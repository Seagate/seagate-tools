#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-


import sys
import json
import requests
import warnings

# Turn off ssl related python warnings
# -------------------------------------
warnings.filterwarnings('ignore')

# Cluster Details
# ----------------
# url='https://eos-mgmt-vip-131.colo.seagate.com'
url = f'https://{sys.argv[1]}'
node_id = sys.argv[2]
adminusr = 'cortxadmin'
adminpwd = 'Cortxadmin@123'

# API Locations
# --------------
api_login = '/api/v2/login'
api_cluster_status = '/api/v2/system/management/cluster_status'
api_cluster = '/api/v2/system/management/cluster'
api_node = '/api/v2/system/management/node'
api_service = '/api/v2/system/management/service'

# Requesting AuthToken
# ---------------------
print('\nRequest => Auth Token')
api_url = f'{url}{api_login}'
# print(f'{api_url}')
response = requests.post(
    api_url, data={'username': adminusr, 'password': adminpwd}, verify=True)
authToken = response.headers["Authorization"]
print(f'Response => {response.status_code} : {authToken}')

# Requesting cluster status
# --------------------------
print('\nRequest => Cluster status')
api_url = f'{url}{api_cluster_status}/{node_id}'
# print(f'URL={api_url}')
response = requests.get(api_url, verify=True,  headers={
                        'Authorization': authToken})
if response.status_code == 200 and response.json()['status'] == "ok":
    print(f'Response => {response.status_code} : {response.json()}')
    print('Skipping to start node! Cluster is already healthy, Node must be already up')
    sys.exit(0)

# Requesting node start
# ----------------------
print('\nRequest => node start')
params = {"operation": "start", "arguments": {"resource_id": f"{node_id}"}}
params = json.dumps(params)
# print(f'Data={params}')
api_url = f"{url}{api_node}"
# print(f'URL={api_url}')
response = requests.post(api_url, verify=True, headers={
                         "Authorization": authToken, "Content-Type": "application/json"}, data=params)
print(f'Response => {response.status_code} : {response.json()}')
