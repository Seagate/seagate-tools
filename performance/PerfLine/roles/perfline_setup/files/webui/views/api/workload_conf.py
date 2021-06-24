# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import json
import gzip
from flask import make_response, jsonify

from app_global_data import *
from core.utils import get_list_of_files


@app.route('/api/task/<string:task>')
def loadtask(task: str):
    files = get_list_of_files(WORKLOAD_DIR)
    try:
        with open(files[task], "r") as f:
            data = {
                "task": "".join(f.readlines())
            }
    except FileNotFoundError:
        return jsonify({"data": ""})

    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response
