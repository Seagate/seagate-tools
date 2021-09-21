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

import config
from config import huey
from datetime import datetime
import os
import plumbum
import json
import yaml

def get_overrides(overrides):
    return " ".join([f"{x}={y}" for (x, y) in overrides.items()])


def parse_options(conf, result_dir):
    options = []

    options.append('-p')
    options.append(result_dir)


    # Stats collection
    if conf['stats_collection']['iostat']:
        options.append('--iostat')
    if conf['stats_collection']['dstat']:
        options.append('--dstat')
    if conf['stats_collection']['blktrace']:
        options.append('--blktrace')
    if conf['stats_collection']['glances']:
        options.append('--glances')

    # Workloads
    for b in conf['workloads']:
        if 'custom' in b:
            options.append('-w')
            options.append(b['custom']['cmd'])
        elif 's3bench' in b:
            options.append('--s3bench')
            # Parameter
            s3bench_params = ''
            for param_name, param_val in b['s3bench'].items():
                s3bench_params += "--{} {} ".format(param_name, param_val)
            options.append('--s3bench-params')
            options.append(s3bench_params)

        elif 'm0crate' in b:
            options.append('--m0crate')
            params_str = ''
            for param_name, param_val in b['m0crate'].items():
                params_str += "{}={} ".format(param_name, param_val)
            options.append('--m0crate-params')
            options.append(params_str)

    # Execution options:
    if 'mkfs' in conf['execution_options']:
        if conf['execution_options']['mkfs']:
            options.append("--mkfs")
    if conf['execution_options']['collect_m0trace']:
        options.append("--m0trace-files")
    if conf['execution_options']['collect_addb']:
        options.append("--addb-dumps")
    if 'analyze_addb' in conf['execution_options']:
        if conf['execution_options']['analyze_addb']:
            options.append("--addb-analyze")
    if conf['execution_options']['backup_result']:
        options.append("--backup-result")

    print(options)
    return options


def run_cmds(cmds, path):
    for entry in cmds:
        with plumbum.local.env():
            try:
                argv = entry['cmd'].split(" ")
                cmd = argv[0]
                params = argv[1:]
                print("cmd: {}, params: {}".format(cmd, params))
                run = plumbum.local[cmd]
                run[params] & plumbum.FG
            except plumbum.commands.processes.CommandNotFound as err:
                print(f"Command '{entry}' not found, error {err}")
            except plumbum.commands.processes.ProcessExecutionError as err:
                print(f"Command '{entry}' returned non-zero, error {err}")
            except KeyError:
                print(f"Not properly formed command '{entry}'")


def send_mail(to, status, tid):
    nl = "\n"
    msg = f"Subject: Cluster task queue{nl}Task {tid} {status}"
    sendmail = plumbum.local["sendmail"]
    echo = plumbum.local["echo"]
    chain = echo[msg] | sendmail[to]
    try:
        chain()
    except:
        print(f"Couldn't send email to {to}")


def pack_artifacts(path):
    tar = plumbum.local["tar"]
    parent_dir = '/'.join(path.split('/')[:-1])
    archive_dir = path.split('/')[-1]
    tar[f"-cJvf {parent_dir}/{archive_dir}.tar.xz -C {parent_dir} {archive_dir}".split(
        " ")] & plumbum.FG
    print(f"Rm path: {path}")
    rm = plumbum.local["rm"]
    # rm[f"-rf {path}".split(" ")]()


def update_configs(conf, log_dir):
    options = []
    result = 'SUCCESS'

    if 'configuration' in conf:

        if 'motr' in conf['configuration']:
            motr = conf['configuration']['motr']
            
            if 'custom_conf' in motr:
                options.append('--motr-custom-conf')
                options.append(motr['custom_conf'])

            if 'params' in motr:
                for p_name, p_val in motr['params'].items():
                    options.append('--motr-param')
                    options.append(f'{p_name}={p_val}')

        if 's3' in conf['configuration']:
            s3 = conf['configuration']['s3']

            if 'custom_conf' in s3:
                options.append('--s3-custom-conf')
                options.append(s3['custom_conf'])

            if 'instances_per_node' in s3:
                options.append('--s3-instance-nr')
                options.append(s3['instances_per_node'])

            # S3 config file parameters overriding
            for section, p_name in (('S3_SERVER_CONFIG', '--s3-srv-param'),
                                    ('S3_AUTH_CONFIG', '--s3-auth-param'),
                                    ('S3_MOTR_CONFIG', '--s3-motr-param'),
                                    ('S3_THIRDPARTY_CONFIG', '--s3-thirdparty-param')):
                if section in s3:
                    for k, v in s3[section].items():
                        options.append(p_name)
                        options.append('{}={}'.format(k, repr(v)))

        if 'haproxy' in conf['configuration']:
            haproxy = conf['configuration']['haproxy']

            if 'maxconn_total' in haproxy:
                options.append('--haproxy-maxconn-total')
                options.append(haproxy['maxconn_total'])

            if 'maxconn_per_s3_instance' in haproxy:
                options.append('--haproxy-maxconn-per-s3-instance')
                options.append(haproxy['maxconn_per_s3_instance'])

            if 'nbproc' in haproxy:
                options.append('--haproxy-nbproc')
                options.append(haproxy['nbproc'])

            if 'nbthread' in haproxy:
                options.append('--haproxy-nbthread')
                options.append(haproxy['nbthread'])

        if 'hare' in conf['configuration']:
            hare = conf['configuration']['hare']
            if 'custom_cdf' in hare:
                options.append('--hare-custom-cdf')
                options.append(hare['custom_cdf'])

            if 'sns' in hare:
                options.append('--hare-sns-data-units')
                options.append(hare['sns']['data_units'])

                options.append('--hare-sns-parity-units')
                options.append(hare['sns']['parity_units'])

                options.append('--hare-sns-spare-units')
                options.append(hare['sns']['spare_units'])

            if 'dix' in hare:
                options.append('--hare-dix-data-units')
                options.append(hare['dix']['data_units'])

                options.append('--hare-dix-parity-units')
                options.append(hare['dix']['parity_units'])

                options.append('--hare-dix-spare-units')
                options.append(hare['dix']['spare_units'])

        if 'lnet' in conf['configuration']:
            lnet = conf['configuration']['lnet']
            if 'custom_conf' in lnet:
                options.append('--lnet-custom-conf')
                options.append(lnet['custom_conf'])
            
        if 'ko2iblnd' in conf['configuration']:
            ib = conf['configuration']['ko2iblnd']
            if 'custom_conf' in ib:
                options.append('--ib-custom-conf')
                options.append(ib['custom_conf'])
            
        update_configs = plumbum.local["scripts/conf_customization/update_configs.sh"]
        mv = plumbum.local['mv']
        try:
            tee = plumbum.local['tee']
            (update_configs[options] | tee['/tmp/update_configs.log']) & plumbum.FG
        except plumbum.commands.processes.ProcessExecutionError:
            result = 'FAILED'

        mv['/tmp/update_configs.log', log_dir] & plumbum.FG

    return result


def restore_original_configs():    
    result = 'SUCCESS'

    restore_configs = plumbum.local["scripts/conf_customization/restore_orig_configs.sh"]
    
    try:
        (restore_configs['']) & plumbum.FG
    except plumbum.commands.processes.ProcessExecutionError:
        result = 'FAILED'

    return result


def run_worker(conf, result_dir):
    result = 'SUCCESS'

    worker = plumbum.local["scripts/worker.sh"]
    try:
        tee = plumbum.local['tee']
        options = parse_options(conf, result_dir)
        (worker[options] | tee['/tmp/workload.log']) & plumbum.FG
    except plumbum.commands.processes.ProcessExecutionError:
        result = 'FAILED'

    mv = plumbum.local['mv']
    mv['/tmp/workload.log', result_dir] & plumbum.FG
    return result

def sw_update(conf, log_dir):
    options = []
    result = 'SUCCESS'

    if 'custom_build' in conf:
        mv = plumbum.local['mv']
        params = conf['custom_build']
        if 'url' in params:
            options.append('--url')
            options.append(params['url'])
        else:
            options.append('-m')
            options.append(params['motr']['repo'])
            options.append(params['motr']['branch'])
            options.append('-s')
            options.append(params['s3server']['repo'])
            options.append(params['s3server']['branch'])
            options.append('-h')
            options.append(params['hare']['repo'])
            options.append(params['hare']['branch'])
            if 'py-utils' in conf['custom_build']:
               options.append('-u')
               options.append(params['py-utils']['repo'])
               options.append(params['py-utils']['branch'])

        with plumbum.local.env():
            update = plumbum.local["scripts/update.sh"]
            try:
                tee = plumbum.local['tee']
                (update[options] | tee['/tmp/update.log']) & plumbum.FG
            except plumbum.commands.processes.ProcessExecutionError:
                result = 'FAILED'
                
        mv['/tmp/update.log', log_dir] & plumbum.FG

    return result

def run_corebenchmark(conf, log_dir):
    options = []
    options.append('-p')
    options.append(log_dir)
    result = 'SUCCESS'
    mv = plumbum.local['mv']
    # Benchmarks
    if 'benchmarks' in conf:
       for b in conf['benchmarks']:
          if 'custom' in b:
              options.append('-w')
              options.append(b['custom']['cmd'])
          elif 'lnet' in b:
              options.append('--lnet')
              options.append('-ops')
              options.append(b['lnet']['LNET_OPS'])
          elif 'fio' in b:
              options.append('--fio')
              # Fio Parameter
              fio_params = ''
              for param_name, param_val in b['fio'].items():
                  if param_name == "Duration":
                     param_name = "-t"
                  elif param_name == "BlockSize":
                     param_name = "-bs"
                  elif param_name == "NumJobs":
                     param_name = "-nj"
                  elif param_name == "Template":
                     param_name = "-tm"
                  fio_params += "{} {} ".format(param_name, param_val)
              options.append('--fio-params')
              options.append(fio_params)
          elif 'iperf' in b:
              options.append('--iperf')
              params_str = ''
              for param_name, param_val in b['iperf'].items():
                  if param_name == "Interval":
                     param_name = "-i"
                  elif param_name == "Duration":
                     param_name = "-t"
                  elif param_name == "Parallel":
                     param_name = "-P"
                  params_str += "{} {} ".format(param_name, param_val)
              options.append('--iperf-params')
              options.append(params_str)
      		
    
       with plumbum.local.env():
           benchmark_update = plumbum.local["scripts/core_benchmarks.sh"]
           try:
              tee = plumbum.local['tee']
              (benchmark_update[options] | tee['/tmp/core_benchmarks.log']) & plumbum.FG
           except plumbum.commands.processes.ProcessExecutionError:
              result = 'FAILED'
        
       mv['/tmp/core_benchmarks.log', log_dir] & plumbum.FG

    return result

def save_workloadconfig(conf, result_dir):
    workload = "{}/workload.yaml".format(result_dir)
    try:
        with open(workload, 'w') as file:
            yaml.dump(conf, file,default_flow_style=False, sort_keys=False)
    except FileNotFoundError as e:
        print(e)

@huey.task(context=True)
def worker_task(conf_opt, task):
    conf, opt = conf_opt
    current_task = {
        'task_id': task.id,
        'pid': os.getpid(),
        'args': conf_opt,
    }
    huey.put('current_task', current_task)

    result = {
        'conf': conf,
        'start_time': str(datetime.now()),
        'path': f"{config.artifacts_dir}",
        'artifacts_dir': f"{config.artifacts_dir}/result_{task.id}",
    }
    result.update(opt)

    if config.pack_artifacts:
        result['archive_name'] = f"result_{task.id}.tar.xz"

    if conf['common']['send_email']:
        send_mail(conf['common']['user'], "Task started", task.id)

    if 'pre_exec_cmds' in conf:
        run_cmds(conf['pre_exec_cmds'], result['artifacts_dir'])

    with plumbum.local.env():

        mkdir = plumbum.local['mkdir']
        mkdir["-p", result["artifacts_dir"]] & plumbum.FG

        failed = False

        ret = save_workloadconfig(conf, result["artifacts_dir"])

        if not failed:
            ret = restore_original_configs()
            if ret == 'FAILED':
                result['finish_time'] = str(datetime.now())
                failed = True
               
        if not failed:
            ret = sw_update(conf, result["artifacts_dir"])
            if ret == 'FAILED':
                result['finish_time'] = str(datetime.now())
                failed = True

        if not failed:
            ret = update_configs(conf, result["artifacts_dir"])
            if ret == 'FAILED':
                result['finish_time'] = str(datetime.now())
                failed = True

        if not failed:
            ret = run_corebenchmark(conf, result["artifacts_dir"])
            if ret == 'FAILED':
                result['finish_time'] = str(datetime.now())
                failed = True

        if not failed:
            ret = run_worker(conf, result["artifacts_dir"])
            if ret == 'FAILED':
                result['finish_time'] = str(datetime.now())
                failed = True

        ret = restore_original_configs()
        if ret == 'FAILED':
            result['finish_time'] = str(datetime.now())
            failed = True
            

    result['finish_time'] = str(datetime.now())
    result['status'] = 'FAILED' if failed else 'SUCCESS'

    if 'post_exec_cmds' in conf:
        run_cmds(conf['post_exec_cmds'], result['artifacts_dir'])

    if conf['common']['send_email']:
        send_mail(conf['common']['user'], f"finished, status {result['status']}",
                  task.id)

    if config.pack_artifacts:
        pack_artifacts(result["artifacts_dir"])

    pl_metadata_file = "{}/perfline_metadata.json".format(result["artifacts_dir"])

    try:
        with open(pl_metadata_file, "wt") as f:
            f.write(json.dumps(result))
    except FileNotFoundError as e:
        print(e)

    return result


@huey.post_execute()
def post_execute_hook(task, task_value, exc):
    if exc is not None:
        print(f'Task "{task.id}" failed with error: {exc}')
    # Current task finished - do cleanup
    huey.get('current_task')
