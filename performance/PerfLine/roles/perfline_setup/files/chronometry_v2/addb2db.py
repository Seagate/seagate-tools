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

# METADATA PATH DB SCHEMA DIAGRAM
# ===============================
# |-----------------------------------CLIENT-SIDE------------------------------------|-----------------------SERVER-SIDE----------------------|
#
#                                                                              (rpc_to_sxid)
#                                                                                  |   ^
#                                                                                  V   |
#                                                                              (sxid_to_rpc)
#          client_to_dix    dix_to_mdix     dix_to_cas       cas_to_rpc             |                                        fom_to_tx
#                |              |  (meta_dix)   |               |                   |                                           |
# client_req:id --> dix_req:id --> dix_req:id -----> cas_req:id --> rpc_req:id  ------------> fom_desc:{rpc_sm_id, fom_sm_id}  -----> be_tx:id
#                      \               \...
#                      \               +-----------> cas_req:id --> rpc_req:id  ------------> fom_desc:{rpc_sm_id, fom_sm_id}  -----> be_tx:id
#                      \
#                      +---------------------------> cas_req:id --> rpc_req:id  ------------> fom_desc:{rpc_sm_id, fom_sm_id}  -----> be_tx:id
#                      \ ...
#                      \
#                      +---------------------------> cas_req:id --> rpc_req:id  ------------> fom_desc:{rpc_sm_id, fom_sm_id}  -----> be_tx:id
#
# I/O PATH DB SCHEMA DIAGRAM
# ==========================
#                                                                              (rpc_to_sxid)
#                                                                                  |   ^
#                                                                                  V   |
#                                                                              (sxid_to_rpc)
#                client_to_ioo                     ioo_to_rpc                        |                                       fom_to_tx
#                       |                               |                            |                                           |
# client_req:id ------------------>  ioo_req:id -----------------> rpc_req:id  --------------> fom_desc:{rpc_sm_id, fom_sm_id} ------> be_tx:id
#            \                                                                      ...
#             \  client_to_cob                     cob_to_rpc                        |                                       fom_to_tx
#              \        |                               |                            |                                           |
#               +----------------->  cob_req:id ------------------> rpc_req:id --------------> fom_desc:{rpc_sm_id, fom_sm_id} ------> be_tx:id
#                                                                            \
#                                                                             +--> bulk_req:id

import argparse
import logging
import yaml
import numpy
import time
from peewee import TextField
from peewee import IntegerField
from peewee import SqliteDatabase
from peewee import Model
from typing import List
from itertools import zip_longest
from collections import defaultdict
from tqdm import tqdm
from plumbum.cmd import wc
from math import ceil
import sys
from os.path import basename
import re
import json


DB      = SqliteDatabase(None)
BLOCK   = 32<<10
DBBATCH = 777
PID     = 0

def die(what: str):
    print(what, file=sys.stderr)
    sys.exit(1)

# ======================================================================

class BaseModel(Model):
    class Meta:
        database = DB
        primary_key = False

class relation(BaseModel):
    pid1 = IntegerField()
    mid1 = IntegerField()
    pid2 = IntegerField()
    mid2 = IntegerField()
    type_id = TextField()

class request(BaseModel):
    time    = IntegerField()
    pid     = IntegerField()
    id      = IntegerField()
    state   = TextField()
    type_id = TextField()

class attr(BaseModel):
    entity_id = IntegerField()
    pid       = IntegerField()
    name      = TextField()
    val       = TextField()

class s3_request_uid(BaseModel):
    pid = IntegerField()
    id  = IntegerField()
    uuid = TextField()

class host(BaseModel):
    pid      = IntegerField()
    hostname = TextField()


db_create_delete_tables = [relation, request, attr, s3_request_uid, host]

def db_create_tables():
    with DB:
        DB.create_tables(db_create_delete_tables)

def db_drop_tables():
    with DB:
        DB.drop_tables(db_create_delete_tables)

def db_init(path):
    DB.init(path, pragmas={
        'journal_mode': 'off',
        'cache_size': -1024*1024*256,
        'synchronous': 'off',
    })

def db_connect():
    DB.connect()


def db_close():
    """
    Closes the DB
    """
    DB.close()


def db_idx_create():
    request.add_index(request.id)
    request.add_index(request.pid)
    relation.add_index(relation.mid1)
    relation.add_index(relation.mid2)
    relation.add_index(relation.pid1)
    relation.add_index(relation.pid2)
    attr.add_index(attr.entity_id)
    attr.add_index(attr.pid)

# ======================================================================

class profiler:
    def __init__(self, what):
        self.what = what

    def __exit__(self, exp_type, exp_val, traceback):
        delta = time.time() - self.start
        logging.info(f"{self.what}: {delta}s")
    def __enter__(self):
        self.start = time.time()

# ======================================================================

class ADDB2PP:
    @staticmethod
    def clean_yaml(yml):
        return yml.translate(str.maketrans("><-","''_"))

    @staticmethod
    def to_unix(motr_time):
        mt = list(motr_time)
        mt[10] = 'T'
        np_time = numpy.datetime64("".join(mt))
        return np_time.item()

    # ['*', '2019-09-18-19:08:50.975943665', 'fom-phase',
    #  'sm_id:', '38', '-->', 'HA_LINK_OUTGOING_STATE_WAIT_REPLY']

    #* 2020-11-10-10:50:37.794688308 s3-request-state s3_request_id: 3, state: START
    #* 2020-11-10-11:35:15.162867033 cob-req-state    cob_id: 2175, cob_state: COB_REQ_SENDING
    #* 2020-11-10-11:35:15.967095739 stio-req-state   stio_id: 2053, stio_state: M0_AVI_LIO_ENDIO

    def p_sm_req(measurement, labels, table):
        name   = measurement[2]
        time   = measurement[1]
        state  = measurement[-1]
        sm_id  = int(measurement[4].translate(str.maketrans(","," ")))
        return(("request", { 'time': ADDB2PP.to_unix(time), 'state': state,
                             'id': int(sm_id), "pid": PID, "type_id": table }))

    # ['*', '2019-08-29-12:16:54.279414683',
    #  'client-to-dix', 'client_id:', '1170,', 'dix_id:', '1171']
    def p_1_to_2(measurement, labels, table):
        mid1 = int(measurement[4].replace(",",""))
        mid2 = int(measurement[6])
        pid1 = PID
        pid2 = PID
        type_id = table

        return(("relation", {'mid1': mid1, 'pid1': pid1,
                             'mid2': mid2, 'pid2': pid2,
                             'type_id': type_id }))

# * 2020-11-10-10:50:29.739943771 rpc-item-id-assign id: 19,     opcode: 117, xid: 1,    session_id: 1455042236294234156
# * 2020-11-10-10:50:30.235327857 rpc-item-id-fetch  id: 21,     opcode: 32,  xid: -1,   session_id: 0
# "rpc-item-id-assign": (ADDB2PP.p_1_to_2_rpc,  "rpc_to_sxid"),

    def p_1_to_2_rpc(measurement, labels, table):
        name  = measurement[2]
        time  = measurement[1]
        #ADDB2PP.clean_yaml
        ret   = yaml.safe_load("{"+" ".join(measurement[3:])+"}")
        ret['time']  = ADDB2PP.to_unix(time)
        type_id = table

        if table == "sxid_to_rpc":
            return(("relation", {'mid1': ret['xid'], 'pid1': ret['session_id'],
                                 'mid2': ret['id'],  'pid2': PID,
                                 'type_id': type_id }))
        elif table == "rpc_to_sxid":
            return(("relation", {'mid1': ret['id'],  'pid1': PID,
                                 'mid2': ret['xid'], 'pid2': ret['session_id'],
                                 'type_id': type_id }))
        else:
            assert(False)

# * 2021-06-08-04:55:56.016273408 conn-uuid-to-sm uuid: 18376028739450869&-8057109032192707171, sm_id: 23
# * 2021-06-08-04:56:05.189405952 conn-sm-to-uuid sm_id: 128, uuid: 1747424776239521833&-8746343302169642367
# "conn-uuid-to-sm": (ADDB2PP.p_1_to_2_conn,  "conn_uuid_to_sm"),

    def p_1_to_2_conn(measurement, labels, table):
        name  = measurement[2]
        time  = measurement[1]
        ret   = yaml.safe_load("{"+" ".join(measurement[3:])+"}")
        ret['time']  = ADDB2PP.to_unix(time)
        type_id = table

        fake_mid, fake_pid = ret['uuid'].split('&')

        if table == "conn_uuid_to_sm":
            return(("relation", {'mid1': fake_mid,     'pid1': fake_pid,
                                 'mid2': ret['sm_id'], 'pid2': PID,
                                 'type_id': type_id }))
        elif table == "conn_sm_to_uuid":
            return(("relation", {'mid1': ret['sm_id'], 'pid1': PID,
                                 'mid2': fake_mid,     'pid2': fake_pid,
                                 'type_id': type_id }))
        else:
            assert(False)

#* 2020-11-10-10:42:04.735610561 fom-descr        service: <0:0>,         sender: 0x0, req-opcode: none, rep-opcode: none, local: false,
#                                                 rpc_sm_id: 0, fom_sm_id: 0, fom_state_sm_id: 0

    def p_1_to_2_fom(measurement, labels, table):
        mid1 = int(measurement[14].replace(",",""))
        mid2 = int(measurement[16].replace(",",""))
        pid1 = PID
        pid2 = PID
        type_id = table

        result = list()

        fom_attrs = dict()
        for i in range(3, len(measurement), 2):
            fom_attr_name = measurement[i].replace(':', '')
            fom_attr_val = measurement[i + 1].replace('<', '').replace('>', '').replace(',','')
            fom_attrs[fom_attr_name] = fom_attr_val

        e_id = fom_attrs['fom_sm_id']
        for k, v in fom_attrs.items():
            result.append( ('attr', {'entity_id' : e_id, 'pid' : PID, 'name' : k, 'val' : v}) )

        result.append( ("relation", {'mid1': mid1, 'pid1': pid1,
                             'mid2': mid2, 'pid2': pid2,
                             'type_id': type_id }) )
        return result


    # ['*', '2019-08-29-12:08:23.766071289', 'fom-descr', 'service:', '<0:0>,',  'sender:', '0,', 'req-opcode:', 'none,',  'rep-opcode:', 'none,', 'local:', 'false,', 'rpc_sm_id:', '0,',    'fom_sm_id:', '0']
    # ['*', '2019-08-29-12:16:48.097420953', 'rpc-item-id-assign', 'id:', '19,', 'opcode:', '117,', 'xid:', '1,', 'session_id:', '98789222400000038']
    # [* 2020-03-03-21:55:21.632535498 stio-req-state   stio_id: 1345, stio_state: M0_AVI_LIO_ENDIO]
    # [* 2020-03-03-21:55:19.141584520 s3-request-state s3_request_id: 3, state: START]
    # [* 2019-09-07-09:57:43.936545770 cob-req-state    cob_id: 1310, cob_state: 2]
    # def p_cob_req(measurement, labels, table):
    # def p_stio_req(measurement, mnl, param):
    # def p_rpc_item_id(measurement, labels, table):
    # def p_yaml_req(measurement, labels, table):
    def p_yaml_translate(translate_dict, measurement, labels, table):
        # cob_req: {id: cob_id, state: cob_state}
        # stio_req: {id: stio_id, state: stio_state}
        # s3_req: {id: s3_request_id}
        # rpc_item_id: {}
        # yaml_req: {}
        name  = measurement[2]
        time  = measurement[1]
        # XXX: This is a hot fix. Sergey, Dmitry please find out better solution.
        # XXX: test case: {'id': 19, 'opcode': 33, 'xid': '_1', 'session_id': 0, 'time': 1586878694440410275, 'pid': 30},
        # XXX: xid = "_1" should be "-1"
        clean = (lambda x: x) if name in ["rpc-item-id-fetch",
                                          "rpc-item-id-assign"] else ADDB2PP.clean_yaml
        for i,m in enumerate(measurement[3:]) :
            measurement[i+3] = m.replace("::", "_")
        ret   = yaml.safe_load(clean("{"+" ".join(measurement[3:])+"}"))
        ret['time']  = ADDB2PP.to_unix(time)
        for k,v in translate_dict.items():
            ret[k] = ret.pop(v)
        return((table, ret))

    # [* 2019-11-01-20:27:37.467306782 wail  nr: 992 min: 1 max: 4 avg: 2.719758 dev: 0.461787]
    # [.. | ..         locality         0]
    def p_queue(measurement, labels, table):
        name  = measurement[2]
        time  = measurement[1]
        stat  = measurement[3:13]
        ret = dict(zip([s[:-1] for s in stat[::2]], stat[1::2]))
        ret['time'] = ADDB2PP.to_unix(time)
        ret['type'] = name
        ret.update({"locality":
                    labels.get("locality") or
                    labels.get("stob-ioq-thread") or
                    die(f" {measurement} / {labels} : Label not found!")})
        return((table, ret))

    # ['*'
    #  '2019-11-21-11:32:38.717028449',
    #  'attr',
    #  'entity_id:', '1150,', 'M0_AVI_ATTR__RPC_OPCODE:', 'M0_IOSERVICE_READV_OPCODE']
    def p_attr(measurement, labels, table):
        name      = measurement[2]
        entity_id = measurement[4][:-1]
        attr_name = measurement[5][:-1]
        attr_val  = str(measurement[6])
        ret   = { 'entity_id': entity_id, 'name': attr_name, 'val': attr_val, 'pid': PID }
        return(("attr", ret))

    # ['*',
    #  '2020-01-26-17:14:57.134583699'
    #  's3-request-uid'
    #  's3_request_id:'
    #  '3,',
    #  'uid_first_64_bits:'
    #  '0x9d4251f41ddb76f0,',
    #  'uid_last_64_bits:',
    #  '0xbe11ec28e6e52a80']
    # uid form: f076db1d-f451-429d-802a-e5e628ec11be
    def s3req_uid(measurement, labels, table):
        def s3req_bytes_swap(hexstr):
            t = int(hexstr.strip(" ,"), 16)
            t = f"{t:016x}"
            s = []
            for i in range(int(len(t) / 2)):
                s.append(int(t[2*i:2*i+2], 16))
            s.reverse()
            return "".join(map(lambda a: f"{a:02x}", s))

        ret = {'pid': PID}
        ret['id'] = int(measurement[4][:-1])
        first = s3req_bytes_swap(measurement[6])
        last = s3req_bytes_swap(measurement[8])
        ret['uuid'] = f"{first[:8]}-{first[8:12]}-{first[12:16]}-{last[:4]}-{last[4:]}"
        return((table, ret))

    # ['*', '2020-05-20-01:41:07.988231709', 's3-measurement', 'TRACE_POINT,', '1']
    # ['*', '2020-05-20-01:41:08.060563989', 's3-measurement', 'TRACE_POINT_2,', '2,', '3']
    def p_s3_msrm(measurement, labels, table):
        time = measurement[1]
        msrm = measurement[3].strip(',')
        ret = dict(zip_longest(
            [f"val{i}" for i in range(1,14)],
            map(lambda x: int(x.strip(',')), measurement[4:])))
        ret["time"] = ADDB2PP.to_unix(time)
        ret["name"] = msrm
        return((table, ret))

    def __init__(self):
        self.parsers = {
            "rpc-item-id-fetch" : (ADDB2PP.p_1_to_2_rpc,   "sxid_to_rpc"),
            #            "fom-descr"         : (partial(ADDB2PP.p_yaml_translate, {}), "fom_desc"),   # fom_sm_id, fom state_sm_id
            "fom-descr"         : (ADDB2PP.p_1_to_2_fom,  "rpc_to_fom"),
            "tx-state"          : (ADDB2PP.p_sm_req,      "be_tx"),
            "fom-phase"         : (ADDB2PP.p_sm_req,      "fom_req"),
            "fom-state"         : (ADDB2PP.p_sm_req,      "fom_req_state"),
            "fom-to-tx"         : (ADDB2PP.p_1_to_2,      "fom_to_tx"),
            "tx-to-gr"          : (ADDB2PP.p_1_to_2,      "tx_to_gr"),
            "cas-to-rpc"        : (ADDB2PP.p_1_to_2,      "cas_to_rpc"),
            "dix-to-cas"        : (ADDB2PP.p_1_to_2,      "dix_to_cas"),
            "dix-to-mdix"       : (ADDB2PP.p_1_to_2,      "dix_to_mdix"),
            "dtx0-state"        : (ADDB2PP.p_sm_req,      "dtx0"),
            "client-to-dix"     : (ADDB2PP.p_1_to_2,      "client_to_dix"),
            "rpc-item-id-assign": (ADDB2PP.p_1_to_2_rpc,  "rpc_to_sxid"),
            "rpc-out-state"     : (ADDB2PP.p_sm_req,      "rpc_req"),
            "rpc-in-state"      : (ADDB2PP.p_sm_req,      "rpc_req"),
            "rpc-out-phase"     : (ADDB2PP.p_sm_req,      "rpc_req"),
            "rpc-in-phase"      : (ADDB2PP.p_sm_req,      "rpc_req"),
            "cas-req-state"     : (ADDB2PP.p_sm_req,      "cas_req"),
            "dix-req-state"     : (ADDB2PP.p_sm_req,      "dix_req"),
            "op-state"          : (ADDB2PP.p_sm_req,      "client_req"),
            "client-to-cob"     : (ADDB2PP.p_1_to_2,      "client_to_cob"),
            "cob-to-rpc"        : (ADDB2PP.p_1_to_2,      "cob_to_rpc"),
            "client-to-ioo"     : (ADDB2PP.p_1_to_2,      "client_to_ioo"),
            "ioo-to-rpc"        : (ADDB2PP.p_1_to_2,      "ioo_to_rpc"),
            "ioo-req-state"     : (ADDB2PP.p_sm_req,      "ioo_req"),
            "cob-req-state"     : (ADDB2PP.p_sm_req,      "cob_req"),
            "stio-req-state"    : (ADDB2PP.p_sm_req,      "stio_req"),
            "fom-to-stio"       : (ADDB2PP.p_1_to_2,      "fom_to_stio"),
            "attr"              : (ADDB2PP.p_attr,        "attr"),
            "bulk-to-rpc"       : (ADDB2PP.p_1_to_2,      "bulk_to_rpc"),
            "conn-uuid-to-sm"   : (ADDB2PP.p_1_to_2_conn, "conn_uuid_to_sm"),
            "conn-sm-to-uuid"   : (ADDB2PP.p_1_to_2_conn, "conn_sm_to_uuid"),
            "conn-state"        : (ADDB2PP.p_sm_req,      "conn"),
            "conn-to-session"   : (ADDB2PP.p_1_to_2,      "conn_to_session"),
            "session-state"     : (ADDB2PP.p_sm_req,      "sess"),
            "cas-fom-to-crow-fom" : (ADDB2PP.p_1_to_2,    "cas_fom_to_crow_fom"),
            "s3-request-to-motr"  : (ADDB2PP.p_1_to_2,    "s3_request_to_client"),
            "s3-request-state"    : (ADDB2PP.p_sm_req,    "s3_request_state"),
            "s3-request-uid"      : (ADDB2PP.s3req_uid,   "s3_request_uid"),
        }


    def consume_record(self, rec):
        # measurement[0] and labels[1..] (mnl)
        mnl = rec.split("|")
        measurement = mnl[0].split()
        if measurement == []:
            return
        measurement_name = measurement[2]

        labels=dict([kvf for kvf in [kv.strip().split() for kv in mnl[1:]]
                     if kvf and len(kvf)==2])

        for pname, (parser, type_id) in self.parsers.items():
            if pname == measurement_name:
                return parser(measurement, labels, type_id)
        return None

APP = ADDB2PP()
def fd_consume_record(rec):
    return APP.consume_record(rec) if rec else None


class AddbDumpIterator:
    def __init__(self, file, start_pos=None, end_pos=None):
        self.file = file
        self.start_pos = 0 if start_pos is None else start_pos
        self.cur_pos = -1
        self.end_pos = end_pos

    def __iter__(self):
        self.fd = open(self.file)
        self.fd_iter = iter(self.fd)
        return self

    def __next__(self):
        results = list()
        data_chunk = list()

        for addb_rec in self.fd_iter:
            self.cur_pos += 1

            if self.cur_pos < self.start_pos:
                continue
            elif self.end_pos != None and self.cur_pos >= self.end_pos:
                break

            data_chunk.append(addb_rec)
            if len(data_chunk) >= BLOCK:
                break

        if len(data_chunk) == 0:
            self.fd.close()
            raise StopIteration()

        for raw_record in data_chunk:
            tmp = fd_consume_record(raw_record)
            if isinstance(tmp, list):
                results.extend(tmp)
            else:
                results.append(tmp)

        return results

def get_lines_nr(file_path):
    return int(wc["-l", file_path]().split()[0])

def parse_pid(file_path):
    file_name = basename(file_path)
    fid = file_name.split('.')[0].split('_')[-1]
    return int(fid) if fid.isnumeric() else int(fid, base=16)

def parse_hostname(file_path):
    file_name_parts = basename(file_path).split('.')[0].split('_')

    if len(file_name_parts) == 3:
        return file_name_parts[1]
    return None

def insert_records(tables):
    with profiler("Write to db"):
        for k in tables.keys():
            batching = DBBATCH
            while batching >= 0:
                if batching == 0:
                    raise Exception("Cannot insert records with zero dbbatch size")
                with DB.atomic() as dbatomic:
                    with profiler(f"    {k}/{len(tables[k])}"):
                        try:
                            for batch in chunked(tables[k], batching):
                                globals()[k].insert_many(batch).execute()
                            break
                        except OperationalError as ex:
                            if "too many" in str(ex):
                                logging.warning(f"insert recs int {k} err {ex}")
                                dbatomic.rollback()
                                batching = batching // 2
                            else:
                                raise ex

def db_consume_data(files, append_db: bool):
    if len(files) == 0:
        return

    if not append_db:
        db_drop_tables()
        db_create_tables()

    for (nr,input_file_data) in enumerate(files):

        file = input_file_data[0]

        if len(input_file_data) == 3:
            start = input_file_data[1]
            stop = input_file_data[2]
            lines_nr = stop - start
        else:
            start = None
            stop = None
            lines_nr = get_lines_nr(file)

        global PID
        PID = parse_pid(file)

        hostname = parse_hostname(file)

        if hostname:
            host_rec = host(pid=PID, hostname=hostname)
            host_rec.save()

        with tqdm(total=lines_nr, desc=f"{nr+1}/{len(files)} Read file: {file}") as tqwerty:

            for rows in AddbDumpIterator(file, start, stop):

                filtered_rows = filter(None, rows)
                tables = defaultdict(list)
                for k,v in filtered_rows:
                    tables[k].append(v)

                tqwerty.update(len(rows))
                insert_records(tables)


def db_setup_loggers():
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
    level=logging.INFO
    level_sh=logging.WARN
    logging.basicConfig(filename='logfile.txt',
                        filemode='w',
                        level=level,
                        format=format)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(format))
    sh.setLevel(level_sh)
    log = logging.getLogger()
    log.addHandler(sh)

    logger = logging.getLogger('peewee')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())


auth_srv_format = re.compile(r"\A([0-9\- :,]{23,29})\s+\w+\s+\[ReqId:([0-9a-fA-F\-]{36})\]\s+(\S+).*")


def db_parse_args():
    parser = argparse.ArgumentParser(description="""
addb2db.py: creates sql database containing performance samples
    """)
    parser.add_argument('--dumps', nargs='+', type=str, required=False,
                        default=[],
                        help="""
A bunch of addb2dump.txts can be passed here for processing:
python3 addb2db.py --dumps dump1.txt dump2.txt ...
""")
    parser.add_argument('--jdumps', type=str, required=False, default=None, help="""
Json formatted list of addb dumps with start/end position for each file.
Can be used instead of --dumps parameter to limit number of lines of each dump to process.
Example of using:
python3 addb2db.py --jdumps "[[\\"dumps_1.txt\\",100,200],[\\"dumps_2.txt\\",1000,2000]]"
""")

    parser.add_argument('--db', type=str, required=False,
                        default="m0play.db",
                        help="Output database file")
    parser.add_argument('--block', type=int, required=False,
                        default=BLOCK,
                        help="Block of data from dump files processed at once")
    parser.add_argument('--batch', type=int, required=False,
                        default=DBBATCH,
                        help="Number of samples commited at once")
    parser.add_argument('--append_db', type=bool, required=False, default=False)

    return parser.parse_args()

if __name__ == '__main__':
    args=db_parse_args()

    if args.jdumps:
        input_data = json.loads(args.jdumps)
    else:
        input_data = [ [addb_dump] for addb_dump in args.dumps ]

    BLOCK=args.block
    DBBATCH=args.batch

    db_init(args.db)
    db_setup_loggers()
    db_connect()

    db_consume_data(input_data, args.append_db)
    # db_idx_create()
    db_close()
