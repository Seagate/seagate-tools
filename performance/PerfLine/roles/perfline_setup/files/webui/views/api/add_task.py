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

from flask import make_response, request

from app_global_data import *
from core import pl_api
import yaml

@app.route('/addtask', methods = ["POST"])
def addtask():
    config: str = request.form['config']
    config1 = yaml.safe_load(config)
    prio = config1['common']['priority']

    if HIGHEST_WEBUI_PRIO < prio or prio < LOWEST_PRIO:
        result = { 'PRIORITY': f'Too high priority are not allowed. Please use between {LOWEST_PRIO} to {HIGHEST_WEBUI_PRIO}' }
    else:
        result = pl_api.add_task(config)
    response = make_response(f'{result}')
    return response
