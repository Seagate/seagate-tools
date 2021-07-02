
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

import json
from os.path import join, isfile
from datetime import datetime
from os import listdir
from threading import Lock
from copy import copy


CACHE_UPDATE_PERIOD_SECONDS = 20
PERFLINE_METADATA_FILENAME = 'perfline_metadata.json'
PERF_RESULTS_FILENAME = 'perf_results'
ARTIFACTS_DIR_PREFIX = 'result_'


class TaskCache:
    
    def __init__(self):
        self._storage = dict()
        self._last_update_time = None
        self._lock = Lock()


    def update(self, artifacts_locations, force = False):
        if not force and self.__cache_is_valid():
            return

        with self._lock:
            storage_copy = copy(self._storage)


        deleted_tasks = set(storage_copy.keys())

        for location in artifacts_locations:
            artif_dirs = [join(location, d) for d in listdir(location)
                                if d.startswith(ARTIFACTS_DIR_PREFIX)]

            for artifacts_dir in artif_dirs:
                task_id = self.__parse_task_id(artifacts_dir)

                if task_id in storage_copy:
                    deleted_tasks.remove(task_id)

                    if storage_copy[task_id]['location'] == location:
                        continue

                task_data = self.__parse_task_data(artifacts_dir)

                if task_data:
                    print(f'found new completed task {task_id}')
                    perf_results = self.__parse_perf_results(artifacts_dir)
                    self.__put(storage_copy, task_id, location,
                               task_data, perf_results)

        for deleted_task_id in deleted_tasks:
            print(f'delete task {deleted_task_id} from cache')
            self.__remove(storage_copy, deleted_task_id)

        with self._lock:
            self._storage = storage_copy
            self._last_update_time = datetime.now()


    def get_tasks(self, limit, locations=None):

        def start_time(pl_metadata):
            return datetime.strptime(pl_metadata['start_time'],
                                     '%Y-%m-%d %H:%M:%S.%f')

        def prepare_dat(task_id, task_data):
            return [{'task_id': task_id},
                    {'state': 'FINISHED'},
                    {'info': task_data}]

        with self._lock:

            if locations is not None:
                filtered = filter(lambda kv: kv[1]['location'] in locations,
                                  self._storage.items())
            else:
                filtered = self._storage.items()

            tasks = sorted(filtered, reverse=True,
                           key=lambda kv: start_time(kv[1]['pl_metadata']))

        tasks = [prepare_dat(i[0], i[1]['pl_metadata']) for i in tasks]
        return tasks[0:limit]


    def has(self, task_id):
        with self._lock:
            return task_id in self._storage


    def get_location(self, task_id):
        with self._lock:
            return self._storage[task_id]['location']


    def get_perf_results(self, task_id):
        with self._lock:
            return self._storage[task_id]['perf_results']


    def __cache_is_valid(self):
        with self._lock:
            last_update_time = self._last_update_time

        if last_update_time is None:
            return False

        time_delta = datetime.now() - last_update_time

        if time_delta.total_seconds() > CACHE_UPDATE_PERIOD_SECONDS:
            return False

        return True


    @staticmethod
    def __put(storage, task_id, location, data, perf_results=None):
        task_data = dict()
        task_data['pl_metadata'] = data
        task_data['location'] = location
        task_data['perf_results'] = perf_results
        storage[task_id] = task_data


    @staticmethod
    def __remove(storage, task_id):
        del storage[task_id]


    @staticmethod
    def __parse_task_id(artifacts_dir_path):
        return artifacts_dir_path.split('/')[-1].split('_')[-1]


    @staticmethod
    def __parse_perf_results(artifacts_dir_path):
        perf_results = None
        perf_results_path = f'{artifacts_dir_path}/{PERF_RESULTS_FILENAME}'

        if isfile(perf_results_path):
            perf_results = []

            with open(perf_results_path) as f:
                for line in f:
                    line_s = line.strip()
                    if line_s:
                        perf_results.append({'val': line_s})
        return perf_results


    @staticmethod
    def __parse_task_data(artifacts_dir_path):
        pl_metadata_file = f'{artifacts_dir_path}/{PERFLINE_METADATA_FILENAME}'

        if not isfile(pl_metadata_file):
            print(f'file {pl_metadata_file} not found')
            return None

        with open(pl_metadata_file, 'rt') as f:
            pl_metadata = f.read()

        data = None

        try:
            data = json.loads(pl_metadata)
        except Exception as e:
            print(e)

        return data
