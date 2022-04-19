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

def del_task(task_id):
    _check_tq_ep()
    result = (_tq['-d', task_id])()
    return result

def put_prio(task_id,prio):
    _check_tq_ep()
    result = (_tq['-p', task_id, prio])()
    return result

def _check_tq_ep():
    assert _tq is not None, "call init_tq_endpoint(tq_endpoint_path) before"
