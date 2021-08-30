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

import os
import datetime

def tq_task_common_get(elem, r):
    task = r[0]
    info = r[2]

    elem["task_id"] = task['task_id']
    elem["task_id_short"] = task['task_id'][:4] \
        + "..." + task['task_id'][-4:]

    elem["desc"] = info['info']['conf']['common'].get('description')
    elem["prio"] = info['info']['conf']['common']['priority']
    elem["user"] = info['info']['conf']['common']['user'].\
        replace("@seagate.com", "")

    if 'benchmarks' in info['info']['conf']:
        elem['benchmarks'] = info['info']['conf']['benchmarks']

    if 'workloads' in info['info']['conf']:
        elem['workloads'] = info['info']['conf']['workloads']

    fmt = '%Y-%m-%d %H:%M:%S.%f'
    hms = '%Y-%m-%d %H:%M:%S'
    q = datetime.datetime.strptime(info['info']['enqueue_time'], fmt)
    elem['time'] = {
        "enqueue": q.strftime(hms),
    }

    if 'start_time' in info['info']:
        s = datetime.datetime.strptime(info['info']['start_time'], fmt)
        elem['time']['start'] = s.strftime(hms)

    if 'finish_time' in info['info']:
        f = datetime.datetime.strptime(info['info']['finish_time'], fmt)
        elem['time']['end'] = f.strftime(hms)


def get_list_of_files(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = dict()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles.update(get_list_of_files(fullPath))
        else:
            if fullPath.endswith(".yaml"):
               key = entry.replace(".yaml","")
               allFiles[key] = fullPath
    # Dicts preserve insertion order in Python3.7+ and CPython3.6
    # Creating a new dict based on the old one, but filtered, resolves
    # the ordering problem.
    allFiles = {k: v for k, v in sorted(allFiles.items(), key=lambda item: item[0])}
    return allFiles
