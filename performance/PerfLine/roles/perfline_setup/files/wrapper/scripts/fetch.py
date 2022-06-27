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

import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

exec(open('./../../perfline.conf').read())

class TaskInfo():
    METADATA_FILE = "perfline_metadata.json"
    RESULTS_FILE  = "s3bench_report.csv"
    def __init__(self, folder):
        self.folder = folder
        self.tid = None
        self.date = None
        self.motr = None
        self.s3server = None
        self.hare = None
        self.results = None

    def read(self):
        with open(os.path.join(self.folder, self.METADATA_FILE)) as f:
            data = json.load(f)
            self.date = data["enqueue_time"]
            self.motr = data["conf"]["custom_build"]["motr"]["branch"]
            self.s3server = data["conf"]["custom_build"]["s3server"]["branch"]
            self.hare = data["conf"]["custom_build"]["hare"]["branch"]
            self.tid = data["artifacts_dir"].split("_")[1]
            df = pd.read_csv(os.path.join(self.folder, "client", self.RESULTS_FILE))
            df = df[['numClients', 'objectSize (MB)', 'numSamples', 'Errors Count', 'Total Throughput (MB/s)', 'Errors Count.1', 'Total Throughput (MB/s).1']]
            df.rename(columns = {'Errors Count': 'Write Errors', 'Total Throughput (MB/s)': 'Write Throughput (MB/s)', 'Errors Count.1': 'Read Errors', 'Total Throughput (MB/s).1': 'Read Throughput (MB/s)'}, inplace=True)
            df['TID'] = self.tid
            df['motr'] = self.motr
            df['s3server'] = self.s3server
            df['hare'] = self.hare
            df['date'] = self.date
            self.results = df

    def get_results(self):
        return self.results

    def __str__(self):
        return "TID: {}, Date: {}, motr: {}, s3server: {}, hare: {}".format(
            self.tid, self.date, self.motr, self.s3server, self.hare)


def usage():
    use = """
fetch.py - Fetch build and performance data from list of tasks results.
Information is stored in default night-builds daemon artifacts in
form of bandwidth plots and json dumps.

Usage:
\tpython3 fetch.py "$list_of_tasks_results_dirs" main
\tpython3 fetch.py "$list_of_tasks_results_dirs" stable

for main and stable builds respectively.
    """
    print(use)

def plot_stable(df, filename, size, sessions):
    # TODO: Implement me!
    pass

def plot_main(df, filename, size, sessions):
    commit_domain = df[['motr', 's3server']].drop_duplicates()

    dots = []
    for _, row in commit_domain.iterrows():
        fd = df[(df['motr'] == row['motr']) & (df['s3server'] == row['s3server'])]
        writes = fd['Write Throughput (MB/s)'].tolist()
        reads = fd['Read Throughput (MB/s)'].tolist()

        dots.append({(str(row['motr']), str(row['s3server'])) : {'write': writes, 'read': reads}})

    plot = plt.figure(figsize=(16, 8))

    avgs_x = []
    avgs_write = []
    avgs_read = []
    for d in dots:
        x = next(iter(d))
        y1 = d[x]['write']
        y2 = d[x]['read']
        x = "motr {}\ns3 {}".format(x[0], x[1])

        plt.scatter([x]*len(y1), list(y1), color='red')
        plt.scatter([x]*len(y2), y2, color='green')

        avgs_x.append(x)
        avgs_write.append(sum(y1)/len(y1))
        avgs_read.append(sum(y2)/len(y2))

    plt.scatter(avgs_x, avgs_write, marker='X', color='black')
    plt.scatter(avgs_x, avgs_read, marker='X', color='black')

    plt.plot(avgs_x, avgs_write, color='red', label = 'Write')
    plt.plot(avgs_x, avgs_read, color='green', label = 'Read')

    plt.ylim(bottom=0.0)
    plt.xticks(rotation=45)
    plt.margins(0.5)
    plt.subplots_adjust(bottom=0.2)
    plt.grid()
    plt.title(f"Main branch throughput, {size}, {sessions} sessions")
    plt.ylabel("Throughput, MB/s")
    plt.xlabel("Motr, s3server commit IDs", fontsize=16)
    plt.legend()

    print("Will save to {}".format(filename))
    plt.savefig(filename)
    plt.close(plot)


def plot_img(df, build, filename, size, sessions):
    if build == "main":
        plot_main(df, filename, size, sessions)
    elif build == "stable":
        plot_stable(df, filename, size, sessions)


def main():
    if len(sys.argv) != 3:
        usage()
        exit(1)
    build = sys.argv[1]
    dirs = sys.argv[2].split()

    if build not in ["main", "stable"]:
        usage()
        exit(2)

    tasks = []
    for d in dirs:
        task = TaskInfo(d)
        task.read()
        tasks.append(task)

    df = pd.concat([t.get_results() for t in tasks])
    df.sort_values(by=["date"], inplace=True)

    for size in df['objectSize (MB)'].unique():
        for sessions in df['numClients'].unique():
            fd = df[(df['objectSize (MB)'] == size) & (df['numClients'] == sessions)][['date', 'TID', 'motr', 's3server', 'hare',
                                                                                       'Write Errors', 'Write Throughput (MB/s)',
                                                                                       'Read Errors', 'Read Throughput (MB/s)']]

            size_lookup = {
                "0.0009765625" : "1KB",
                "0.00390625"   : "4KB",
                "0.015625"     : "16KB",
                "0.0625"       : "64KB",
                "0.25"         : "256KB",
                "1.0"          : "1MB",
                "4.0"          : "4MB",
                "16.0"         : "16MB",
                "32.0"         : "32MB",
                "64.0"         : "64MB",
                "128.0"        : "128MB",
                "256.0"        : "256MB",
            }

            # Save json
            base = "_".join([size_lookup[str(size)], str(sessions)])
            filename = os.path.join(NIGHT_ARTIFACTS, build, "data", base + ".json")
            print("Will save to {}".format(filename))
            fd.to_json(filename, orient="split")

            # Save png
            filename = os.path.join(NIGHT_ARTIFACTS, build, "img", base + ".png")
            plot_img(fd, build, filename, size_lookup[str(size)], str(sessions))


if __name__=="__main__":
    main()
