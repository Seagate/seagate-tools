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
import sqlite3
import pandas as pd
from pandas.io import sql

WORKLOAD_TIME_PARTS_NR = 4 # split workload time 0-25%, 25-50%, 50-75%, 75-100%


def select_s3reqs(db_connection):
    sql_query = 'SELECT * FROM request where type_id like "%s3_request_state%"'
    return sql.read_sql(sql_query, con=db_connection)


def select_relations(db_connection):
    sql_query = 'SELECT * FROM relation WHERE type_id = "s3_request_to_client"'
    return sql.read_sql(sql_query, con=db_connection)


def find_s3reqs_by_op(op_name, s3df, reldf):
    s3req_start = s3df[s3df.state.str.startswith('START')]

    s3req_ids = s3df[s3df.state.str.startswith(f'S3{op_name}ObjectAction')][['pid', 'id']].drop_duplicates()
    s3reqs = pd.merge(s3req_start, s3req_ids, on=['pid', 'id'], how='inner').sort_values(by=['time'])

    start_timestamp = s3reqs['time'].min()
    end_timestamp = s3reqs['time'].max()
    workload_duration = end_timestamp - start_timestamp
    workload_duration_part = workload_duration // WORKLOAD_TIME_PARTS_NR

    for i in range(1, WORKLOAD_TIME_PARTS_NR):
        timestamp = start_timestamp + (workload_duration_part * i)
        s3_tmp = s3reqs[s3reqs['time'] >= timestamp]
            
        for index, row in s3_tmp.head(n=3).iterrows():
            s3pid = row['pid']
            s3id = row['id']

            percentage = (100 // WORKLOAD_TIME_PARTS_NR) * i

            print("time:{} s3_op:{} s3_pid:{} s3_reqid:{}".format(percentage, op_name, s3pid, s3id))
            s3req_rels = reldf[(reldf.pid1 == s3pid) & (reldf.mid1 == s3id)]
            for j, rr in s3req_rels.iterrows():
                print("time:{} s3_op:{} s3_pid:{} s3_reqid:{} cli_pid:{} cli_reqid:{}".format(
                    percentage, op_name, s3pid, s3id, rr['pid2'], rr['mid2']))


def main():
    db_path = sys.argv[1]
    db_connection = sqlite3.connect(db_path)

    s3df = select_s3reqs(db_connection)
    reldf = select_relations(db_connection)

    for op in ('Put', 'Get'):
        find_s3reqs_by_op(op, s3df, reldf)


if __name__ == "__main__":
    main()
