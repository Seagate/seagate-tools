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


import fileinput
import record
import sys

def filter(argv):
    tr = record.trace(height = 10, width = 1000, loc_nr = 1, duration = 1,
                      step = 1)
    rec = ""
    fname = ""
    f = None
    for line in fileinput.input([]):
        params = line[1:].split()
        if line[0] == "*":
            if rec != "":
                name = "out." + node + "." + pid + "." + time
                if name != fname:
                    if f != None:
                        f.close()
                    f = open(name, "w+")
                    fname = name
                f.write(rec)
                rec = ""
            time = params[0][0:19]
            keep = record.keep(params[1])
        elif params[0] == "node":
            node = params[1]
        elif params[0] == "pid":
            pid = params[1]
        if keep:
            rec += line
    f.close()

if __name__ == "__main__":
    filter(sys.argv)


