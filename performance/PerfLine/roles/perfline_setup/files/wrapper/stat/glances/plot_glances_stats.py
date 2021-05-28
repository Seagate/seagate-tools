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
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import re


TEMPLATE_PLACEHOLDER = '[TEMPLATE]'
HOSTNAME_PLACEHOLDER = '[HOSTNAME]'
DEFAULT_FIGURE_SIZE = (12, 6)

HOSTNAME = None


def get_val_from_template(template, val):
    result = template.replace(TEMPLATE_PLACEHOLDER, str(val))
    result = result.replace(HOSTNAME_PLACEHOLDER, HOSTNAME)
    return result


class GraphPlotter:

    DISPLAY_OPT_PERCENT = 'percent'
    DISPLAY_OPT_MB = 'MB'
    DISPLAY_OPT_GB = 'GB'

    BYTES_PER_MB = 2 ** 20
    BYTES_PER_GB = 2 ** 30

    RANGE_ITER_PATTERN = r'\[(?P<start>\d+)\.\.(?P<end>\d+)\]'
    LIST_ITER_PATTERN = r'\[(.+)\]'

    def _prepare_metrics_list(self, metrics, index):
        metrics = [get_val_from_template(x, index) for x in metrics]
        result = []

        for m in metrics:
            re_range_result = re.search(self.RANGE_ITER_PATTERN, m)
            re_list_result = re.search(self.LIST_ITER_PATTERN, m)

            if re_range_result:
                template_part = re_range_result.group(0)
                start_val = int(re_range_result.group(1))
                end_val = int(re_range_result.group(2))

                for i in range(start_val, end_val + 1):
                    result.append(m.replace(template_part, str(i)))

            elif re_list_result:
                template_part = re_list_result.group(0)
                tmp_list = re_list_result.group(1).split(',')
                tmp_list = [x.strip() for x in tmp_list]

                for item in tmp_list:
                    result.append(m.replace(template_part, item))
            else:
                result.append(m)
        
        return result

    def __init__(self, df, axs, graph_desc, index):
        self.df = df
        self.axs = axs
        self.metrics = self._prepare_metrics_list(graph_desc['metrics'], index)
        self.title = get_val_from_template(graph_desc['title'], index)
        self.ylabel = graph_desc['y_label'] if 'y_label' in graph_desc else None
        self.display_option = graph_desc['display_as'] if 'display_as' in graph_desc else None
        self.show_legend = graph_desc['show_legend'] if 'show_legend' in graph_desc else True

    def plot(self):
        metrics_to_display = self.metrics

        if self.display_option == self.DISPLAY_OPT_PERCENT:
            self.axs.plot([0], [100])
        elif self.display_option == self.DISPLAY_OPT_GB:
            metrics_to_display = []
            for mm in self.metrics:
                self.df[f'{mm}_GB'] = self.df[mm] / self.BYTES_PER_GB
                metrics_to_display.append(f'{mm}_GB')
        elif self.display_option == self.DISPLAY_OPT_MB:
            metrics_to_display = []
            for mm in self.metrics:
                self.df[f'{mm}_MB'] = self.df[mm] / self.BYTES_PER_MB
                metrics_to_display.append(f'{mm}_MB')
        elif self.display_option is not None:
            raise ValueError('unsupported display option')


        self.df = self.df[metrics_to_display]
        self.df.plot(ax=self.axs, legend=self.show_legend)

        if self.title:
            self.axs.set_title(self.title)

        if self.ylabel:
            self.axs.set_ylabel(self.ylabel)


class FigurePlotter:

    def __init__(self, df, figure_desc, index=None):
        self.df = df
        self.figure_desc = figure_desc
        self.index = index
        self.column_nr = len(figure_desc['columns'])
        self.row_nr = 0

        for column_desc in figure_desc['columns']:
            tmp_row_nr = len(column_desc['column'])
            self.row_nr = max(self.row_nr, tmp_row_nr)

        fig, axes = plt.subplots(self.row_nr, self.column_nr,
                                 figsize=DEFAULT_FIGURE_SIZE, sharex=True)
        self.fig = fig
        self.axes = axes

        self.fname = get_val_from_template(figure_desc['fname'], index)
        self.name = get_val_from_template(figure_desc['name'], index)


    def _get_axs(self, row_ind, col_ind):
        if self.row_nr == 1 and self.column_nr == 1:
            return self.axes
        elif self.row_nr == 1:
            return self.axes[col_ind]
        elif self.column_nr == 1:
            return self.axes[row_ind]
        else:
            return self.axes[row_ind][col_ind]

    def plot(self):
        print('file: {}\nname: {}\n'.format(self.fname, self.name))

        for col_ind, column_desc in enumerate(self.figure_desc['columns']):
            for graph_ind, graph_desc in enumerate(column_desc['column']):
                ax = self._get_axs(graph_ind, col_ind)
                graph_plotter = GraphPlotter(self.df, ax, graph_desc['graph'],
                                             self.index)
                graph_plotter.plot()

        self.fig.autofmt_xdate()
        self.fig.savefig(self.fname)


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
        plot_glances_stats.py is tool for generating images that contain set
        of graphs of system stats provided by Glances utility.
        List of graphs and metrics on each image is described by user
        in yaml format.
    """)
    
    parser.add_argument("-y", "--yaml-schema", type=str, required=True,
                        help="yaml formatted schema of required graphs and metrics")
    
    parser.add_argument("-c", "--csv-data", type=str, required=True,
                        help="csv formatted data provided by glances utility")

    return parser.parse_args()


def prepare_df(csv_file):
    df = pd.read_csv(csv_file)
    df = df.set_index('timestamp')
    return df

def get_hostname(df):
    global HOSTNAME
    HOSTNAME = df['system_hostname'].iloc[0]


def plot_figures(df, figures_descs):
    for figure_desc in figures_descs:
        if 'iterate_by' in figure_desc['figure']:
            for ind in figure_desc['figure']['iterate_by']:
                plotter = FigurePlotter(df, figure_desc['figure'], ind)
                plotter.plot()
        elif 'iterate_for' in figure_desc['figure']:
            start = figure_desc['figure']['iterate_for']['start']
            end = figure_desc['figure']['iterate_for']['end']
            for ind in range(start, end):
                plotter = FigurePlotter(df, figure_desc['figure'], str(ind))
                plotter.plot()
        else:
            plotter = FigurePlotter(df, figure_desc['figure'])
            plotter.plot()


def main():
    args = parse_args()
    conf_path = args.yaml_schema
    csv_file = args.csv_data
    df = prepare_df(csv_file)
    get_hostname(df)

    with open(conf_path) as f:
        conf = yaml.safe_load(f.read())

    plot_figures(df, conf['figures'])


if __name__ == "__main__":
    main()
