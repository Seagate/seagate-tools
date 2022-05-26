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
import csv
from flask import make_response, request

from app_global_data import app, cache


def find_fields_indexes(csv_header):
    max_index = len(csv_header) - 1
    first_read_metric_index = None
    last_read_metric_index = max_index

    last_read_metric_name = csv_header[max_index]

    first_write_metric_index = None
    last_write_metric_index = None

    for index in range(max_index - 1, 0, -1):
        metric = csv_header[index]

        if metric == last_read_metric_name:
            last_write_metric_index = index
            first_read_metric_index = index + 1
            metrics_nr = last_read_metric_index - first_read_metric_index
            first_write_metric_index = last_write_metric_index - metrics_nr
            break

    return first_write_metric_index, first_read_metric_index


def parse_csv(task_id):
    task_location = cache.get_location(task_id) + f'/result_{task_id}'
    csv_file = f'{task_location}/client/s3bench_report.csv'

    with open(csv_file, newline='') as csvfile:
        header = None
        obj_size_index = None
        num_clients_index = None
        num_samples_index = None
        benchmarks = list()

        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if header is None:
                header = row
                obj_size_index = header.index('objectSize (MB)')
                num_clients_index = header.index('numClients')
                num_samples_index = header.index('numSamples')
                w_start, r_start = find_fields_indexes(header)
                continue

            workload = f'Object size: {row[obj_size_index]}Mb, Clients: {row[num_clients_index]}, Samples: {row[num_samples_index]}'
            metrics = dict()

            for i in range(w_start, r_start):
                metric_name = f'(W) {header[i]}'
                metrics[metric_name] = row[i]

            for i in range(r_start, len(header)):
                metric_name = f'(R) {header[i]}'
                metrics[metric_name] = row[i]

            benchmarks.append({'workload': workload, 'metrics': metrics})

    return benchmarks


@app.route('/api/get_perf_metrics')
def get_perf_metrics():
    task_ids = request.args.getlist('task_id')

    if len(task_ids) == 0:
        return make_response("task_id parameter not found", 400)

    data = list()

    for task_id in task_ids:
        try:
            benchmarks = parse_csv(task_id)
            data.append({"task_id": task_id, "benchmarks": benchmarks})
        except Exception as e:
            print(f'error: {e}')

    if len(data) == 0:
        return make_response("data not found", 404)

    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response
