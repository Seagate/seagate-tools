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

from plumbum import local

_tq = None

def init_tq_endpoint(tq_endpoint_path):
    global _tq
    _tq = local[tq_endpoint_path]

def get_queue():
    _check_tq_ep()
    queue = _tq['-l']()
    return queue

def get_results():
    _check_tq_ep()
    results = _tq['-r']()
    return results

def add_task(task_config):
    _check_tq_ep()
    result = (_tq["-a"] << task_config)()
    return result

def _check_tq_ep():
    assert _tq is not None, "call init_tq_endpoint(tq_endpoint_path) before"
