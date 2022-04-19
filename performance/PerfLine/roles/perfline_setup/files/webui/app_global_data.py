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


from flask import Flask
from plumbum import local

from core import task_cache
from core.async.async_worker import AsyncWorker
exec(open('./../perfline.conf').read())

hostname = local["hostname"]["-s"]().strip()
app = Flask(__name__)
cache = task_cache.TaskCache()
async_worker = AsyncWorker()
report_resource_map = dict()

artifacts_dirs = [ARTIFACTS_DIR]
night_daemon_dirs = [NIGHT_ARTIFACTS]

if BACKUP_ARTIFACTS_DIR:
    backup_artifacts_dirs = [BACKUP_ARTIFACTS_DIR]
else:
    backup_artifacts_dirs = []

all_artif_dirs = artifacts_dirs + backup_artifacts_dirs
