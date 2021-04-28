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
import argparse
import sqlite3
import pandas as pd
from pandas.io import sql


def select_s3reqs(db_connection):
    sql_query = 'SELECT * FROM request where type_id like "%s3_request_state%"'
    return sql.read_sql(sql_query, con=db_connection)


def select_relations(db_connection):
    sql_query = 'SELECT * FROM relation WHERE type_id = "s3_request_to_client"'
    return sql.read_sql(sql_query, con=db_connection)


def find_s3reqs_by_op(op_name, s3df, reldf, workload_time_parts_nr, req_nr):
    s3req_start = s3df[s3df.state.str.startswith('START')]

    s3req_ids = s3df[s3df.state.str.startswith(f'S3{op_name}ObjectAction')][['pid', 'id']].drop_duplicates()
    s3reqs = pd.merge(s3req_start, s3req_ids, on=['pid', 'id'], how='inner').sort_values(by=['time'])

    start_timestamp = s3reqs['time'].min()
    end_timestamp = s3reqs['time'].max()
    workload_duration = end_timestamp - start_timestamp
    workload_duration_part = workload_duration // workload_time_parts_nr

    for i in range(1, workload_time_parts_nr):
        timestamp = start_timestamp + (workload_duration_part * i)
        s3_tmp = s3reqs[s3reqs['time'] >= timestamp]
            
        for index, row in s3_tmp.head(n=req_nr).iterrows():
            s3pid = row['pid']
            s3id = row['id']

            percentage = (100 // workload_time_parts_nr) * i

            print("time:{} s3_op:{} s3_pid:{} s3_reqid:{}".format(percentage, op_name, s3pid, s3id))
            s3req_rels = reldf[(reldf.pid1 == s3pid) & (reldf.mid1 == s3id)]
            for j, rr in s3req_rels.iterrows():
                print("time:{} s3_op:{} s3_pid:{} s3_reqid:{} cli_pid:{} cli_reqid:{}".format(
                    percentage, op_name, s3pid, s3id, rr['pid2'], rr['mid2']))


def positive_int(val):
    result = int(val)

    if result <= 0:
        raise ValueError("only positive values are allowed")

    return result


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    
    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-p", "--workload-time-parts", type=positive_int, default=4,
                        help="""
                        Workload time will be splitted into several parts.
                        From each part of workload time will be taken several requests. 
                        """)
    parser.add_argument("-r", "--req-nr", type=positive_int, default=3,
                        help="""
                        Number of requests that will be taken from each part of
                        workload time.
                        """)


    return parser.parse_args()


def main():
    args = parse_args()
    db_connection = sqlite3.connect(args.db)

    s3df = select_s3reqs(db_connection)
    reldf = select_relations(db_connection)

    for op in ('Put', 'Get'):
        find_s3reqs_by_op(op, s3df, reldf, args.workload_time_parts,
                          args.req_nr)


if __name__ == "__main__":
    main()
