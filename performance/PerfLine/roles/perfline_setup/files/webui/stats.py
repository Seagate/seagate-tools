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

import matplotlib.pyplot as plt
import datetime
import yaml
import os
import taskq_api

STATS = "stats.svg"
today = datetime.datetime.utcnow().date()

try:
    mtime = datetime.datetime.fromtimestamp(os.stat(STATS).st_mtime).date()
    if (today == mtime):
        exit(0)
except FileNotFoundError:
    pass

fmt = '%Y-%m-%d %H:%M:%S.%f'
totals = {}

taskq_api.init_tq_endpoint("./task_queue_proxy.sh")
lines = taskq_api.get_results().split('\n')
lines = filter(None, lines) #remove empty line
results = [yaml.safe_load(line) for line in lines]

dates = []
for r in results:
    try:
        q = datetime.datetime.strptime(r[2]['info']['enqueue_time'],
                                       fmt).date()
        dates.append(q)
    except Exception as e:
        print(e)

d = min(dates)
while d <= max(dates):
    date = d.strftime('%m/%d')
    if d >= today - datetime.timedelta(days=60):
        totals[date] = 0
    d = d + datetime.timedelta(days=1)

for r in results:
    try:
        q = datetime.datetime.strptime(r[2]['info']['enqueue_time'],
                                       fmt).date()
        if q >= today - datetime.timedelta(days=60):
            date = q.strftime('%m/%d')
            totals[date] = totals[date] + 1
    except Exception as e:
        print(e)

plt.figure(figsize=(16.00, 6.00))

marker = ["o", "v", "^", "X", "D", "d", "s"]
lstyle = ["solid", "dashed", "dashdot"]

plt.plot(list(totals.keys()), list(totals.values()),
         marker=marker[0], ls=lstyle[0], ms=12,
         lw=4, label="total")

plt.xlabel("date")
plt.ylabel("tests nr")
plt.title("PC1: number of tests daily")
plt.xticks(rotation=30)
plt.legend()
plt.gca().yaxis.grid(True)
plt.savefig(f"stats/tmp.{STATS}")
os.replace(f"stats/tmp.{STATS}", f"stats/{STATS}")
