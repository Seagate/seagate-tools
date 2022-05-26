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

import os
from os.path import isdir, join, isfile
from flask import send_file

from app_global_data import report_resource_map, app, cache


# TODO: check if this function really needed and delete this bad code!
def define_path_for_report_imgs(tid, location):
    path_to_stats = f'{location}/result_{tid}/stats'
    path_to_workload = f'{location}/result_{tid}/client'
    path_to_m0crate_logs = f'{location}/result_{tid}/m0crate'
    nodes_stat_dirs = [join(path_to_stats, f) for f in os.listdir(
        path_to_stats) if isdir(join(path_to_stats, f)) and not "addb" in f]

    workload_files = {}

    if isdir(path_to_workload):
        workload_files.update({f: join(path_to_workload, f) for f in os.listdir(
            path_to_workload) if isfile(join(path_to_workload, f))})

    if isdir(path_to_m0crate_logs):
        for dir_path, _, files in os.walk(path_to_m0crate_logs):
            m0crate_logs_filtered = filter(lambda f_name: f_name.endswith('.log'), files)

            for f in m0crate_logs_filtered:
                workload_files[f] = join(dir_path, f)

    iostat_aggegated_imgs = [
        f'{path}/iostat/iostat.aggregated.png' for path in nodes_stat_dirs]

    iostat_detailed_imgs = {
        'io_rqm': [f'{path}/iostat/iostat.io_rqm.png' for path in nodes_stat_dirs],
        'svctm': [f'{path}/iostat/iostat.svctm.png' for path in nodes_stat_dirs],
        'iops': [f'{path}/iostat/iostat.iops.png' for path in nodes_stat_dirs],
        'await': [f'{path}/iostat/iostat.await.png' for path in nodes_stat_dirs],
        '%util': [f'{path}/iostat/iostat.%util.png' for path in nodes_stat_dirs],
        'avgqu-sz': [f'{path}/iostat/iostat.avgqu-sz.png' for path in nodes_stat_dirs],
        'avgrq-sz': [f'{path}/iostat/iostat.avgrq-sz.png' for path in nodes_stat_dirs],
        'io_transfer': [f'{path}/iostat/iostat.io_transfer.png' for path in nodes_stat_dirs]
    }

    blktrace_imgs = []
    for path in nodes_stat_dirs:
        if isdir(f'{path}/blktrace'):
            agg_img = next((f'/blktrace/{f}' for f in os.listdir(
                f'{path}/blktrace') if 'node' in f and 'aggregated' in f), None)
            if agg_img:
                blktrace_imgs.append(path + agg_img)

    report_resource_map[tid] = {
        'iostat': iostat_aggegated_imgs,
        'blktrace': blktrace_imgs,
    }
    report_resource_map[tid].update(iostat_detailed_imgs)
    report_resource_map[tid]['workload_files'] = workload_files


@app.route('/report/<string:tid>')
def report(tid=None):
    location = cache.get_location(tid)
    path_to_report = f'{location}/result_{tid}/report_page.html'

    if not os.path.isfile(path_to_report):
        return 'Report was not generated for this workload'

    with open(path_to_report, 'r') as report_file:
        report_html = report_file.read()

    define_path_for_report_imgs(tid, location)
    return report_html


@app.route('/report/css')
def report_css():
    return send_file('styles/report.css', mimetype='text/css')
