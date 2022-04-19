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

from threading import Thread, Lock
from time import sleep
from collections import deque

from core.async.move_dir import move_dir

class AsyncWorker:

    def __init__(self):

        print("AsyncWorker is created")

        def fff():
            self.__worker_func()

        self.__lock = Lock()
        self.__queue = deque()
        self.__term_tequest = False
        self.__worker_thread = Thread(target=fff)

    def start(self):
        self.__worker_thread.start()

    def stop(self):
        print("got termination request")

        with self.__lock:
            self.__term_tequest = True

        self.__worker_thread.join()

    def move_dir_async(self, origin_dir, src_dir, dst_dir):
        item = dict()
        item['action'] = 'move_dir'
        item['original'] = origin_dir
        item['src'] = src_dir
        item['dst'] = dst_dir

        self.process_async(item)

    def process_async(self, item):
        with self.__lock:
            self.__queue.append(item)

    def __worker_func(self):
        print("worker thread started now")

        while True:
            with self.__lock:
                term_request = self.__term_tequest
                queue_item_nr = len(self.__queue)

            if term_request:
                break

            if queue_item_nr == 0:
                sleep(1)
                continue

            with self.__lock:
                item = self.__queue.popleft()

            try:
                self.__process_item(item)
            except Exception as e:
                print(e)

        print("worker thread finished now")

    def __process_item(self, item):
        print(f"processing: {item}")
        action = item['action']

        if action == "move_dir":
            move_dir(item['original'], item['src'], item['dst'])
        else:
            print(f"unsupported action: {action}")
