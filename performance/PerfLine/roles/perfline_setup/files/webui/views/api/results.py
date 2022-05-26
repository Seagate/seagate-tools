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
from flask import make_response

from app_global_data import cache, app, artifacts_dirs, \
    backup_artifacts_dirs, all_artif_dirs

from core.utils import tq_task_common_get


def tq_results_read(limit, locations_list=None):

    cache.update(all_artif_dirs)
    results = cache.get_tasks(limit, locations=locations_list)
    out = []

    for r in results:
        elem = {}
        try:
            if len(r) < 3:
                continue

            info = r[2]

            tq_task_common_get(elem, r)

            elem["status"] = info['info']['status']
            task = r[0]

            perf_results = cache.get_perf_results(elem["task_id"])

            if not perf_results:
                perf_results = [{'val': 'N/A'}]

            elem['perf_metrics'] = perf_results

            elem['artifacts'] = {
                "artifacts_page": "artifacts/{0}".format(task['task_id']),
            }

            elem['perfagg'] = {
                "report_page": "report/{0}".format(task['task_id']),
            }
            elem['perfline_logs'] = {
                "log": "log/{0}".format(task['task_id']),
            }
        except Exception as e:
            print("exception: " + str(e))

        out.append(elem)

    return out



def create_response(limit, locations):
    data = {
        "results": tq_results_read(limit, locations)
    }
    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


@app.route('/api/results', defaults={'limit': 9999999})
@app.route('/api/results/<int:limit>')
def results(limit=9999999):
    return create_response(limit, artifacts_dirs)


@app.route('/api/backup_results', defaults={'limit': 9999999})
@app.route('/api/backup_results/<int:limit>')
def backup_results(limit=9999999):
    return create_response(limit, backup_artifacts_dirs)
