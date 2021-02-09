#!/usr/bin/env python3
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

import sys
import yaml
import logging
from addb2db import *
import matplotlib.pyplot as plt
from itertools import zip_longest as zipl

# time convertor
CONV={"us": 1000, "ms": 1000*1000}

REQ_QUERY = """
    SELECT (fr.time-request.time) as time, request.state, fr.state, fr.id FROM request
    JOIN request fr ON fr.id=request.id AND fr.pid=request.pid
    WHERE request.state="{from_}"
    AND fr.state="{to_}"
    AND request.type_id="{plug_name}";
    """

FOM_REQ_WRITE_QUERY = """
    SELECT (fr.time-request.time) as time, request.state, fr.state, fr.id FROM request
    JOIN request fr ON fr.id=request.id AND fr.pid=request.pid
    JOIN attr ON attr.entity_id=request.id and attr.pid=request.pid and attr.name="req-opcode"
    WHERE request.state="{from_}"
    AND fr.state="{to_}"
    AND request.type_id="{plug_name}"
    AND attr.val LIKE '%WRITE%';
    """

FOM_REQ_READ_QUERY = """
    SELECT (fr.time-request.time) as time, request.state, fr.state, fr.id FROM request
    JOIN request fr ON fr.id=request.id AND fr.pid=request.pid
    JOIN attr ON attr.entity_id=request.id and attr.pid=request.pid and attr.name="req-opcode"
    WHERE request.state="{from_}"
    AND fr.state="{to_}"
    AND request.type_id="{plug_name}"
    AND attr.val LIKE '%READV%';
    """

FOM_TO_RPC_QUERY = """
    SELECT (rpc_r.time-fom_r.time), fom_r.state, rpc_r.state
    FROM attr a1 
    JOIN attr a2 
        ON a1.entity_id=a2.entity_id AND a1.pid=a2.pid AND a1.name='fom_sm_id' AND a2.name='rpc_sm_id'
    JOIN attr a3
        ON a1.entity_id=a3.entity_id AND a1.pid=a3.pid AND a3.name='req-opcode'
    JOIN request fom_r ON fom_r.id=a1.val
    JOIN request rpc_r ON rpc_r.id=a2.val
    WHERE a3.val LIKE "%M0_IOSERVICE_%"
    AND rpc_r.pid=fom_r.pid
    AND rpc_r.state="{to_}" AND fom_r.state="{from_}";
    """

SRPC_TO_CRPC_QUERY = """
    SELECT (crq.time-srq.time), srq.state, crq.state
    FROM relation r1
    JOIN relation r2 ON r1.mid2=r2.mid1 AND r1.pid2=r2.pid1
    JOIN request crq ON r1.mid1=crq.id AND r1.pid1=crq.pid AND r1.type_id='rpc_to_sxid'
    JOIN request srq ON r2.mid2=srq.id AND r2.pid2=srq.pid AND r2.type_id='sxid_to_rpc'
    WHERE crq.state="{to_}" AND srq.state="{from_}";
    """

HIST_TYPES = {'client_req'       : REQ_QUERY,
              'fom_req_w'        : FOM_REQ_WRITE_QUERY,
              'fom_req_r'        : FOM_REQ_READ_QUERY,
              'fom_to_rpc'       : FOM_TO_RPC_QUERY, 
              'ioo_req'          : REQ_QUERY,
              'srpc_to_crpc'     : SRPC_TO_CRPC_QUERY,
              'stio_req'         : REQ_QUERY,
              's3_request_state' : REQ_QUERY}

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="""hist.py: creates timings histograms from performance samples.""",
    epilog="""Examples:
    1. list of the supported histogram types
        # ./hist.py -l

    2. histogram of fom_req_w type
        # ./hist.py -f png -o write.png -v -u ms -t fom_req_w
          "[[auth, zero-copy-initiate], [zero-copy-initiate, tx_open],
          [tx_open, stobio-launch], [stobio-launch, network-buffer-release],
          [tx_commit, finish]]"
    """)
    parser.add_argument('--db', type=str, required=False, default="m0play.db")
    group0 = parser.add_mutually_exclusive_group(required=True)
    group0.add_argument("-t", "--hist-type", type=str, help="histogram type")
    group0.add_argument("-l", "--list", action='store_true', help="prints supported types of histograms")
    parser.add_argument("-v", "--verbose", action='count', default=0)
    parser.add_argument("-u", "--time-unit", choices=['ms','us'], default='us')
    parser.add_argument("-o", "--out", type=str, default="img.svg")
    parser.add_argument("-f", "--fmt", type=str, default="svg")
    parser.add_argument("-r", "--rows", type=int, default=1)
    parser.add_argument("-s", "--size", nargs=2, type=int, default=[12,4])
    parser.add_argument("range", nargs='?', help="""
    "[[from1, to1, [rend]], ... [from_n, to_n, [rend_n]]]"
    """)

    return parser.parse_args()

def draw_histogram(from_, to_, range_end, plug_name, time_unit):
    sql_query = HIST_TYPES[plug_name].format(from_ = from_, to_ = to_, plug_name = plug_name)
    logging.info(f"hist_type={plug_name} query={sql_query}")
    DIV = CONV[time_unit]
    fields = []
    with DB.atomic():
        cursor = DB.execute_sql(sql_query)
        fields = [f[0]/DIV for f in cursor.fetchall()]

    max_f = round(max(fields), 2)
    min_f = round(min(fields), 2)
    avg_f = round(sum(fields) / len(fields), 2)
    ag_stat = f"total max/avg/min {max_f}/{avg_f}/{min_f}"

    in_range = [f for f in fields if range_end is None or f < range_end]
    plt.hist(in_range, 50)
    plt.title(f"{from_} \n {to_}")

    fs = len(fields)
    ir = len(in_range)
    stat = f"total/range/%: {fs}/{ir}/{round(ir/fs,2)}"
    logging.info(stat)
    plt.xlabel(f"time({time_unit}) \n {stat} \n {ag_stat}")
    plt.ylabel(f"frequency \n")
    plt.tight_layout()


def hist(db_name, plug, range, fmt="svg", out="img.svg", time_unit="us", rows=1, size=(12,4)):
    stages = yaml.safe_load(range)
    db_init(db_name)
    db_connect()

    plt.figure(figsize=size)
    nr_stages = len(stages)
    columns = nr_stages // rows + (1 if nr_stages % rows > 0 else 0)
    for nr,s in enumerate(stages, 1):
        r = dict(zipl(["from", "to", "end"], s, fillvalue=None))
        plt.subplot(rows, columns, nr)
        plt.grid(True)
        draw_histogram(r["from"], r["to"], r["end"], plug, time_unit)

    db_close()
    plt.savefig(fname=out, format=fmt)

if __name__ == "__main__":
    args=parse_args()

    verbosity = { 0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG }
    logging.basicConfig(format='%(asctime)s - %(levelname)-8s %(message)s',
                        level=verbosity[args.verbose if args.verbose < max(verbosity)
                                        else max(verbosity)])

    if args.list:
        print("Supported histograms:")
        for k in HIST_TYPES.keys():
            print(k)

    if args.hist_type:
        hist(args.db, args.hist_type, args.range, args.fmt, args.out, args.time_unit, args.rows, args.size)
