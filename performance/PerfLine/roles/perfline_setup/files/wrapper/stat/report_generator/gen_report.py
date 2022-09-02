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

from os import listdir, getcwd, walk
from os.path import isdir, join, isfile

import fnmatch
import json
import sys
import datetime
import yaml
from jinja2 import Environment, FileSystemLoader

import pandas as pd
import csv
import itertools
import matplotlib.pyplot as plt

import iperf_log_parser
import m0crate_log_parser
exec(open("{}/../../../perfline.conf".format(sys.argv[2])).read())
# Helper functions


def replace_spaces_for_html(line):
    line = line.replace(' ', ' ')
    return line


def list_replace_spaces_for_html(lines):
    lines = [line.replace(' ', ' ') for line in lines]
    return lines


def replace_newline_for_html(line):
    line = line.replace('\n', '<br>')
    return line


def parse_commit_info(line):
    l1 = line.split('-')
    l2 = line.split('_')[1].split('.')[0]
    return replace_spaces_for_html(l1[0] + l1[1] + ': ' + l2)


# Info parsers

def parse_time(stat_result_dir):
    workload_start_time = ''
    workload_stop_time = ''
    test_start_time = ''
    test_stop_time = ''
    if isfile(join(stat_result_dir, 'common_stats.yaml')):
        with open(join(stat_result_dir, 'common_stats.yaml'), 'r') as common_stats:
            common_stats = yaml.safe_load(common_stats)
            workload_start_time = datetime.datetime.fromtimestamp(
                common_stats['workload_start_time']).strftime("%A, %d %B %Y %I:%M:%S%p")
            workload_stop_time = datetime.datetime.fromtimestamp(
                common_stats['workload_stop_time']).strftime("%A, %d %B %Y %I:%M:%S%p")
            test_start_time = datetime.datetime.fromtimestamp(
                common_stats['test_start_time']).strftime("%A, %d %B %Y %I:%M:%S%p")
            test_stop_time = datetime.datetime.fromtimestamp(
                common_stats['test_stop_time']).strftime("%A, %d %B %Y %I:%M:%S%p")
    return workload_start_time, workload_stop_time, test_start_time, test_stop_time


def parse_hardware_info(nodes_stat_dirs):
    mems = []
    cpu_info = []
    commit_info = []
    for path in nodes_stat_dirs:
        if isdir(join(path, 'hw')):
            if isfile(join(path, 'hw', 'cpu_info')):
                with open(join(path, 'hw/cpu_info'), 'r') as cpu_info_file:
                    lines = cpu_info_file.readlines()
                    lines = [replace_spaces_for_html(line) for line in lines]
                    cpu_info.append(lines)
            if isfile(join(path, 'hw/memory_info')):
                with open(join(path, 'hw/memory_info'), 'r') as memory_file:
                    mem_info = memory_file.readlines()[0]
                    mem_in_kb = mem_info.split()[1]
                    mems.append(mem_in_kb[:3] + '.' + mem_in_kb[3:] + ' GB')
            if isfile(join(path, 'hw/git_info')):
                with open(join(path, 'hw/git_info'), 'r') as commit_info_file:
                    lines = commit_info_file.readlines()
                    lines = [parse_commit_info(line)
                             for line in lines if 'cortx' in line]
                    commit_info.append(lines)
    return mems, cpu_info, commit_info


def get_pids(run_metadata, nodes_stat_dirs):

    if 'pids' not in run_metadata:
        return None

    pids_md = run_metadata['pids']

    result = list()

    for node_stats_path in nodes_stat_dirs:
        hostname = node_stats_path.split('/')[-1]

        node_pids = list()
        result.append(node_pids)

        if hostname in pids_md:
            for app_name, app_pids in pids_md[hostname].items():
                node_pids.extend(map(lambda pid: f"{app_name}: {pid}", app_pids))

    return result

def parse_network_info(nodes_stat_dirs):
    network_infos = []
    lnet_conf = []
    lnet_info = []
    multipath_conf = []
    multipath_info = []
    if isdir(join(nodes_stat_dirs[0], 'network')):
        for path in nodes_stat_dirs:
            if isfile(join(path, 'network/network_interfaces_info')):
                with open(join(path, 'network/network_interfaces_info'), 'r') as network_file:
                    lines = network_file.readlines()
                    lines = [replace_spaces_for_html(line) for line in lines]
                    network_infos.append(lines)

            # LNET
            if isfile(join(path, 'network/lnet.conf')):
                with open(join(path, 'network/lnet.conf'), 'r') as lnet_conf_file:
                    lnet_conf.append(lnet_conf_file.readlines())

            if isfile(join(path, 'network/lnet_info')):
                with open(join(path, 'network/lnet_info'), 'r') as lnet_info_file:
                    lnet_info.append(lnet_info_file.readlines())

            # Multipath
            if isfile(join(path, 'network/multipath.conf')):
                with open(join(path, 'network/multipath.conf'), 'r') as multipath_conf_file:
                    lines = multipath_conf_file.readlines()
                    lines = [replace_spaces_for_html(line) for line in lines]
                    multipath_conf.append(lines)

            if isfile(join(path, 'network/multipath_info')):
                with open(join(path, 'network/multipath_info'), 'r') as multipath_info_file:
                    lines = multipath_info_file.readlines()
                    lines = [replace_spaces_for_html(line) for line in lines]
                    multipath_info.append(lines)
    return network_infos, lnet_conf, lnet_info, multipath_conf, multipath_info


def parse_config_info(report_dir, node_names):
    motr_config = []
    cluster_nodes_info = []

    if isfile(join(report_dir, 'm0d/configs/cluster.yaml')):
        with open(join(report_dir, 'm0d/configs/cluster.yaml'), 'r') as cluster_file:
            cluster_yaml = yaml.safe_load(cluster_file)
            cluster_nodes_info = [n for n in cluster_yaml['nodes']]

    for node in node_names:
       if isfile(join(report_dir, 'm0d/configs/{}/motr'.format(node))):
           with open(join(report_dir, 'm0d/configs/{}/motr'.format(node)), 'r') as motr_config_file:
               motr_file = motr_config_file.readlines()
               motr_file = [conf for conf in motr_file if len(
                   conf.split('=')) == 2 and conf[0] != '#']
               motr_config.append(motr_file)
    return motr_config, cluster_nodes_info

def parse_s3_info(report_dir):
    s3_config_info = []
    hosts_info = []
    haproxy_info = []

    s3_dir = join(report_dir, 's3server')

    s3_haproxy_cfg_files = [join(join(s3_dir, d), 'haproxy/cfg/haproxy.cfg')
                            for d in listdir(s3_dir) if isdir(join(s3_dir, d))]
    for path in s3_haproxy_cfg_files:
        if isfile(path):
            with open(path, 'r') as haproxy_file:
                lines = haproxy_file.readlines()
                lines = [replace_spaces_for_html(line) for line in lines]
                haproxy_info.append(lines)

    s3_hosts_files = [join(join(s3_dir, d), 'hosts')
                      for d in listdir(s3_dir) if isdir(join(s3_dir, d))]
    for path in s3_hosts_files:
        if isfile(path):
            with open(path, 'r') as hosts_file:
                lines = hosts_file.readlines()
                lines = [replace_spaces_for_html(line) for line in lines]
                hosts_info.append(lines)

    s3_config_files = [join(join(s3_dir, d), 's3config.yaml')
                       for d in listdir(s3_dir) if isdir(join(s3_dir, d))]
    for path in s3_config_files:
        if isfile(path):
            with open(path, 'r') as s3_config_file:
                lines = s3_config_file.readlines()
                lines = [line.split(
                    '#')[0] if '#' in line else line for line in lines if line[0] != '#']
                s3_config_info.append(lines)

    return s3_config_info, hosts_info, haproxy_info


def parse_s3bench_csv(csvfile_path):
    fields = ('numSamples', 'numClients', 'objectSize (MB)', 'Operation',
              'Errors Count', 'Total Throughput (MB/s)')
    indexes = list()
    result = list()

    with open(csvfile_path, newline='') as csvfile:
        header = None
        spamreader = csv.reader(csvfile)

        for row in spamreader:
            if header is None:
                header = list()

                for i, field_name in enumerate(row):
                    if field_name in fields:
                        header.append(field_name)
                        indexes.append(i)

                result.append(header)
                continue

            bench_res = list()

            for index in indexes:
                value = row[index]

                # try to round float value
                try:
                    if '.' in value:
                        value = float(value)
                        value = round(value, 3)
                except ValueError:
                    pass

                bench_res.append(value)

            result.append(bench_res)

    return result


def parse_report_info(report_dir):
    csv_report_content = list()
    csvfile_path = join(report_dir, 'client', 's3bench_report.csv')

    if isfile(csvfile_path):
        csv_report_content = parse_s3bench_csv(csvfile_path)

    workload_filenames = []

    # Saving workload filenames
    workload_dir = join(report_dir, 'client')

    if isdir(workload_dir):
        workload_filenames.extend([f for f in listdir(
            workload_dir) if isfile(join(workload_dir, f))])

    # Excluding auto generated s3bench log files or duplicate logs.
    workload_filenames = list(filter(lambda a: not a.startswith("s3bench-"), workload_filenames))

    workload_dir = join(report_dir, 'core_benchmark')
    if isdir(workload_dir):
        workload_filenames.extend([f for f in listdir(
            workload_dir) if isfile(join(workload_dir, f))])

    #Iperf
    iperf_rw_stat = {}
    if isdir(workload_dir):
       iperf_log_list = fnmatch.filter(listdir(workload_dir), '*iperf_workload.log')
       for index, _ in enumerate(iperf_log_list):
          iperf_log = join(workload_dir,iperf_log_list[index])
          if isfile(iperf_log):
              temp = 'srvnode-{}'.format(index + 1)
              iperf_rw_stat[temp] = iperf_log_parser.parse_iperf_log(iperf_log)
       print('Iperf output: {}'.format(iperf_rw_stat))

    #m0crate
    m0crate_dir = join(report_dir, 'm0crate')
    m0crate_rw_stats = {}
    if isdir(m0crate_dir):
        for dir_path, _, files in walk(m0crate_dir):
            m0crate_logs = list(filter(lambda f_name: f_name.endswith('.log'), files))
            workload_filenames.extend(m0crate_logs)

            for f in m0crate_logs:
                if "io" in f:
                    m0crate_log_path = join(dir_path, f)
                    m0crate_rw_stats[f] = m0crate_log_parser.parse_m0crate_log(m0crate_log_path)

    return m0crate_rw_stats, workload_filenames, iperf_rw_stat, csv_report_content


def parse_mapping_info(nodes_stat_dirs):
    disks_mapping_info = []
    nodes_mapping_info = []

    for path in nodes_stat_dirs:
        if isfile(join(path, 'disks.mapping')):
            with open(join(path, 'disks.mapping'), 'r') as disks_mapping_info_file:
                lines = disks_mapping_info_file.readlines()
                lines = [replace_spaces_for_html(line) for line in lines]
                disks_mapping_info.append(lines)

    for path in nodes_stat_dirs:
        if isfile(join(path, 'iostat/nodes.mapping')):
            with open(join(path, 'iostat/nodes.mapping'), 'r') as nodes_mapping_info_file:
                lines = nodes_mapping_info_file.readlines()
                lines = [replace_spaces_for_html(line) for line in lines]
                nodes_mapping_info.append(lines)

    return disks_mapping_info, nodes_mapping_info


def parse_dstat_info(nodes_stat_dirs):
    dstat_net_info = []
    for path in nodes_stat_dirs:
        if isfile(f'{path}/dstat/dstat.csv'):
            df = pd.read_csv(f'{path}/dstat/dstat.csv',
                             sep=',', skiprows=lambda x: x in range(5))
            net_columns = [c.split('/')[1] for c in df.columns if 'net' in c]
            if ':' in net_columns[0]:
                # dstat 0.7.3
                for column in net_columns:
                    if not column.startswith("cali"):
                        print(column)
                        # plt.figure()
                        net = df['net/' + column]
                        net = [float(n)/10**4 for n in net.tolist()]
                        plt.plot(net)

                        plt.ylabel('KB')
                        plt.xlabel('Seconds')
                        plt.savefig(f'{path}/dstat/{column.replace(":", "_")}.png')
                        plt.cla()
                dstat_net_info.append([column.replace(":", "_")
                                       for column in net_columns])
            else:
                # dstat 0.7.2
                net_columns_7_2 = []
                for column in net_columns:
                    if not column.startswith("cali"):
                        print(column)
                        net_col_id = df.columns.get_loc('net/' + column)
                        net_recv = df['net/' + column]
                        net_send = df[df.columns[net_col_id + 1]]
                        del net_recv[0]
                        del net_send[0]
                        net_recv = [float(n)/10**4 for n in net_recv.tolist()]
                        net_send = [float(n)/10**4 for n in net_send.tolist()]

                        plt.figure()
                        plt.plot(net_recv)
                        plt.ylabel('KB')
                        plt.xlabel('Seconds')
                        plt.savefig(f'{path}/dstat/{column}_recv.png')
                        net_columns_7_2.append(f'{column}_recv')
                        plt.cla()

                        plt.figure()
                        plt.plot(net_send)

                        plt.ylabel('KB')
                        plt.xlabel('Seconds')
                        plt.savefig(f'{path}/dstat/{column}_send.png')
                        net_columns_7_2.append(f'{column}_send')
                        plt.close()

                dstat_net_info.append(net_columns_7_2)

    dstat_net_info = set(itertools.chain.from_iterable(dstat_net_info))

    return dstat_net_info


def parse_addb_timelines(addb_stat_dir):
    result = []

    if isdir(addb_stat_dir):

        for op in ('Put', 'Get'):

            tmp_res = {'op_name': op}

            timelines_imgs = sorted([f for f in listdir(addb_stat_dir) if f.startswith('s3_timeline_') and op in f])

            def parse_timeline_name(fname):
                tmp = fname.split('.')[-2].split('_')
                info = {'workload_part': tmp[2], 'op': tmp[3],
                        'pid': tmp[4], 'id': tmp[5], 'fname': fname}

                fname_template = fname.replace('s3', '').replace('.png', '')
                subreqs_timelines = sorted([f for f in listdir(addb_stat_dir) if f.startswith('motr_timeline_') and fname_template in f])
                info['subrequests'] = subreqs_timelines
                return info

            timelines_imgs = list(map(parse_timeline_name, timelines_imgs))
            tmp_res['imgs'] = timelines_imgs
            result.append(tmp_res)


    return result


def parse_addb_info(addb_stat_dir):
    if isdir(addb_stat_dir):
        queues_imgs = [f for f in listdir(addb_stat_dir) if f.startswith('queues_')]
        hist_imgs = [f for f in listdir(addb_stat_dir) if '_histogram' in f]
        rps_imgs = [f for f in listdir(addb_stat_dir) if '_cluster_wide_RPS' in f]
        lat_imgs = [f for f in listdir(addb_stat_dir) if '_cluster_wide_latency' in f]
        mbps_imgs = [f for f in listdir(addb_stat_dir) if '_cluster_wide_throughput' in f]
    else:
        queues_imgs = []
        hist_imgs = []
        rps_imgs = []
        lat_imgs = []
        mbps_imgs = []

    return queues_imgs, hist_imgs, rps_imgs, lat_imgs, mbps_imgs

def parse_glances_imgs(stat_dir):
    glances_imgs = []
    subdir_list = [join(stat_dir, d) for d in listdir(stat_dir) if isdir(join(stat_dir, d))]

    for subdir in subdir_list:
        glances_dir = join(subdir, 'glances')

        if isdir(glances_dir):
            glances_imgs.extend([f for f in listdir(glances_dir) if f.endswith('.png')])

    result = {}
    hostnames = set()
    percpu_metric_names = set()
    net_metric_names = set()
    datavol_metric_names = set()
    mdvol_metric_names = set()

    for img in glances_imgs:
        fname_parts = img.replace('.png', '').split('__', maxsplit=1)
        hostname = fname_parts[0]
        graph_type = fname_parts[1]

        if graph_type not in result:
            result[graph_type] = {}

        result[graph_type][hostname] = img
        hostnames.add(hostname)

        if graph_type.startswith('percpu__'):
            percpu_metric_names.add(graph_type)
        elif graph_type.startswith('net__'):
            net_metric_names.add(graph_type)
        elif graph_type.startswith('datavolume__'):
            datavol_metric_names.add(graph_type)
        elif graph_type.startswith('mdvolume__'):
            mdvol_metric_names.add(graph_type)

    sorted_hostnames = list(sorted(hostnames))
    sorted_percpu_metrics = list(sorted(percpu_metric_names,
                                        key=lambda x: int(x.replace('percpu__', ''))))

    sorted_net_metrics = list(sorted(net_metric_names,
                                     key=lambda x: x.replace('net__', '')))

    sorted_datavol_metrics = list(sorted(datavol_metric_names,
                                         key=lambda x: x.replace('datavolume__', '')))

    sorted_mdvol_metrics = list(sorted(mdvol_metric_names,
                                       key=lambda x: x.replace('mdvolume__', '')))

    return (sorted_hostnames, result, sorted_percpu_metrics,
           sorted_net_metrics, sorted_datavol_metrics, sorted_mdvol_metrics)

def detect_iostat_imgs(nodes_stat_dirs):
    iostat_img_types = set()

    for n_path in nodes_stat_dirs:
        n_path_iostat = join(n_path, 'iostat')

        if isdir(n_path_iostat):
            for f in listdir(n_path_iostat):
                if isfile(join(n_path_iostat, f)) and f.endswith('.png'):
                    f = f.replace('iostat.','').replace('.png','')
                    iostat_img_types.add(f)

    return sorted(iostat_img_types)


def detect_blktrace_imgs(nodes_stat_dirs):
    blktrace_img_types = set()

    for n_path in nodes_stat_dirs:
        n_path_blktrace = join(n_path, 'blktrace')

        if isdir(n_path_blktrace):
            for f in listdir(n_path_blktrace):
                if isfile(join(n_path_blktrace, f)) and 'node' in f and 'aggregated' in f:
                    blktrace_img_types.add('aggregated')

    return sorted(blktrace_img_types)


def main():
    report_gen_dir = sys.argv[2]
    report_dir = getcwd() if sys.argv[1] == '.' else sys.argv[1]
    stat_result_dir = join(report_dir, 'stats')
    addb_stat_dir = join(stat_result_dir, 'addb')

    run_metadata_path = join(report_dir, 'run_metadata.json')
    run_metadata = None

    if isfile(run_metadata_path):
        with open(run_metadata_path) as f:
            try:
                run_metadata = json.loads(f.read())
            except Exception as e:
                print(e)

    if not isdir(stat_result_dir):
        print(
            f'Aborting report generation. No stats directory detected at: {report_dir}')
        exit()
    nodes_stat_dirs = [join(stat_result_dir, f) for f in listdir(
        stat_result_dir) if isdir(join(stat_result_dir, f))]

    # Filter 'addb' directory
    # Needs to be improved in the future
    nodes_stat_dirs = list(filter(lambda x: not x.split('/')[-1].startswith('addb'), nodes_stat_dirs))

    # Define task_id
    task_id_path = report_dir.split('/')
    task_id = task_id_path[-2].split(
        '_')[-1] if task_id_path[-1] == '' else task_id_path[-1].split('_')[-1]

    pids_info = None

    if run_metadata is not None:
        pids_info = get_pids(run_metadata, nodes_stat_dirs)

    # Static info
    node_names = [node_path.split('/')[-1] for node_path in nodes_stat_dirs]
    node_amount = len(nodes_stat_dirs)

    # Iostat images
    iostat_imgs = detect_iostat_imgs(nodes_stat_dirs)

    # Blktrace images
    blktrace_imgs = detect_blktrace_imgs(nodes_stat_dirs)

    # Time
    workload_start_time, workload_stop_time, test_start_time, test_stop_time = parse_time(
        stat_result_dir)

    # Hardware
    mems, cpu_info, commit_info = parse_hardware_info(nodes_stat_dirs)

    # Network
    network_infos, lnet_conf, lnet_info, multipath_conf, multipath_info = parse_network_info(
        nodes_stat_dirs)

    # Configs
#    motr_config, cluster_nodes_info = parse_config_info(report_dir, node_names)

    # S3
#    s3_config_info, hosts_info, haproxy_info = parse_s3_info(report_dir)

    # Read report output
    # m0crate_rw_stats, workload_filenames, iperf_rw_stat, csv_report_content = parse_report_info(report_dir)
    m0crate_rw_stats, workload_filenames, _, csv_report_content = parse_report_info(report_dir)

    # Disk and network mappings
    disks_mapping_info, nodes_mapping_info = parse_mapping_info(
        nodes_stat_dirs)

    # Gen images for dstat
    dstat_net_info = parse_dstat_info(nodes_stat_dirs)

    # Images for addb queues
    addb_queues, addb_hists, addb_rps, addb_lat, addb_mbps = parse_addb_info(
        addb_stat_dir)
    timelines_imgs = parse_addb_timelines(addb_stat_dir)

    # Glances images
    (hostnames, glances_imgs, percpu_metrics, net_metrics,
     datavolume_metrics, mdvolume_metrics) = parse_glances_imgs(stat_result_dir)

    with open(join(report_gen_dir, 'templates/home.html'), 'r') as home:
        home_template = home.read()

    loader = FileSystemLoader(searchpath=report_gen_dir + "/templates")
    home_template = Environment(loader=loader,autoescape=True).from_string(home_template)

    with open(join(report_dir, 'report_page.html'), 'w+') as report:
        report.write(home_template.render(
            cpu_info=cpu_info,
            dstat_net_info=dstat_net_info,
            disks_mapping_info=disks_mapping_info,
            nodes_mapping_info=nodes_mapping_info,
            commit_info=commit_info,
            lnet_conf=lnet_conf,
            lnet_info=lnet_info,
            multipath_conf=multipath_conf,
            multipath_info=multipath_info,
            m0crate_rw_stats=m0crate_rw_stats,
            workload_filenames=workload_filenames,
#            iperf_rw_stat=iperf_rw_stat,
            mems=mems,
#            s3_config_info=s3_config_info,
#            hosts_info=hosts_info,
#            haproxy_info=haproxy_info,
#            motr_config=motr_config,
#            cluster_nodes_info=cluster_nodes_info,
            network_infos=network_infos,
            node_names=node_names,
            workload_start_time=workload_start_time,
            workload_stop_time=workload_stop_time,
            test_start_time=test_start_time,
            test_stop_time=test_stop_time,
            node_amount=node_amount,
            iostat_imgs=iostat_imgs,
            blktrace_imgs=blktrace_imgs,
            addb_queues=addb_queues,
            addb_hists=addb_hists,
            addb_rps=addb_rps,
            addb_lat=addb_lat,
            addb_mbps=addb_mbps,
            timelines_imgs=timelines_imgs,
            task_id=task_id,
            glances_imgs=glances_imgs,
            hostnames=hostnames,
            percpu_metrics=percpu_metrics,
            net_metrics=net_metrics,
            datavolume_metrics=datavolume_metrics,
            mdvolume_metrics=mdvolume_metrics,
            csv_report_content=csv_report_content,
#            pids_info=pids_info
        ))


def usage():
    print("Usage: python3 report.py $path_to_m0crate_results $report_generator_dir")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main()
    else:
        usage()
