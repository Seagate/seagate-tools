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

from flask import send_from_directory, make_response

from app_global_data import app, cache

@app.route('/log/<uuid:task_id>/<path:subpath>')
@app.route('/artifacts/<uuid:task_id>/<path:subpath>')
def get_artifact(task_id, subpath):
    task_id = str(task_id)

    if cache.has(task_id):
        location = cache.get_location(task_id)
        path = 'result_{0}/{1}'.format(task_id, subpath)
        return send_from_directory(location + '/', path)
    else:
        return make_response('not found', 404)
