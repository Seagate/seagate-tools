#!/usr/bin/env python3
#
#
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
