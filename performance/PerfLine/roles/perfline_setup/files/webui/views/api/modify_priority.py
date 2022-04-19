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
from flask import make_response

from app_global_data import *

from core import pl_api

@app.route('/api/priority/update/<string:taskList>/<int:prio>')
def updatePriority(taskList: str, prio: int):
    status = {}
    status_of_tasklist = {}
    for taskid in list(taskList.split(",")):
        status = pl_api.put_prio(taskid, prio)
        status_of_tasklist[taskid] = status
    response = make_response(json.dumps(status_of_tasklist, indent = 4))
    return response