#!/usr/bin/env python3
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from pandas.io import sql
import sqlite3
import gc
import sys
import argparse
from sys_utils import *
import copy

class LocalFigure():
    def __init__(self, fig):
        self.fig = fig
        self.sharex = None

class Handler():
    NUM_CLI_LAYERS = 1 # MOTR IOO
    NUM_SRV_LAYERS = 2 # FOM, STIO
    NUM_COLS       = 1 # Only MBps

    def __init__(self, fiter, avg_window, save_only,
                 hostmap=None, agg=True,
                 per_host=False, per_process=True,
                 client=True, server=True):
        self.hostmap = hostmap
        self.save_only = save_only
        self.avg_window = avg_window
        self.fiter = fiter
        self.agg = agg
        self.per_host = per_host
        self.per_process = per_process
        self.client = client
        self.server = server
        if self.agg:
            self.cluster_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide throughput',
                                                  self.NUM_CLI_LAYERS + self.NUM_SRV_LAYERS,
                                                  self.NUM_COLS))
        if self.agg and self.client:
            self.client_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide client throughput',
                                                 self.NUM_CLI_LAYERS, self.NUM_COLS))

        if self.agg and self.server:
            self.server_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide server throughput',
                                                 self.NUM_SRV_LAYERS, self.NUM_COLS))

        if self.hostmap and self.per_host and self.client:
            self.client_hosts = dict()
        if self.hostmap and self.per_host and self.server:
            self.server_hosts = dict()

        if self.per_process and self.client:
            self.client_process = dict()
        if self.per_process and self.server:
            self.server_process = dict()

    def draw_layer(self, fig, ypos, mbps, avg, pids=None,
                   sharex=None, samex=False):
        ax = fig.add(mbps, ypos, 0, sharex=sharex)
        return ax

    def draw(self, lfig, ypos, mbps, first_plot=False, pids=None):
        ax = self.draw_layer(lfig.fig, ypos, mbps,
                             self.avg_window, sharex=lfig.sharex,
                             samex=first_plot, pids=pids)
        lfig.sharex = ax
        if first_plot:
            ax.set_title(f"Throughput, MBps, avg_window {self.avg_window}")

    def process_agg(self, mbps, ypos_com, ypos_cli, ypos_srv):

        if self.agg and ypos_com is not None:
            self.draw(self.cluster_agg, ypos_com, mbps, mbps.layer.layer_type == IOO)

        if self.agg and self.client and ypos_cli is not None:
            self.draw(self.client_agg, ypos_cli, mbps, mbps.layer.layer_type == IOO)

        if self.agg and self.server and ypos_srv is not None:
            self.draw(self.server_agg, ypos_srv, mbps, mbps.layer.layer_type == FOM)

    def create_host_figs(self, container, rows, cols, label):
        if not container:
            for host in self.hostmap.keys():
                title = f'{self.fiter.name} node {host} {label} throughput'
                lfig = LocalFigure(Figure(title, rows, cols))
                container[host] = lfig

    def process_per_host(self, mbps,
                         dummy, ypos_cli, ypos_srv):
        if self.hostmap and self.per_host and self.client and ypos_cli is not None:
            if not self.client_hosts:
                self.create_host_figs(self.client_hosts,
                                      self.NUM_CLI_LAYERS,
                                      self.NUM_COLS,
                                      'client')
            for host in self.hostmap.keys():
                df = MBPS(mbps.layer, mbps.attr, mbps.states,
                          mbps.op, avg_window=mbps.window,
                          pids=self.hostmap[host])
                df.attr_cache = mbps.attr_cache
                df.calculate()
                lfig = self.client_hosts[host]
                self.draw(lfig, ypos_cli,
                          df, df.layer.layer_type == IOO,
                          pids=self.hostmap[host])

        if self.hostmap and self.per_host and self.server and ypos_srv is not None:
            if not self.server_hosts:
                self.create_host_figs(self.server_hosts,
                                      self.NUM_SRV_LAYERS,
                                      self.NUM_COLS,
                                      'server')
            for host in self.hostmap.keys():
                df = MBPS(mbps.layer, mbps.attr, mbps.states,
                          mbps.op, avg_window=mbps.window,
                          pids=self.hostmap[host])
                df.attr_cache = mbps.attr_cache
                df.calculate()
                lfig = self.server_hosts[host]
                self.draw(lfig, ypos_srv,
                          df, df.layer.layer_type == FOM,
                          pids=self.hostmap[host])

    def create_process_figs(self, mbps, container, rows, cols, label):
        pids = mbps.get_pids()
        for pid in pids:
            title = f'{self.fiter.name} process {pid} {label} throughput'
            lfig = LocalFigure(Figure(title, rows, cols))
            container[pid]= lfig

    def process_per_process(self, mbps, dummy, ypos_cli, ypos_srv):
        if self.per_process and self.client and ypos_cli is not None:
            if not self.client_process:
                self.create_process_figs(mbps, self.client_process,
                                         self.NUM_CLI_LAYERS,
                                         self.NUM_COLS, 'client')
            pids = self.client_process.keys()
            for pid in pids:
                df = MBPS(mbps.layer, mbps.attr, mbps.states,
                          mbps.op, avg_window=mbps.window, pids=[pid])
                df.attr_cache = mbps.attr_cache
                df.calculate()
                lfig = self.client_process[pid]
                self.draw(lfig, ypos_cli,
                          df, df.layer.layer_type == IOO,
                          pids=[pid])

        if self.per_process and self.server and ypos_srv is not None:
            if not self.server_process:
                self.create_process_figs(mbps, self.server_process,
                                         self.NUM_SRV_LAYERS,
                                         self.NUM_COLS, 'server')
            pids = self.server_process.keys()
            for pid in pids:
                df = MBPS(mbps.layer, mbps.attr, mbps.states,
                          mbps.op, avg_window=mbps.window, pids=[pid])
                df.attr_cache = mbps.attr_cache
                df.calculate()
                lfig = self.server_process[pid]
                self.draw(lfig, ypos_srv,
                          df, df.layer.layer_type == FOM,
                          pids=[pid])

    def process_layer(self, mbps, ypos_com, ypos_cli, ypos_srv):
        foos = [self.process_agg, self.process_per_host, self.process_per_process]
        for f in foos:
            f(mbps, ypos_com, ypos_cli, ypos_srv)

    LAYER_MAP = {
        IOO:      {'ypos_com': 0, 'ypos_cli': 0, 'ypos_srv': None},
        FOM:      {'ypos_com': 1, 'ypos_cli': None, 'ypos_srv': 0},
        STIO:     {'ypos_com': 2, 'ypos_cli': None, 'ypos_srv': 1},
    }

    def consume(self, mbps):
        desc = self.LAYER_MAP[mbps.layer.layer_type]
        self.process_layer(mbps, desc['ypos_com'], desc['ypos_cli'], desc['ypos_srv'])

    def done(self):
        if self.agg:
            self.cluster_agg.fig.draw()
            self.cluster_agg.fig.save()

            if self.client:
                self.client_agg.fig.draw()
                self.client_agg.fig.save()

            if self.server:
                self.server_agg.fig.draw()
                self.server_agg.fig.save()

        if self.client and self.per_process:
            for pid in self.client_process.keys():
                fig = self.client_process[pid].fig
                fig.draw()
                fig.save()

        if self.server and self.per_process:
            for pid in self.server_process.keys():
                fig = self.server_process[pid].fig
                fig.draw()
                fig.save()

        if self.client and self.per_host:
            for host in self.client_hosts:
                fig = self.client_hosts[host].fig
                fig.draw()
                fig.save()

        if self.server and self.per_host:
            for host in self.server_hosts:
                fig = self.server_hosts[host].fig
                fig.draw()
                fig.save()

        if not self.save_only:
            Figure.show_plt()

def pandas_init():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

def pandas_fini():
    pass

def calculate(conn, fiter, handler):
    s3all = Layer(S3, conn)
    s3 = fiter.run(s3all)
    del s3all
    gc.collect()

    rel = Relation(S3_TO_CLIENT, conn)
    motr_all = Layer(MOTR_REQ, conn)
    motr = rel.sieve(s3, motr_all)

    del rel
    del motr_all
    gc.collect()

    ioo_all = Layer(IOO, conn)
    rel = Relation(CLIENT_TO_IOO, conn)
    ioo = rel.sieve(motr, ioo_all)

    ioo_attr = Attr(conn, ['M0_AVI_IOO_ATTR_BUFS_NR', 'M0_AVI_IOO_ATTR_BUF_SIZE'])
    ioo_attr.read()
    ioo_mbps = MBPS(ioo, ioo_attr, ['IO_req_complete'], 'prod')
    ioo_mbps.calculate()

    handler.consume(ioo_mbps)
    del motr
    del ioo_all
    del rel
    gc.collect()

    rpc_all = Layer(CRPC, conn)
    rel_ioo = Relation(IOO_TO_CRPC, conn)
    rel_cob = Relation(COB_TO_CRPC, conn)
    rel_cas = Relation(CAS_TO_CRPC, conn)
    crpc = rel_ioo.sieve(ioo, rpc_all)

    del rel_ioo
    del rel_cob
    del rel_cas
    del rpc_all

    rpc_all = Layer(SRPC, conn)
    rel = XIDRelation(conn)
    srpc = rel.sieve(crpc, rpc_all)

    del rpc_all
    del crpc

    fom_all = Layer(FOM, conn)
    rel = Relation(SRPC_TO_FOM, conn)
    fom = rel.sieve(srpc, fom_all)
    del rel
    del srpc
    del fom_all
    gc.collect()

    fom_attr = Attr(conn, ['M0_AVI_IOS_IO_ATTR_FOMCRW_BYTES'])
    fom_attr.read()
    fom_mbps = MBPS(fom, fom_attr, ['finish'], 'sum')
    fom_mbps.calculate()
    handler.consume(fom_mbps)

    stio_all = Layer(STIO, conn)
    rel = Relation(FOM_TO_STIO, conn)
    stio = rel.sieve(fom, stio_all)

    del stio_all
    del rel
    gc.collect()

    stio_attr = Attr(conn, ['M0_AVI_STOB_IO_ATTR_UVEC_BYTES'])
    stio_attr.read()
    stio_mbps = MBPS(stio, stio_attr, ['M0_AVI_AD_ENDIO'], 'sum')
    stio_mbps.calculate()

    handler.consume(stio_mbps)
    del stio
    del fom
    gc.collect()

    handler.done()

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    mbps.py: Generate throughput plots of Cortx S3 and Motr layers
    """)

    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-g",'--s3get', action='store_true',
                        help="Show plots of S3GetObject operation")
    parser.add_argument("-p", "--s3put", action='store_true',
                        help="Show plots of S3GetObject operation")
    parser.add_argument("-s", "--save-only", action='store_true',
                        help="Don't show figures, only save")
    parser.add_argument("-w", "--avg-window", type=str, default='1s',
                        help="Rolling window duration, default '1s'")
    parser.add_argument("--client", action="store_true",
                        help="Show client side of stack: MotrReq")
    parser.add_argument("--server", action="store_true",
                        help="Show server side of stack: FOM, STIO")
    parser.add_argument('-a', "--all", action="store_true",
                        help="Plot possible views: cluster-wise, per porcess and per host")
    parser.add_argument("--aggregated", action="store_true",
                        help="Plot cluster-wise (aggregated) view")
    parser.add_argument("--per-host", action="store_true",
                        help="Plot per-host view")
    parser.add_argument("--per-process", action="store_true",
                        help="Plot per-process view")
    args = parser.parse_args()

    return args

def get_hosts_pids(conn):
    table_descr_query = 'select * from sqlite_master where type="table" and name="host"'
    table_descr_df = sql.read_sql(table_descr_query, con=conn.conn)

    if table_descr_df.empty:
        return None

    pids_df = sql.read_sql('select * from host', con=conn.conn)

    if pids_df.empty:
        return None

    pids_df = pids_df.drop_duplicates(subset=['pid'])
    hostmap = pids_df.groupby('hostname')['pid'].apply(list).to_dict()
    return hostmap

def main():
    args = parse_args()

    pandas_init()

    conn = Connection(args.db)
    conn.connect()

    if not args.s3get and not args.s3put:
        args.s3get = True
        args.s3put = True

    if not args.client and not args.server:
        args.client = True
        args.server = True

    if not args.aggregated and not args.per_process and not args.per_host:
        args.all = True

    if args.all:
        args.aggregated = True
        args.per_process = True
        args.per_host = True

    hostmap = get_hosts_pids(conn)

    if args.s3put:
        handler = Handler(S3PUT_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap,
                          agg=args.aggregated,
                          per_host=args.per_host,
                          per_process=args.per_process,
                          client=args.client,
                          server=args.server)
        calculate(conn, S3PUT_FILTER, handler)

    if args.s3get:
        handler = Handler(S3GET_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap,
                          agg=args.aggregated,
                          per_host=args.per_host,
                          per_process=args.per_process,
                          client=args.client,
                          server=args.server)
        calculate(conn, S3GET_FILTER, handler)

    return

if __name__ == "__main__":
    main()
