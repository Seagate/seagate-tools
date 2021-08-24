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

from os.path import isdir, join, isfile, isdir
from os import listdir
import json
import gzip
from flask import make_response
from flask import request

from app_global_data import *


def parse_commit_info(line):
    app = line.split('-')[1]
    commit = line.split('_')[1].split('.')[0].replace('git', '')
    return app, commit


def get_commit_info(task_location):
    result = dict()
    stats_dir = f'{task_location}/stats'

    commits = {'hare': {}, 'motr': {}, 's3server': {}}

    for dir_name in listdir(stats_dir):
        if dir_name.startswith('addb'):
            continue

        git_info_file_path = join(stats_dir, dir_name, 'hw/git_info')

        if not isfile(git_info_file_path):
            continue

        with open(git_info_file_path, 'r') as f:
            for line in f.readlines():
                if 'cortx' in line:
                    app, commit = parse_commit_info(line)
                    if app in ('hare', 's3server', 'motr'):
                        commits[app][dir_name] = commit

    for app, node_commit_map in commits.items():
        app_commit = None
        commits_are_equal = True

        for node, commit in node_commit_map.items():
            if app_commit is None:
                app_commit = commit

            if commit != app_commit:
                commits_are_equal = False
                continue
        if commits_are_equal and app_commit is not None:
            result[f'{app}_commit'] = app_commit
        else:
            for node, commit in node_commit_map.items():
                result[f'{node}_{app}_commit'] = commit

    return result


def parse_perfline_metadata(task_id):
    task_location = cache.get_location(task_id) + f'/result_{task_id}'
    perfline_md_file = f'{task_location}/perfline_metadata.json'

    result = dict()

    with open(perfline_md_file) as f:
        data = json.loads(f.read())
        common = data['conf']['common']
        result['description'] = common['description']
        result['user'] = common['user']

    commits_info = get_commit_info(task_location)
    result.update(commits_info)

    return result


@app.route('/api/get_tasks_metadata')
def get_tasks_metadata():
    task_ids = request.args.getlist('task_id')

    if len(task_ids) == 0:
        return make_response("task_id parameter not found", 400)

    data = list()

    for task_id in task_ids:
        try:
            task_md = parse_perfline_metadata(task_id)
            data.append({"task_id": task_id, "metadata": task_md})
        except:
            print(f'error: {e}')

    if len(data) == 0:
        return make_response("data not found", 404)

    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response
