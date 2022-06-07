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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from pandas.io import sql
import sqlite3
import re

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
    def __init__(self, layer_type, connection, start=None, stop=None):
        self.layer_type = layer_type
        self.connection = connection
        self.df = None
        self.start = start
        self.stop = stop

    def write(self, df):
        self.df = df

    def read(self):
        if self.df is None:
            if self.start is not None and self.stop is not None:
                query = f'SELECT * FROM request where type_id="{self.layer_type.type_id}" and time > {self.start} and time < {self.stop}'
            elif self.start is not None:
                query = f'SELECT * FROM request where type_id="{self.layer_type.type_id}" and time > {self.start}'
            elif self.stop is not None:
                query = f'SELECT * FROM request where type_id="{self.layer_type.type_id}" and time < {self.stop}'
            else:
                query = f'SELECT * FROM request where type_id="{self.layer_type.type_id}"'
            df = sql.read_sql(query, con=self.connection.get())
            self.df = df.loc[:,~df.columns.duplicated()]
        return self.df

    def merge(self, layer):
        self.df = pd.concat([self.read(), layer.read()], ignore_index=True)

    def pids(self):
        return list(set(self.df['pid'].to_list()))

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
    MICROSECOND_SCALE = 10**3

    def __init__(self, layer, start, stop, bins=BINS, percentile=PERCENTILE, pids=None, scale='ms'):
        self.layer = layer
        self.bins = bins
        self.percentile = percentile
        self.start_states = start
        self.stop_states = stop
        self.hist = None
        self.pids = pids
        self.scale_name = scale
        if self.scale_name=='ms':
            self.scale = self.MILLISECOND_SCALE
        elif self.scale_name=='us':
            self.scale = self.MICROSECOND_SCALE
        self.name = f"{self.layer.layer_type.name}: {self.start_states} -> {self.stop_states}, {self.scale_name}"

    @staticmethod
    def __process_states(df, states, inverse=False):
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
        if self.pids is not None:
            df = df[(df.pid.isin(self.pids))]
        start = self.__process_states(df, self.start_states, inverse=True)
        stop = self.__process_states(df, self.stop_states)
        df = pd.concat([start,stop], ignore_index=True)
        gb = df.groupby(['pid','id']).agg({'time': [np.sum]})
        gb.reset_index(inplace=True)
        gb['delta'] = [x/self.scale for x in gb[('time', 'sum')]]
        self.hist = gb['delta']
        self.hist = self.hist[self.hist > 0]

    def hist_df(self):
        return self.hist

    def draw(self, fig, ax, color):
        df = self.hist
        df[df > 0][df < df.quantile(self.percentile)].hist(bins=self.bins, alpha=0.5, figure=fig, ax=ax, color=color)

        q80 = df.quantile(0.8)
        q90 = df.quantile(0.9)
        q95 = df.quantile(0.95)
        q99 = df.quantile(0.99)
        q995 = df.quantile(0.995)
        q998 = df.quantile(0.998)
        q999 = df.quantile(0.999)

        textstr = df.describe().to_string()
        text = textstr.split('\n')
        textstr = ''
        for i in range(len(text)-1):
            t = text[i].split(' ')
            textstr = textstr + t[0] + ": " + t[-1] + '\n'
        textstr = textstr + "80%: "   + "{:.2f}".format(q80) + "\n"
        textstr = textstr + "90%: "   + "{:.2f}".format(q90) + "\n"
        textstr = textstr + "95%: "   + "{:.2f}".format(q95) + "\n"
        textstr = textstr + "99%: "   + "{:.2f}".format(q99) + "\n"
        textstr = textstr + "99.5%: " + "{:.2f}".format(q995) + "\n"
        textstr = textstr + "99.8%: " + "{:.2f}".format(q998) + "\n"
        textstr = textstr + "99.9%: " + "{:.2f}".format(q999) + "\n"
        textstr = textstr + text[-1].split(' ')[0] + ": " + text[-1].split(' ')[-1]

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
        return Figure.figure_idx

    def next_color(self):
        color = Figure.COLORS[self.color_idx]
        self.color_idx = (self.color_idx + 1) % len(Figure.COLORS)
        return color

    def __init__(self, name, rows, cols):
        self.mpl_idx = Figure.next_figure()
        self.fig = plt.figure(self.mpl_idx, figsize=(20, 10))
        self.mpl_plt = plt
        self.layout = self.fig.add_gridspec(rows, cols)
        self.rows = rows
        self.cols = cols
        self.name = name
        filename = name.replace(' ', '_')
        filename = filename.replace('-', '_')
        filename = filename + ".png"
        self.filename = filename
        self.plots = []
        self.axes = dict()
        self.mpl_plt.suptitle(self.name)

    def add(self, hist, row, col, sharex=None, sharey=None):
        if (row, col) in self.axes:
            ax = self.axes[(row, col)]
        else:
            ax = self.fig.add_subplot(self.layout[row, col], sharex=sharex, sharey=sharey)
            self.axes[(row, col)] = ax
        self.plots.append(Plot(hist, ax))
        return ax

    def draw(self):
        for plot in self.plots:
            plot.hist.draw(self.fig, plot.ax, self.next_color())
            if plot.hist.name:
                plot.ax.set_title(plot.hist.name)

    def show(self):
        self.mpl_plt.figure(self.mpl_idx)
        self.mpl_plt.subplots_adjust(left=0.04,
                                     bottom=0.06,
                                     right=0.99,
                                     top=0.92,
                                     wspace=0.11,
                                     hspace=0.11)
        self.mpl_plt.show()

    @staticmethod
    def show_plt():
        plt.show()

    def save(self):
        self.mpl_plt.figure(self.mpl_idx)
        self.mpl_plt.subplots_adjust(left=0.04,
                                     bottom=0.06,
                                     right=0.99,
                                     top=0.92,
                                     wspace=0.11,
                                     hspace=0.11)
        self.fig.savefig(self.filename, format="png")

class Queue():
    def __init__(self, layer, start, stop, pids=None):
        self.layer = layer
        self.start_states = start
        self.stop_states = stop
        self.queue = pd.DataFrame()
        self.rps_in = pd.DataFrame()
        self.rps_out = pd.DataFrame()
        self.name = f"{self.layer.layer_type.name}: {self.start_states} -> {self.stop_states}, ms"
        self.name = None
        self.label = ''
        self.pids = pids

    @staticmethod
    def __df_prepare(df, states, val, rule='first'):
        df = df[(df.state.isin(states))]
        df.drop_duplicates(subset=['pid', 'id', 'state'],
                           keep=rule, inplace=True)
        df = df[['time','state']]
        df.set_index('time', inplace=True)
        df['state'] = val
        df = df.sort_values('time')
        df.index = [pd.Timestamp(x, unit='ns') for x in df.index]
        return df

    def __filter_queue(self, df):
        up = df[(df.state.isin(self.start_states))]
        down = df[(df.state.isin(self.stop_states))]

        up_mask = up[['pid', 'id']].drop_duplicates()
        down_mask = down[['pid', 'id']].drop_duplicates()
        mask = pd.merge(up_mask, down_mask, how='inner', on=['pid','id'])
        mask = mask[['pid', 'id']].drop_duplicates()

        df = pd.merge(df, mask, how='inner', on=['pid','id'])
        return df

    def calculate(self):
        df = self.layer.read()
        if self.pids is not None:
            df = df[(df.pid.isin(self.pids))]
        df = self.__filter_queue(df)
        df_in = self.__df_prepare(df, self.start_states, 1)
        df_out = self.__df_prepare(df, self.stop_states, -1, rule='last')
        df = pd.concat([df_in, df_out])
        df = df.sort_index().cumsum()
        nl = '\n'
        self.label = f'{self.layer.layer_type.name}{nl}{self.start_states} -> {self.stop_states}'
        df.rename(columns={"state": self.label}, inplace=True)
        self.queue = df

    def draw(self, fig, ax, color):
        df = self.queue
        if df.empty:
            return
        ax = df.plot(alpha=0.5, figure=fig, ax=ax, color=color, grid=True)
        ax.legend(loc="upper right")
        ymax = df[self.label].max()
        ax.set_ylim([0, ymax * 2] )

    def name(self):
        return self.name

class RPS():
    def __init__(self, layer, states, avg_window='1s',
                 color=None, rule='first', pids=None):
        self.layer = layer
        self.states = states
        self.rps = pd.DataFrame()
        self.window = avg_window
        self.color = color
        self.name = None
        self.label = ''
        self.keep_rule = rule
        self.pids = pids

    def __calc_rps(self, df):
        # Average window field is variable, and scale must be normilized, so
        # resulting rolling sum shows results as requests per second.
        # Using the formula:
        # 1 RPS = N * avg_window,
        # where N is the scale coefficient
        # avg_window is an averaging window and it has dimension
        # of 1 Request per [avg_window]
        # If window is 1 second, then rolling sum shows the number
        # of requests per 1 second, and N = 1.
        # If window is 100 ms, it shows the number of requests per 100ms,
        # or 0.1 seconds, and N = 10.
        UNITS = {'s': 1, 'ms': 1000, 'us': 1000000, 'ns': 1000000000}
        r = re.split('(\d+)', self.window)
        unit = r[2]
        scale = int(r[1])
        N = UNITS[unit] / scale
        df['state'] = N
        df = df.rolling(self.window).sum()
        return df

    def __df_prepare(self, df, states, val, rule='first'):
        df = df[(df.state.isin(states))]
        df.drop_duplicates(subset=['pid', 'id', 'state'], keep=rule, inplace=True)
        df = df[['time','state']]
        df.set_index('time', inplace=True)
        df['state'] = val
        df = df.sort_values('time')
        df.index = [pd.Timestamp(x, unit='ns') for x in df.index]
        return df

    def calculate(self):
        df = self.layer.read()
        if self.pids is not None:
            df = df[(df.pid.isin(self.pids))]

        df = self.__df_prepare(df, self.states, 1, self.keep_rule)
        rps = self.__calc_rps(df)
        self.label = f"{self.layer.layer_type.name}: {self.states}"
        rps.rename(columns={"state": self.label}, inplace=True)
        self.rps = rps

    def draw(self, fig, ax, color):
        if self.color:
            color = self.color
        if self.rps.empty:
            return
        ax = self.rps.plot(alpha=0.5, figure=fig, ax=ax, color=color, grid=True)
        ax.legend(loc="upper right")
        ymax = self.rps[self.label].max()
        ax.set_ylim([0, ymax * 2] )

    def name(self):
        return self.name

class Latency():
    MILLISECOND_SCALE = 10**6
    MICROSECOND_SCALE = 10**3

    def __init__(self, layer, start, stop, pids=None, scale='ms',
                 avg_window='1s'):
        self.layer = layer
        self.start_states = start
        self.stop_states = stop
        self.latency = pd.DataFrame()
        self.pids = pids
        self.scale_name = scale
        if self.scale_name=='ms':
            self.scale = self.MILLISECOND_SCALE
        elif self.scale_name=='us':
            self.scale = self.MICROSECOND_SCALE
        self.name = ''
        self.label = 'test0'
        self.window = avg_window
        self.color = None

    def __process_states(self, df, states, inverse=False, rule='first'):
        acc = pd.DataFrame()
        for s in states:
            tmp = df[(df.state == s)]
            acc = pd.concat([acc, tmp], ignore_index=True)
        if inverse:
            acc['time'] = -acc['time']
        acc.sort_values('time', inplace=True)
        acc.drop_duplicates(subset=['pid', 'id', 'state'], keep=rule, inplace=True)
        return acc

    def calculate(self):
        df = self.layer.read()
        if self.pids is not None:
            df = df[(df.pid.isin(self.pids))]
        start = self.__process_states(df, self.start_states, inverse=True)
        stop = self.__process_states(df, self.stop_states)
        df = pd.concat([start,stop], ignore_index=True)
        df['delta'] = df.groupby(['pid','id'])['time'].transform('sum') / self.scale
        df = df[df.time > 0]
        df = df[df.delta > 0]
        df = df[['time', 'delta']]
        df.set_index('time', inplace=True)
        df = df.sort_values('time')
        df.index = [pd.Timestamp(x, unit='ns') for x in df.index]
        nl = '\n'
        self.label = f'{self.layer.layer_type.name}{nl}{self.start_states} -> {self.stop_states}'
        df.rename(columns={"delta": self.label}, inplace=True)
        self.latency = df.rolling(self.window).mean()

    def draw(self, fig, ax, color):
        if self.color:
            color = self.color
        if self.latency.empty:
            return
        ax = self.latency.plot(alpha=0.5, figure=fig,
                               ax=ax, color=color, grid=True)
        ax.legend(loc="upper right")
        ymax = self.latency[self.label].max()
        ax.set_ylim([0, ymax * 2] )

    def name(self):
        return self.name

    def merge(self, latency):
        self.latency = pd.concat([self.latency, histogram.latency], ignore_index=True)
        self.latency.reset_index(drop=True)

class Attr():
    def __init__(self, connection, attributes):
        self.connection = connection
        self.attrs = attributes
        self.df = None

    def read(self):
        if self.df is None:
            query = 'select * from attr where'
            for i, attr in enumerate(self.attrs):
                query = query + f" name='{attr}' "
                if i != (len(self.attrs) - 1):
                    query = query + ' or '
                else:
                    query = query + ';'
            df = sql.read_sql(query, con=self.connection.get())
            self.df = df.loc[:,~df.columns.duplicated()]
        return self.df

class MBPS():
    MB_SCALE = 10**6
    def __init__(self, layer, attr, states, op, avg_window='1s',
                 color=None, rule='first', pids=None):
        self.layer = layer
        self.mbps = pd.DataFrame()
        self.window = avg_window
        self.color = color
        self.name = None
        self.label = ''
        self.keep_rule = rule
        self.pids = pids
        self.attr = attr
        self.attr_cache = None
        self.states = states
        self.op = op

    def calculate(self):
        if self.attr_cache is None:
            df = self.attr.read()
            df.rename(columns = {'entity_id': 'id'}, inplace=True)
            df['val'] = df['val'].astype(int)
            df['MB'] = df.groupby(['pid', 'id'])['val'].transform(self.op) / self.MB_SCALE
            df = df[['pid', 'id', 'MB']].drop_duplicates()
        else:
            df = self.attr_cache

        layer = self.layer.read()
        layer = layer[(layer.state.isin(self.states))]

        merge = pd.merge(layer, df, how='inner', on=['pid', 'id'])

        df = merge[['time', 'pid', 'id', 'MB']]
        df.set_index('time', inplace=True)
        df = df.sort_values('time')
        df.index = [pd.Timestamp(x, unit='ns') for x in df.index]

        if self.pids is not None:
            df = df[(df.pid.isin(self.pids))]

        UNITS = {'s': 1, 'ms': 1000, 'us': 1000000, 'ns': 1000000000}
        r = re.split('(\d+)', self.window)
        unit = r[2]
        scale = int(r[1])
        N = UNITS[unit] / scale
        t = df['MB'] * N;
        mbps = t.rolling(self.window).sum()
        self.pids = df['pid']
        self.label = f"{self.layer.layer_type.name}"
        mbps.rename(self.label, inplace=True)
        self.mbps = mbps

    def filter_pids(self, pids):
        pass

    def draw(self, fig, ax, color):
        if self.color:
            color = self.color
        if self.mbps.empty:
            return
        ax = self.mbps.plot(alpha=0.5, figure=fig, ax=ax, color=color, grid=True)
        ax.legend(loc="upper right")
        ymax = self.mbps.max()
        ax.set_ylim([0, ymax * 2] )

    def name(self):
        return self.name

    def get_pids(self):
        return list(set(self.pids.to_list()))
