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
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from pandas.io import sql
import sqlite3
import gc
import sys
import argparse

def pandas_init():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

def pandas_fini():
    pass

class Connection():
    def __init__(self, filename):
        self.filename = filename
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.filename)

    def get(self):
        if self.conn is None:
            self.connect()
        return self.conn

class TypeId():
    def __init__(self, name, type_id):
        self.name = name
        self.type_id = type_id

class Layer():
    def __init__(self, layer_type, connection):
        self.layer_type = layer_type
        self.connection = connection
        self.df = None

    def write(self, df):
        self.df = df

    def read(self):
        if self.df is None:
            query = f'SELECT * FROM request where type_id="{self.layer_type.type_id}"'
            df = sql.read_sql(query, con=self.connection.get())
            self.df = df.loc[:,~df.columns.duplicated()]
        return self.df

    def merge(self, layer):
        self.df = pd.concat([self.read(), layer.read()], ignore_index=True)

class Filter():
    def __init__(self, name, filter_cb=None):
        self.name = name
        self.filter_cb = filter_cb

    def run(self, layer):
        df = self.filter_cb(layer.read())
        filtered_layer = Layer(layer.layer_type, layer.connection)
        filtered_layer.write(df)
        return filtered_layer

def s3_filter(s3, request_state):
    mask = s3[s3.state.str.contains(request_state)][['pid', 'id']].drop_duplicates()
    return pd.merge(s3, mask, on=['pid', 'id'], how='inner')

def s3putobject_filter(s3):
    return s3_filter(s3, 'S3PutObjectAction')

def s3getobject_filter(s3):
    return s3_filter(s3, 'S3GetObjectAction')

# List of supported Layers types:

# [+] stio_req
# [+] rpc_req
# [-] fom_req_state
# [+] fom_req
# [-] rpc_post_reply
# [+] be_tx
# [+] dix_req
# [+] cas_req
# [+] client_req
# [+] s3_request_state
# [+] cob_req
# [+] ioo_req

S3       = TypeId('S3', 's3_request_state')
MOTR_REQ = TypeId('MotrReq', 'client_req')
COB      = TypeId('COB', 'cob_req')
CAS      = TypeId('CAS', 'cas_req')
DIX      = TypeId('DIX', 'dix_req')
IOO      = TypeId('IOO', 'ioo_req')
CRPC     = TypeId('CRPC', 'rpc_req')
SRPC     = TypeId('SRPC', 'rpc_req')
FOM      = TypeId('FOM', 'fom_req')
STIO     = TypeId('STIO', 'stio_req')
BETX     = TypeId('BETX', 'be_tx')

S3PUT_FILTER = Filter('S3PutObject', s3putobject_filter)
S3GET_FILTER = Filter('S3GetObject', s3getobject_filter)

BINS = 50
PERCENTILE = 0.95

class Histogram():
    BINS = 100
    PERCENTILE = 0.95
    MILLISECOND_SCALE = 10**6

    def __init__(self, layer, start, stop, bins=BINS, percentile=PERCENTILE):
        self.layer = layer
        self.bins = bins
        self.percentile = percentile
        self.start_states = start
        self.stop_states = stop
        self.hist = None
        self.name = f"{self.layer.layer_type.name}: {self.start_states} -> {self.stop_states}, ms"

    def __process_states(self, df, states, inverse=False):
        acc = pd.DataFrame()
        for s in states:
            tmp = df[(df.state == s)]
            acc = pd.concat([acc, tmp], ignore_index=True)
        if inverse:
            acc['time'] = -acc['time']
        acc.sort_values('time', inplace=True)
        acc.drop_duplicates(subset=['pid', 'id', 'state'], keep='first', inplace=True)
        return acc

    def calculate(self):
        df = self.layer.read()
        start = self.__process_states(df, self.start_states, inverse=True)
        stop = self.__process_states(df, self.stop_states)
        df = pd.concat([start,stop], ignore_index=True)
        gb = df.groupby(['pid','id']).agg({'time': [np.sum]})
        gb.reset_index(inplace=True)
        gb['delta'] = [x/self.MILLISECOND_SCALE for x in gb[('time', 'sum')]]
        self.hist = gb['delta']
        self.hist = self.hist[self.hist > 0]

    def hist_df(self):
        return self.hist

    def draw(self, fig, ax, color):
        df = self.hist
        df[df > 0][df < df.quantile(self.percentile)].hist(bins=self.bins, alpha=0.5, figure=fig, ax=ax, color=color)

        textstr = df.describe().to_string()
        text = textstr.split('\n')
        textstr = ''
        for i in range(len(text)):
            t = text[i].split(' ')
            textstr = textstr + t[0] + ": " + t[-1]
            if i < (len(text) - 1):
                textstr = textstr + '\n'

        handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white",
                                         lw=0, alpha=0)]
        labels = []
        labels.append(textstr)
        ax.legend(handles, labels, loc='upper right', prop={'size': 8},
                  fancybox=True, framealpha=0.7,
                  handlelength=0, handletextpad=0)


    def name(self):
        return self.name

    def merge(self, histogram):
        self.hist = pd.concat([self.hist, histogram.hist], ignore_index=True)
        self.hist.reset_index(drop=True)


class Relation():
    def __init__(self, relation_type, connection):
        self.relation_type = relation_type
        self.connection = connection
        self.df = None

    def read(self):
        if self.df is None:
            query = f'SELECT * FROM relation where type_id="{self.relation_type.type_id}"'
            df = sql.read_sql(query, con=self.connection.get())
            self.df = df.loc[:,~df.columns.duplicated()]
        return self.df

    def sieve(self, upper_layer, next_layer):
        upper_df = upper_layer.read()
        next_df = next_layer.read()
        rel_df = self.read()

        mask_rel = upper_df[['pid', 'id']].drop_duplicates()
        src_mask = pd.merge(rel_df, mask_rel, how='inner', left_on=['pid1', 'mid1'], right_on=['pid', 'id'])
        src_mask.drop_duplicates(inplace=True)
        result_df = pd.merge(next_df, src_mask[['pid2', 'mid2']], how='inner', left_on=['pid', 'id'], right_on=['pid2', 'mid2'])
        result_df.drop_duplicates(inplace=True)
        result_df.drop('pid2', 1, inplace=True)
        result_df.drop('mid2', 1, inplace=True)

        result = Layer(next_layer.layer_type, next_layer.connection)
        result.write(result_df)

        return result


# List of available relations:
#
# [+] sxid_to_rpc
# [+] rpc_to_sxid
# [+] rpc_to_fom
# [-] tx_to_gr
# [+] fom_to_tx
# [-] cas_fom_to_crow_fom
# [+] fom_to_stio
# [+] dix_to_mdix
# [+] dix_to_cas
# [+] cas_to_rpc
# [+] client_to_dix
# [+] s3_request_to_client
# [+] client_to_cob
# [+] cob_to_rpc
# [+] client_to_ioo
# [-] bulk_to_rpc
# [+] ioo_to_rpc

S3_TO_CLIENT  = TypeId('S3 to Motr client request', 's3_request_to_client')
CLIENT_TO_DIX = TypeId('Motr client request to DIX request', 'client_to_dix')
DIX_TO_MDIX   = TypeId('DIX request to MDIX request', 'dix_to_mdix')
DIX_TO_CAS    = TypeId('DIX request to CAS request', 'dix_to_cas')
CAS_TO_CRPC   = TypeId('CAS request to CPRC request', 'cas_to_rpc')
CLIENT_TO_COB = TypeId('Motr client request to COB request', 'client_to_cob')
COB_TO_CRPC   = TypeId('COB request to CPRC request', 'cob_to_rpc')
CLIENT_TO_IOO = TypeId('Motr client request to IOO request', 'client_to_ioo')
IOO_TO_CRPC   = TypeId('IOO request to CPRC request', 'ioo_to_rpc')
RPC_TO_SXID   = TypeId('RPC request to Session & Transfer ID', 'rpc_to_sxid')
SXID_TO_RPC   = TypeId('Session & Transfer ID to RPC request', 'sxid_to_rpc')
SRPC_TO_FOM   = TypeId('SRPC request to FOM', 'rpc_to_fom')
FOM_TO_STIO   = TypeId('FOM to STOB IO request', 'fom_to_stio')
FOM_TO_TX     = TypeId('FOM to BE TX request', 'fom_to_tx')


class XIDRelation():
    def __init__(self,  connection):
        self.connection = connection
        self.rpc_to_sxid = Relation(RPC_TO_SXID, connection)
        self.sxid_to_rpc = Relation(SXID_TO_RPC, connection)
        self.df = None

    def read(self):
        if self.df is None:
            df1 = self.rpc_to_sxid.read()
            df2 = self.sxid_to_rpc.read()
            self.df = pd.concat([df1, df2], ignore_index=True)
        return self.df

    def sieve(self, upper_layer, next_layer):
        crpc = upper_layer.read()
        rpc = next_layer.read()
        relations = self.read()

        crpc_mask = crpc[['pid', 'id']].drop_duplicates()
        sxids = pd.merge(crpc_mask, relations, how='inner', left_on=['pid', 'id'], right_on=['pid1', 'mid1'])
        sxids = sxids[['pid2', 'mid2']].drop_duplicates()
        sxids.rename(columns={'pid2': 'pid', 'mid2': 'id'}, inplace=True)
        srpc_mask = pd.merge(sxids, relations, how='inner', left_on=['pid', 'id'], right_on=['pid1', 'mid1'])
        srpc_mask = srpc_mask[['pid2', 'mid2']].drop_duplicates()
        srpc = pd.merge(rpc, srpc_mask, how='inner', left_on=['pid', 'id'], right_on=['pid2', 'mid2'])
        srpc.drop_duplicates(inplace=True)
        srpc.drop('pid2', 1, inplace=True)
        srpc.drop('mid2', 1, inplace=True)

        result = Layer(next_layer.layer_type, next_layer.connection)
        result.write(srpc)

        return result

class Plot():
    def __init__(self, hist, ax):
        self.hist = hist
        self.ax = ax

    def name(self):
        return self.hist.name

class Figure():
    COLORS = ['g', 'b', 'r', 'c', 'm']
    color_idx = 0
    figure_idx = 0

    @staticmethod
    def next_figure():
        Figure.figure_idx = Figure.figure_idx + 1

    def next_color(self):
        color = Figure.COLORS[self.color_idx]
        self.color_idx = (self.color_idx + 1) % len(Figure.COLORS)
        return color

    def __init__(self, name, rows, cols):
        self.mpl_idx = Figure.next_figure()
        self.fig = plt.figure(self.mpl_idx, constrained_layout=True, figsize=(20, 10))
        self.mpl_plt = plt
        self.layout = self.fig.add_gridspec(rows, cols)
        self.rows = rows
        self.cols = cols
        self.name = name
        self.filename = name.replace(' ', '_') + ".png"
        self.plots = []
        self.mpl_plt.suptitle(self.name)

    def add(self, hist, row, col, sharex=None, sharey=None):
        ax = self.fig.add_subplot(self.layout[row, col], sharex=sharex, sharey=sharey)
        self.plots.append(Plot(hist, ax))
        return ax

    def draw(self):
        for plot in self.plots:
            print(f"plotting: {plot.hist.name}")
            plot.hist.draw(self.fig, plot.ax, self.next_color())
            plot.ax.set_title(plot.hist.name)

    def show(self):
        self.mpl_plt.show()

    def save(self):
        self.fig.savefig(self.filename, format="png")

def calculate(conn, fiter, save_only):
    s3fig = Figure(f"{fiter.name} system histograms", 4, 2)
    mfig = Figure(f"{fiter.name} Motr histograms", 6, 3)

    s3all = Layer(S3, conn)
    #s3 = S3PUT_FILTER.run(s3all)
    s3 = fiter.run(s3all)
    s3hist = Histogram(s3, ["START"], ["COMPLETE"], bins=50, percentile=0.90)
    s3hist.calculate()
    s3fig.add(s3hist, 0, 0)
    # Cleanup
    del s3all
    gc.collect()

    rel = Relation(S3_TO_CLIENT, conn)
    motr_all = Layer(MOTR_REQ, conn)
    motr = rel.sieve(s3, motr_all)
    motr_hist = Histogram(motr, ["initialised"], ['stable'])
    motr_hist.calculate()
    axs = s3fig.add(motr_hist, 1, 0)
    # Cleanup
    del motr_all
    gc.collect()

    ioo_all = Layer(IOO, conn)
    rel = Relation(CLIENT_TO_IOO, conn)
    ioo = rel.sieve(motr, ioo_all)
    del ioo_all
    gc.collect()
    ioo_hist = Histogram(ioo, ['IO_initial'], ['IO_req_complete'])
    ioo_hist.calculate()
    axm = mfig.add(ioo_hist, 0, 0)

    cob_all = Layer(COB, conn)
    rel = Relation(CLIENT_TO_COB, conn)
    cob = rel.sieve(motr, cob_all)
    del cob_all
    gc.collect()
    cob_hist = Histogram(cob, ['COB_REQ_ACTIVE'], ['COB_REQ_DONE'])
    cob_hist.calculate()
    mfig.add(cob_hist, 0, 1, sharex=axm)

    dix_all = Layer(DIX, conn)
    rel_dix = Relation(CLIENT_TO_DIX, conn)
    rel_mdix = Relation(DIX_TO_MDIX, conn)
    dix = rel_dix.sieve(motr, dix_all)
    mdix = rel_mdix.sieve(dix, dix_all)

    cas_all = Layer(CAS, conn)
    rel_cas = Relation(DIX_TO_CAS, conn)
    cas = rel_cas.sieve(dix, cas_all)
    cas2 = rel_cas.sieve(mdix, cas_all)
    cas.merge(cas2)

    del dix_all
    del cas_all
    del mdix
    del dix
    del rel_dix
    del rel_mdix
    gc.collect()
    cas_hist = Histogram(cas, ['init'], ['final', 'failure'])
    cas_hist.calculate()
    mfig.add(cas_hist, 0, 2, sharex=axm)

    rpc_all = Layer(CRPC, conn)
    rel_ioo = Relation(IOO_TO_CRPC, conn)
    rel_cob = Relation(COB_TO_CRPC, conn)
    rel_cas = Relation(CAS_TO_CRPC, conn)
    crpc_ioo = rel_ioo.sieve(ioo, rpc_all)
    crpc_cob = rel_cob.sieve(cob, rpc_all)
    crpc_cas = rel_cas.sieve(cas, rpc_all)

    crpc_ioo_hist = Histogram(crpc_ioo, ['INITIALISED'], ['REPLIED'])
    crpc_ioo_hist.calculate()
    mfig.add(crpc_ioo_hist, 1, 0, sharex=axm)

    crpc_cob_hist = Histogram(crpc_cob, ['INITIALISED'], ['REPLIED'])
    crpc_cob_hist.calculate()
    mfig.add(crpc_cob_hist, 1, 1, sharex=axm)

    crpc_cas_hist = Histogram(crpc_cas, ['INITIALISED'], ['REPLIED'])
    crpc_cas_hist.calculate()
    mfig.add(crpc_cas_hist, 1, 2, sharex=axm)

    crpc_hist = Histogram(crpc_ioo, ['INITIALISED'], ['REPLIED'])
    crpc_hist.calculate()
    crpc_hist.merge(crpc_cob_hist)
    crpc_hist.merge(crpc_cas_hist)
    s3fig.add(crpc_hist, 2, 0, sharex=axs)

    del rel_ioo
    del rel_cob
    del rel_cas
    del rpc_all

    rpc_all = Layer(SRPC, conn)
    rel = XIDRelation(conn)
    srpc_ioo = rel.sieve(crpc_ioo, rpc_all)
    srpc_cob = rel.sieve(crpc_cob, rpc_all)
    srpc_cas = rel.sieve(crpc_cas, rpc_all)

    del rpc_all
    del crpc_ioo
    del crpc_cas
    del crpc_cob
    del rel
    gc.collect()

    srpc_ioo_hist = Histogram(srpc_ioo, ['INITIALISED'], ['REPLIED'])
    srpc_ioo_hist.calculate()
    axm = mfig.add(srpc_ioo_hist, 2, 0)

    srpc_cob_hist = Histogram(srpc_cob, ['INITIALISED'], ['REPLIED'])
    srpc_cob_hist.calculate()
    mfig.add(srpc_cob_hist, 2, 1, sharex=axm)

    srpc_cas_hist = Histogram(srpc_cas, ['INITIALISED'], ['REPLIED'])
    srpc_cas_hist.calculate()
    mfig.add(srpc_cas_hist, 2, 2, sharex=axm)

    srpc_hist = Histogram(srpc_ioo, ['INITIALISED'], ['REPLIED'])
    srpc_hist.calculate()
    srpc_hist.merge(srpc_cob_hist)
    srpc_hist.merge(srpc_cas_hist)
    axs = s3fig.add(srpc_hist, 0, 1)

    fom_all = Layer(FOM, conn)
    rel = Relation(SRPC_TO_FOM, conn)
    fom_ioo = rel.sieve(srpc_ioo, fom_all)
    fom_cob = rel.sieve(srpc_cob, fom_all)
    fom_cas = rel.sieve(srpc_cas, fom_all)
    del fom_all
    del rel
    gc.collect()

    fom_ioo_hist = Histogram(fom_ioo, ['0', '-1'], ['finish'])
    fom_ioo_hist.calculate()
    mfig.add(fom_ioo_hist, 3, 0, sharex=axm)

    fom_cob_hist = Histogram(fom_cob, ['0', '-1'], ['finish'])
    fom_cob_hist.calculate()
    mfig.add(fom_cob_hist, 3, 1, sharex=axm)

    fom_cas_hist = Histogram(fom_cas, ['0', '-1'], ['finish'])
    fom_cas_hist.calculate()
    mfig.add(fom_cas_hist, 3, 2, sharex=axm)

    fom_hist = Histogram(fom_ioo, ['0', '-1'], ['finish'])
    fom_hist.calculate()
    fom_hist.merge(fom_cob_hist)
    fom_hist.merge(fom_cas_hist)
    s3fig.add(fom_hist, 1, 1, sharex=axs)

    stio_all = Layer(STIO, conn)
    rel = Relation(FOM_TO_STIO, conn)
    stio_ioo = rel.sieve(fom_ioo, stio_all)
    stio_cob = rel.sieve(fom_cob, stio_all)
    stio_cas = rel.sieve(fom_cas, stio_all)
    del stio_all
    del rel
    gc.collect()

    stio_ioo_hist = Histogram(stio_ioo, ['M0_AVI_IO_LAUNCH'], ['M0_AVI_AD_ENDIO'])
    stio_ioo_hist.calculate()
    mfig.add(stio_ioo_hist, 4, 0, sharex=axm)
    s3fig.add(stio_ioo_hist, 2, 1, sharex=axs)

    del stio_ioo
    gc.collect()

    # Only for writes
    if fiter is S3PUT_FILTER:
        betx_all = Layer(BETX, conn)
        rel = Relation(FOM_TO_TX, conn)
        betx_ioo = rel.sieve(fom_ioo, betx_all)
        betx_cob = rel.sieve(fom_cob, betx_all)
        betx_cas = rel.sieve(fom_cas, betx_all)
        del betx_all
        del rel
        gc.collect()

        betx_ioo_hist = Histogram(betx_ioo, ['prepare'], ['done'])
        betx_ioo_hist.calculate()
        mfig.add(betx_ioo_hist, 5, 0, sharex=axm)

        betx_cob_hist = Histogram(betx_cob, ['prepare'], ['done'])
        betx_cob_hist.calculate()
        mfig.add(betx_cob_hist, 5, 1, sharex=axm)

        betx_cas_hist = Histogram(betx_cas, ['prepare'], ['done'])
        betx_cas_hist.calculate()
        mfig.add(betx_cas_hist, 5, 2, sharex=axm)

        betx_hist = Histogram(betx_ioo, ['prepare'], ['done'])
        betx_hist.calculate()
        betx_hist.merge(betx_cob_hist)
        betx_hist.merge(betx_cas_hist)
        s3fig.add(betx_hist, 3, 1, sharex=axs)

    s3fig.draw()
    mfig.draw()

    s3fig.save()
    mfig.save()

    if not save_only:
        s3fig.show()
        mfig.show()

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    system_hist.py: Generate histograms of Cortx S3 and Motr layers
    """)

    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-g",'--s3get', action='store_true', help="Show histograms of S3GetObject operation")
    parser.add_argument("-p", "--s3put", action='store_true', help="Show histograms of S3GetObject operation")
    parser.add_argument("-s", "--save-only", action='store_true', help="Don't show figures, only save")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    pandas_init()

    conn = Connection(args.db)

    if not args.s3get and not args.s3put:
        args.s3get = True
        args.s3put = True

    if args.s3put:
        calculate(conn, S3PUT_FILTER, args.save_only)

    if args.s3get:
        calculate(conn, S3GET_FILTER, args.save_only)

    return

if __name__ == "__main__":
    main()

