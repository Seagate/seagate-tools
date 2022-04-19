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
import yaml
from flask import make_response

from app_global_data import *
from core import pl_api
from core.utils import tq_task_common_get


def tq_queue_read(limit: int):
    lines = pl_api.get_queue().split('\n')[-limit:]
    lines = filter(None, lines)  # remove empty line

    out = []
    results = [yaml.safe_load(line) for line in lines]

    for r in results:
        elem = {}
        try:
            state = r[1]
            tq_task_common_get(elem, r)
            elem["state"] = state['state']
        except Exception as e:
            print(e)

        out.append(elem)

    return out


@app.route('/api/queue', defaults={'limit': 9999999})
@app.route('/api/queue/<int:limit>')
def queue(limit=9999999):
    data = {
        "queue": tq_queue_read(limit)
    }
    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response
