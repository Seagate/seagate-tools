#!/usr/bin/env python
#
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

from flask import Flask, send_from_directory, redirect, \
    render_template, request, json, make_response, jsonify, send_file
import gzip
import yaml
from typing import Dict
from plumbum import local, BG
import datetime
import os
from os.path import isdir, join, isfile
import perf_result_parser
import config
import uuid

from os.path import join

import pandas as pd
import csv
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from core.utils import *
from core import cache, pl_api


app = Flask(__name__)
git = local["git"]
hostname = local["hostname"]["-s"]().strip()
logcookies = {}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

report_resource_map = dict()
AGGREGATED_PERF_FILE = '/root/perfline/webui/images/aggregated_perf_{0}.png'


# @app.after_request
# def add_header(resp):
#     resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     resp.headers["Pragma"] = "no-cache"
#     resp.headers["Expires"] = "0"
#     resp.headers["Cache-Control"] = "public, max-age=0"
#     return resp

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


def refresh_performance_img():

    lines = pl_api.get_results().split('\n')
    lines = filter(None, lines)  # remove empty line

    results = [yaml.safe_load(line) for line in lines]

    sizes = ['100k', '1m', '16m', '128m']
    rw_data = {size: (list(), list(), list()) for size in sizes}
    # rw_data = {
    #     '100k': ((list(), list()),
    #             (list(), list()),
    #     '1m': ((list(), list()),
    #             (list(), list()),
    #     '16m': ((list(), list()),
    #             (list(), list()),
    #     '128m': ((list(), list()),
    #             (list(), list()),
    # }
    for r in results:
        try:
            if len(r) < 3:
                continue

            task_descr = r[2]['info']['conf']['common'].get('description')
            task_finish_time = r[2]['info']['finish_time']
            task_id = r[0]['task_id']

            if 'Perf benchmark' not in task_descr:
                continue
            task_descr.split(',')
            size = next(t.strip().split('=')[1] for t in task_descr.split(
                ',') if t.strip().split('=')[0] == 'size')
            if size not in rw_data:
                continue

            rw_file_path = f'/var/perfline/result_{task_id}/rw_stat'
            if isfile(rw_file_path):
                with open(rw_file_path, 'r') as rw_file:
                    rw_info = rw_file.readlines()
                    rw_data[size][0].append(float(rw_info[0].split(' ')[0]))
                    rw_data[size][1].append(float(rw_info[1].split(' ')[0]))
            else:
                continue

            fmt = '%Y-%m-%d %H:%M:%S.%f'
            hms = '%Y-%m-%d %H:%M:%S'
            f = datetime.datetime.strptime(task_finish_time, fmt)

            rw_data[size][2].append(f)
        except Exception as e:
            print("exception: " + str(e))

    print(rw_data)

    for size, data in rw_data.items():
        fig, ax = plt.subplots(1)

        ax.plot(data[2], data[0], label="write")
        ax.plot(data[2], data[1], label="read")
        plt.title(size)
        plt.ylabel('MB/s')
        plt.legend(loc='best')
        fig.autofmt_xdate()
        plt.savefig(AGGREGATED_PERF_FILE.format(size))
        plt.cla()


@app.route('/aggregated_perf_img/<string:size>')
def aggregated_perf_img(size):
    return send_file(AGGREGATED_PERF_FILE.format(size), mimetype='image')


@app.route('/')
def index():
    refresh_performance_img()
    return render_template("index.html")


@app.route('/templates/<path:path>')
def templates(path):
    return send_from_directory('templates', path)

@app.route('/stats/<path:path>')
def stats(path):
    response = send_from_directory('stats', path)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

def get_perf_results(task_id):
    cache_key = f'perf_res_{task_id}'

    if cache.contains(cache_key):
        return cache.get(cache_key)

    perf_results_path = f'{config.artifacts_dir}/result_{task_id}/{config.perf_results_filename}'

    if isfile(perf_results_path):
        result = []

        with open(perf_results_path) as f:
            for line in f:
                line_s = line.strip()
                if line_s:
                    result.append(line_s)
    else:
        result = ['N/A']

    cache.put(cache_key, result)
    return result

def tq_results_read(limit: int) -> Dict:
    lines = pl_api.get_results().split('\n')[-limit:]
    print(lines)
    lines = filter(None, lines)  # remove empty line

    out = []
    results = [yaml.safe_load(line) for line in lines]

    for r in results:
        elem = {}
        try:
            if len(r) < 3:
                continue

            info = r[2]

            tq_task_common_get(elem, r)

            elem["status"] = info['info']['status']
            task = r[0]

            elem['perf_metrics'] = get_perf_results(elem["task_id"])

            elem['artifacts'] = {
                "artifacts_page": "artifacts/{0}".format(task['task_id']),
            }

            elem['perfagg'] = {
                "report_page": "report/{0}".format(task['task_id']),
            }
        except Exception as e:
            print("exception: " + str(e))

        out.append(elem)

    return list(reversed(out))

def tq_queue_read(limit: int) -> Dict:
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

    return list(reversed(out))


@app.route('/api/results', defaults={'limit': 9999999})
@app.route('/api/results/<int:limit>')
def results(limit=9999999):
    data = {
        "results": tq_results_read(limit)
    }
    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


def define_path_for_report_imgs(tid):
    path_to_stats = f'/var/perfline/result_{tid}/stats'
    path_to_workload = f'/var/perfline/result_{tid}/client'
    nodes_stat_dirs = [join(path_to_stats, f) for f in os.listdir(
        path_to_stats) if isdir(join(path_to_stats, f))]

    workload_files = {f: join(path_to_workload, f) for f in os.listdir(
        path_to_workload) if isfile(join(path_to_workload, f))}

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
    path_to_report = f'/var/perfline/result_{tid}/report_page.html'

    if not os.path.isfile(path_to_report):
        return 'Report was not generated for this workload'

    with open(path_to_report, 'r') as report_file:
        report_html = report_file.read()

    define_path_for_report_imgs(tid)
    return report_html


@app.route('/report/css')
def report_css(tid=None):
    return send_file('styles/report.css', mimetype='text/css')


@app.route('/report/<string:tid>/imgs/<string:node_id>/<string:img_type>')
def serve_report_imgs(tid, node_id, img_type):
    imgs_dict = report_resource_map.get(tid)
    print(imgs_dict)
    path_to_img = imgs_dict.get(img_type)[int(node_id)]
    return send_file(path_to_img, mimetype='image/svg+xml' if img_type == 'blktrace' else 'image')

@app.route('/report/<string:tid>/addb_imgs/<string:filename>')
def serve_addb_imgs(tid, filename):
    path_to_img = f'/var/perfline/result_{tid}/stats/addb/{filename}'
    return send_file(path_to_img, mimetype='image')


@app.route('/report/<string:tid>/dstat_imgs/<string:node_id>/<string:img_type>')
def serve_dstat_imgs(tid, node_id, img_type):
    # Easy safe check
    if ':' in img_type or '/' in img_type or '|' in img_type or ';' in img_type:
        return None

    path_to_stats = f'/var/perfline/result_{tid}/stats'
    nodes_stat_dirs = [join(path_to_stats, f) for f in os.listdir(
        path_to_stats) if isdir(join(path_to_stats, f))]

    path_to_img = join(
        nodes_stat_dirs[int(node_id)], 'dstat', img_type + '.png')
    return send_file(path_to_img, mimetype='image')


@app.route('/report/<string:tid>/workload/<string:filename>')
def serve_workload(tid, filename):
    path_to_workload = report_resource_map.get(tid)['workload_files'][filename]
    return send_file(path_to_workload, mimetype='text/plain')


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


@app.route('/api/task/<string:task>')
def loadtask(task: str):
    try:
        with open(f"task_templates/{task}.yaml", "r") as f:
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


@app.route('/addtask', methods=['POST'])
def addtask():
    config: str = request.form['config']
    pl_api.add_task(config)
    return redirect("/#!/queue")


@app.route('/api/log/<string:morelines>')
def getlog(morelines: str):
    cookie = request.cookies.get('logcookie')
    logf = None
    uid = None

    # coookie found and active, log is opened
    if cookie and logcookies.get(cookie):
        logf = logcookies[cookie]
    # no coookie found: open log, seek to its end
    else:
        uid = str(uuid.uuid1())
        logf = open(config.logfile, "r")
        logf.seek(0, os.SEEK_END)
        logcookies.update({uid: logf})

    # if morelines == "true":  # [sigh]
    #     logf.seek(0, os.SEEK_END)
    #     logf.seek(logf.tell() - 2048, os.SEEK_SET)

    data = {
        "tqlog": "".join(list(logf.readlines()))
    }
    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    if uid:
        response.set_cookie('logcookie', uid)
    return response


@app.route('/artifacts/<uuid:task_id>/<path:subpath>')
def get_artifact(task_id, subpath):
    path = 'result_{0}/{1}'.format(task_id, subpath)
    return send_from_directory(config.artifacts_dir + '/', path)


@app.route('/artifacts/<uuid:task_id>')
def artifacts_list_page(task_id):
    files = list()

    for item in os.walk('{0}/result_{1}'.format(config.artifacts_dir, task_id)):  # TODO
        for file_name in item[2]:
            dir_name = item[0].replace(
                '{0}/result_{1}'.format(config.artifacts_dir, task_id), '', 1)  # TODO
            files.append('{0}/{1}'.format(dir_name, file_name))

    context = dict()
    context['task_id'] = task_id
    context['files'] = files
    context['artifacts_nr'] = len(files)

    return render_template("artifacts.html", **context)


@app.route('/api/tqhost')
def tqhost():
    return jsonify({"tqhost": hostname})


@app.route('/api/stats')
def api_stats():
    local["python3"]["stats.py"] & BG
    return jsonify({"stats": ["stats/stats.svg"]})

# @app.route('/report/<path:path>')
# def report(path):
#     response = send_from_directory('/root/perf/pc1/chronometry/report/', path)
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     return response


if __name__ == '__main__':
    pl_api.init_tq_endpoint("./perfline_proxy.sh")
    print('------------------------------------------------------')
    app.run(**config.server_ep)
