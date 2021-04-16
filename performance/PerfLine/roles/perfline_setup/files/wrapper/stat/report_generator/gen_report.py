from os import listdir, getcwd
from os.path import isdir, join, isfile, isdir

import json
import sys
import datetime
import yaml
from jinja2 import Template, Environment, BaseLoader, FileSystemLoader

import pandas as pd
import csv
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import s3bench_log_parser
import m0crate_log_parser

# Helper functions


def replace_spaces_for_html(line):
    line = line.replace(' ', '&nbsp')
    return line


def list_replace_spaces_for_html(lines):
    lines = [line.replace(' ', '&nbsp') for line in lines]
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


def parse_config_info(report_dir):
    motr_config = []
    cluster_nodes_info = []

    if isfile(join(report_dir, 'm0d/configs/cluster.yaml')):
        with open(join(report_dir, 'm0d/configs/cluster.yaml'), 'r') as cluster_file:
            cluster_yaml = yaml.safe_load(cluster_file)
            cluster_nodes_info = [n for n in cluster_yaml['nodes']]

    if isfile(join(report_dir, 'm0d/configs/motr')):
        with open(join(report_dir, 'm0d/configs/motr'), 'r') as motr_config_file:
            motr_config = motr_config_file.readlines()
            motr_config = [conf for conf in motr_config if len(
                conf.split('=')) == 2 and conf[0] != '#']
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


def parse_report_info(report_dir):
    rw_stats = {}
    s3bench_log = join(report_dir, 'client/workload_s3bench.log')
    if isfile(s3bench_log):
        rw_stats = s3bench_log_parser.parse_s3bench_log(s3bench_log)

    workload_filenames = []

    # Saving workload filenames
    workload_dir = join(report_dir, 'client')

    if isdir(workload_dir):
        workload_filenames.extend([f for f in listdir(
            workload_dir) if isfile(join(workload_dir, f))])

    #m0crate
    m0crate_dir = join(report_dir, 'm0crate')
    m0crate_rw_stats = {}

    if isdir(m0crate_dir):
        m0crate_logs = [f for f in listdir(
            m0crate_dir) if isfile(join(m0crate_dir, f)) and f.endswith('.log')]

        workload_filenames.extend(m0crate_logs)

        for m0crate_log in m0crate_logs:
            m0crate_log_path = join(m0crate_dir, m0crate_log)
            m0crate_rw_stats[m0crate_log] = m0crate_log_parser.parse_m0crate_log(m0crate_log_path)

    return rw_stats, m0crate_rw_stats, workload_filenames


def parse_mapping_info(nodes_stat_dirs):
    disks_mapping_info = []
    nodes_mapping_info = []

    for path in nodes_stat_dirs:
        if isfile(join(path, 'iostat/disks.mapping')):
            with open(join(path, 'iostat/disks.mapping'), 'r') as disks_mapping_info_file:
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


def parse_addb_info(addb_stat_dir):
    if isdir(addb_stat_dir):
        queues_imgs = [f for f in listdir(addb_stat_dir) if f.startswith('queues_')]
    else:
        queues_imgs = []

    return queues_imgs

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
    motr_config, cluster_nodes_info = parse_config_info(report_dir)

    # S3
    s3_config_info, hosts_info, haproxy_info = parse_s3_info(report_dir)

    # Read report output
    rw_stats, m0crate_rw_stats, workload_filenames = parse_report_info(report_dir)

    # Disk and network mappings
    disks_mapping_info, nodes_mapping_info = parse_mapping_info(
        nodes_stat_dirs)

    # Gen images for dstat
    dstat_net_info = parse_dstat_info(nodes_stat_dirs)

    # Images for addb queues
    addb_queues = parse_addb_info(addb_stat_dir)

    with open(join(report_gen_dir, 'templates/home.html'), 'r') as home:
        home_template = home.read()

    loader = FileSystemLoader(searchpath=report_gen_dir + "/templates")
    home_template = Environment(loader=loader).from_string(home_template)

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
            rw_stats=rw_stats,
            m0crate_rw_stats=m0crate_rw_stats,
            workload_filenames=workload_filenames,
            mems=mems,
            s3_config_info=s3_config_info,
            hosts_info=hosts_info,
            haproxy_info=haproxy_info,
            motr_config=motr_config,
            cluster_nodes_info=cluster_nodes_info,
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
            task_id=task_id
        ))


def usage():
    print("Usage: python3 report.py $path_to_m0crate_results $report_generator_dir")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main()
    else:
        usage()
