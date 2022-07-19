#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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

"""
Script for collecting system data
Command line arguments:  object size, name
  Ex: python3 systemMonitoring.py <object size> <name>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""


import modules.common_functions as cf
import modules.schemas as schemas
import mongodbapi as mapi
import os
import subprocess
import time
import sys
import datetime
import socket


class SystemMonitor:

    def __init__(self, Object_Size, Name):
        self.Object_Size = Object_Size
        self.Name = Name
        self.cmd = [[['sar', '5'], 'p1', "CPU"], [['sar', '-r', '5'], 'p2', "MEMORY"],
                    [['sar', '-d', '5'], 'p3',
                        "DISK"], [['sar', '-b', '5'], 'p4', "I/O"],
                    [['sar', '-n', 'DEV', '5'], 'p5', "NETWORK"]]
        self.main_config = cf.import_perfpro_config()
        self.db_uri = self.main_config["sanity"]["database"]["url"]
        self.db_name = self.main_config["sanity"]["database"]["name"]
        self.build, self.Version, self.Branch, self.OS = cf.get_build_info(
            self.main_config)
        self.add_report()

    def add_report(self):
        """Execute the required command on shell using suprocess"""

        count = 0
        f = open("pidfile", "w+")
        f.close()
        for c in self.cmd:
            c[1] = subprocess.Popen(c[0], stdout=subprocess.PIPE)
            count += 1

        time.sleep(3)
        while os.path.isfile("pidfile"):
            time.sleep(1)

        for c in self.cmd:
            c[1].kill()
            self.out, _ = c[1].communicate()
            self.outs = self.out.splitlines()
            # print("\n"+c[2]+"\n")
            self.device = c[2]
            self.add_data()

    def add_data(self):
        """Create a config set for system monitoring"""

        self.Config_ID = "NA"
        self.config_set = schemas.set_system_monitoring_config_set()
        self.update_or_insert_documnets(self.config_set, 'config_collection')

    def update_or_insert_documnets(self, query, collection):
        """Update or insert the documnents in the required DB collection

        Args:
            query (dict): set of the data
            collection (dict): mongodb collection
        """

        status, result = mapi.find_documents(
            query, None, self.db_uri, self.db_name, collection)
        if status:
            self.Config_ID = result['_id']

        attr = " ".join(self.outs[2].decode("utf-8").split()).split(" ")
        length = len(attr)

        for d in self.outs[3:]:
            value = " ".join(d.decode("utf-8").split()).split(" ")
            if value[0] != "":
                if value[2] != "DEV" and value[2] != "IFACE":
                    count = 2
                    self.host = socket.gethostname()
                    self.time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.primary_set = schemas.set_system_monitoring_primary_set(
                        self)
                    self.insertion_set = schemas.set_system_monitoring_insertion_set(
                        self, value[0])

                    while count < length:
                        self.insertion_set.update({attr[count]: value[count]})
                        count += 1
                    self.sysstats = {}
                    self.sysstats.update(self.primary_set)
                    self.sysstats.update(self.insertion_set)
                    try:
                        self.iteration()
                    except Exception as e:
                        print(
                            "Unable to insert/update documents into database. Observed following exception:")
                        print(e)

    def iteration(self):
        """Iterate  over the collection"""

        self.find_iteration = True
        self.delete_data = True
        if self.find_iteration:
            iteration_number = cf.get_latest_iteration(
                self.primary_set, self.db_uri, self.db_name, 'db_collection')
            self.find_iteration = False
        if iteration_number == 0:
            self.sysstats.update(Iteration=iteration_number+1)
        elif self.main_config['overwrite '] == True:
            self.primary_set.update(Iteration=iteration_number)
            self.primary_set.update(Object_Size=self.Object_Size)
            if self.delete_data and self.device == "CPU":
                # api missing
                # col.delete_many(self.primary_set)
                mapi.delete_documents(
                    self.primary_set, None, self.db_uri, self.db_uri, 'sysstats_collections')
                self.delete_data = False
                print(
                    "'overwrite' is True in config. Hence, old DB entry deleted")
            self.sysstats.update(Iteration=iteration_number)
        else:
            self.sysstats.update(Iteration=iteration_number+1)
        mapi.add_document(self.sysstats, self.db_uri,
                          self.db_name, 'sysstats_collections')


def main():
    if os.path.isfile("pidfile"):
        print("systemstats are already running! Nothing to start. Exiting")
        return
    SystemMonitor(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
