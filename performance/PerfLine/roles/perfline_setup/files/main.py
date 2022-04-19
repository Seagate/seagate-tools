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
import getopt
import sys

def recdone(tr, rec):
    if rec != None:
        rec.done(tr)

def processinput(argv):
    kw = {
        "height"    : 1000000,
        "width"     :   40000,
        "loc_nr"    :       4,
        "duration"  :     100,
        "step"      :     100,
        "starttime" :    None
    }
    xlate = {
        "-h" : ("height",    int, "Output image height in pixels."),
        "-w" : ("width",     int, "Output image width in pixels."),
        "-v" : ("verbosity", int, "Verbosity level."),
        "-d" : ("duration",  float, "Duration of the part of the input"
                " to process in seconds."),
        "-l" : ("loc_nr",    int, "Number of localities in the analysed"
                " process. If 1, localities are ignored."),
        "-s" : ("step",      int, "Milliseconds between timestamp axes."),
        "-f" : ("maxfom",    int, "Maximum number of foms per locality."),
        "-t" : ("starttime", str, "Timestamp in the addb format at which"
                " output generation starts."),
        "-L" : ("label",     int, "If 0, omit text labels,"),
        "-o" : ("outname",   str, "Output file name.")
    }
    try:
        opts, args = getopt.getopt(argv[1:], "h:w:l:d:s:t:o:f:v:L:")
    except getopt.GetoptError:
        print "{} [options]\n\nOptions:\n".format(argv[0])
        for k in xlate:
            print "    {} : {}".format(k, xlate[k][2])
        sys.exit(2)
    for opt, arg in opts:
        xl = xlate[opt]
        kw[xl[0]] = xl[1](arg)

    tr = record.trace(**kw)
    rec = None;
    for line in fileinput.input([]):
        params = line[1:].split()
        if line[0] == "*":
            recdone(tr, rec)
            rec = record.parse(tr, params)
        elif line[0] == "|":
            if rec != None:
                rec.add(params)
        else:
            assert False
    recdone(tr, rec)
    tr.done()

if __name__ == "__main__":
    processinput(sys.argv)


