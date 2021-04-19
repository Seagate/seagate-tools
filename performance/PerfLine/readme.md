
# Perfline
This is perfline module that allows to run cortx workloads.
It consists of three modules:
- wrapper - main functionality, report generator, statistic gather scripts
- webui - web server for presenting workload result and controlling over new workloads
- ansible playbook - ansible script for fast perfline setup

# Prerequisites
You can setup perfline from any machine, to setup perfline or deploying perfline on a client, following prerequisites must be satisfied:
1. Actual version of seagatetools repo downloaded
2. Ansible package installed (ver. 2.9+)
3. Choose Machine, from which installation will be performed,
4. Setup config for cluster nodes
    4.1 Change ./inventories/perfline_hosts/hosts file and set target cluster nodes dns-name/ip. Accordingly for nodes and client groups.
 Build machine is an optional to user, if user want to create new build for io-path components on LR2 setup.
    ```
    [nodes]
    srvnode-1 ansible_host=<PRIMARY NODE-FQDN>
    srvnode-2 ansible_host=<SECONDARY NODE-FQDN>
    srvnode-3 ansible_host=<TERTIARY NODE-FQDN>

    [client]
    client-1 ansible_host=<CLIENT NODE-FQDN>

    [build_machine]
    #build-server ansible_host=<BUILD-MACHINE-FQDN>
    ```
    4.2 Change ./roles/perfline_setup/files/wrapper/sys/config.py and set target nodes names and ha_type.
    ```
    nodes = 'target1.seagate.com,target2.seagate.com'
    ha_type = 'hare'
    ```
    For Minimal(io-path components) configuration `ha_type = hare`
    For Complete cluster configuration `ha_type = pcs`

    4.3 Default root password is "seagate1" for cortx cluster including client, If user having different password then please update on "/roles/perfline_setup/vars/main.yml"
    ```
    CLUSTER_PASS: seagate1
    ```

# Installation
When prerequisites is satisfied you need to `# cd` to `PerfLine` directory and run:
`# ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v`
After that wait till ansible will copy and install all required artifacts on target nodes and also copy required script on client node to run perfline workload within `/root/perfline`.

# Define own workload
As per your test cases, Create a "<example>.yaml" file inside `/root/perfline/wrapper/workload` directory .
Custom build:
```
1. if user want to use internal docker service then user must generate "github personal access token"(github_PAT), "github username" otherwise user can move ahead with external docker service without "github_PAT" and "github_username".
2. User have an option to choose build machine either VM or HW machine.
3. No need to mention anything for motr_repo_path, hare_repo_path and s3server_repo_path. This feature is disabled.
4. User can update cluster or build based on io-path components commit_id.
```

For ex:
```
common:
  version: 1
  description: Perf benchmark example
  priority: 1
  batch_id: null
  user: user@seagate.com
  send_email: false
  
# Optional section. It may be deleted in case you don't want
# to build/deploy custom version of Cortx components
custom_build:
  github_PAT:
  github_username:
  build_machine:                     # Build Anywhere (it could be client, any one cortx cluster server or VM)
  motr_repo_path: ""
  hare_repo_path: ""
  s3server_repo_path: ""
  hare_commit_id: ""
  motr_commit_id: ""
  s3server_commit_id: ""

stats_collection:
  iostat: true
  dstat: true
  blktrace: true
  glances: false
  
# List of benchmarks and parameters. This section must include
# at least one benchmark (custom/fio/s3bench/m0crate).
benchmarks:
  - custom:
      cmd: sleep 1
  - fio:
      Duration:
      BlockSize:
      NumJobs:
      Template:         #Template for fio like seq_read_fio, seq_write_fio, randmix_80-20_fio, randmix_20-80_fio and rand_fio
  - s3bench:
      BucketName: mybucket
      NumClients: 10
      NumSample: 100
      ObjSize: 32Mb
      EndPoint: https://s3.seagate.com
  - m0crate:
      NR_THREADS: 2
      BLOCK_SIZE: 2m
      IOSIZE: 4m

execution_options:
  mkfs: false
  m0trace: false
  addb: false
```

# Starting workload
Workload can be started only from client_node machine
For starting workload on a cluster you need to run tasks, which describing amount/size of files you want to upload/download and how many clients will perform load.
You can find examples of such tasks at `/root/perfline/wrapper/workload`
After you choose/wrote task description, you need to `# cd /root/perfline/wrapper` and than run task with:
`# ./perfline.py  -a < workload/<example>.yaml`
or
`# python3 perfline.py  -a < workload/<example>.yaml`

# Additional info
# Webui
If ansible script finish it's job successfully, you should be able to access webui page from browser at 'client_ip:8005'.
- At the main page you should see 4 graphs, that displays results of performance loads for different file sizes.
- At Queue page you can see current running tasks and short info about them
- At Results page you can see all finished tasks, read/write results, it's statuses and links to their artifacts and report page.
If you go to report page you could see detailed report for executed task, including hardware, network, block devices, statistic sctipts infos.

##### 8005 is a default port. If you want to change it, you should do it before perfline installation with these steps:
- in ./ansible_setup/setup.yaml find task named 'Open port for webui' and change mentioned port for desired:
    ```
    ` - name: Open port for webui`
    `firewalld: port='new_port'/tcp zone=public permanent=true state=enabled immediate=yes`
    ```
- in ./webui/config.py change `server_ep` variable for port:
    `...`
    `server_ep = {'host': '0.0.0.0', 'port': 'new_port'}`


# Re-organized and renamed PerfLine
```
.
├── ansible.cfg
├── callbacks
│   └── anstomlog.py
├── inventories
│   └── perfline_hosts
│       └── hosts
├── readme.md
├── roles
│   └── perfline_setup
│       ├── files
│       │   ├── build_deploy
│       │   │   ├── ansible.cfg
│       │   │   ├── callbacks
│       │   │   │   └── anstomlog.py
│       │   │   ├── roles
│       │   │   │   └── deploybuild
│       │   │   │       ├── files
│       │   │   │       │   └── local.repo
│       │   │   │       └── tasks
│       │   │   │           └── main.yml
│       │   │   └── run_build_deploy.yml
│       │   ├── chronometry
│       │   │   ├── addb2db.py
│       │   │   ├── addb2new.py
│       │   │   ├── common
│       │   │   │   ├── common_funcs
│       │   │   │   ├── patch_motr_role_mappings
│       │   │   │   ├── remote_execution
│       │   │   │   ├── sw_ver_check_funcs
│       │   │   │   └── timeout_funcs
│       │   │   ├── corruption_workload
│       │   │   ├── endless_m0crate
│       │   │   ├── endless_s3bench
│       │   │   ├── fio_tests
│       │   │   ├── fom_req.py
│       │   │   ├── fom_req.sh
│       │   │   ├── get_hw_conf.exp
│       │   │   ├── hist__client_req.py
│       │   │   ├── hist__fom_req.py
│       │   │   ├── hist__fom_req_r.py
│       │   │   ├── hist__fom_to_rpc.py
│       │   │   ├── hist__ioo_req.py
│       │   │   ├── hist.py
│       │   │   ├── hist__s3req.py
│       │   │   ├── hist__srpc_to_crpc.py
│       │   │   ├── hist__stio_req.py
│       │   │   ├── io_req.py
│       │   │   ├── ios-hist.sh
│       │   │   ├── io_workload
│       │   │   ├── kill_endless_m0crate
│       │   │   ├── md_req.py
│       │   │   ├── no_motr_trace.patch
│       │   │   ├── p0
│       │   │   ├── p0_hare
│       │   │   ├── queues.py
│       │   │   ├── req_utils.py
│       │   │   ├── restart_ios.sh
│       │   │   ├── run_corruption_task
│       │   │   ├── run_s3_corruption
│       │   │   ├── run_s3_task
│       │   │   ├── run_task
│       │   │   ├── s3_build_fix
│       │   │   │   ├── BUILD.template
│       │   │   │   ├── headers.template
│       │   │   │   ├── libs.template
│       │   │   │   └── rebuildall.sh
│       │   │   ├── s3_corruption_workload
│       │   │   ├── s3_req.py
│       │   │   ├── s3server_integration
│       │   │   │   ├── check_and_create_s3_cred
│       │   │   │   ├── functions
│       │   │   │   ├── patch_haproxy_config
│       │   │   │   ├── s3cli_aws
│       │   │   │   ├── s3cli_configure_aws
│       │   │   │   ├── s3cli_patch_hosts
│       │   │   │   ├── s3cli_s3bench
│       │   │   │   ├── s3_create_user
│       │   │   │   ├── s3_overrides.py
│       │   │   │   └── s3srv_build_prepare
│       │   │   ├── s3_workload
│       │   │   ├── task_queue
│       │   │   │   ├── batch_enqueue
│       │   │   │   ├── batch_results
│       │   │   │   ├── config.py
│       │   │   │   ├── config.yaml
│       │   │   │   ├── issues.txt
│       │   │   │   ├── m0crate.corruption.sample.yaml
│       │   │   │   ├── motr.sample.yaml
│       │   │   │   ├── print_task_results
│       │   │   │   ├── s3bench.corruption.sample.yaml
│       │   │   │   ├── s3.sample.yaml
│       │   │   │   ├── st.sh
│       │   │   │   ├── task_queue.py
│       │   │   │   ├── task_queue.sh
│       │   │   │   ├── tasks.py
│       │   │   │   └── validator.py
│       │   │   └── test_io.yaml.template
│       │   ├── chronometry_v2
│       │   │   ├── addb2db_multiprocess.sh
│       │   │   ├── addb2db.py
│       │   │   ├── hist.py
│       │   │   ├── queues.py
│       │   │   ├── req_graph.py
│       │   │   ├── req_timelines.py
│       │   │   └── req_utils.py
│       │   ├── filter.py
│       │   ├── glances.tar.gz
│       │   ├── huey_consumer
│       │   ├── local.repo
│       │   ├── main.py
│       │   ├── passwordless_ssh.sh
│       │   ├── perfline.service
│       │   ├── perfline-ui.service
│       │   ├── record.py
│       │   ├── webui
│       │   │   ├── config.py
│       │   │   ├── core
│       │   │   │   ├── cache.py
│       │   │   │   ├── __init__.py
│       │   │   │   ├── pl_api.py
│       │   │   │   └── utils.py
│       │   │   ├── install-systemd-service
│       │   │   ├── perfline_proxy.sh
│       │   │   ├── perf_result_parser.py
│       │   │   ├── pl-web-ctl
│       │   │   ├── pl-web.service.template
│       │   │   ├── server.py
│       │   │   ├── stats
│       │   │   ├── stats.py
│       │   │   ├── styles
│       │   │   │   └── report.css
│       │   │   ├── task_templates
│       │   │   │   └── s3bench.yaml
│       │   │   └── templates
│       │   │       ├── artifacts.html
│       │   │       ├── gif
│       │   │       │   ├── beavis.gif
│       │   │       │   ├── dog.gif
│       │   │       │   └── spinner.gif
│       │   │       ├── index.html
│       │   │       ├── log.html
│       │   │       ├── queue.html
│       │   │       ├── results.html
│       │   │       ├── scripts
│       │   │       │   ├── angular.min.js
│       │   │       │   ├── angular-route.min.js
│       │   │       │   ├── bootstrap.min.css
│       │   │       │   ├── bootstrap.min.js
│       │   │       │   ├── jquery.min.js
│       │   │       │   └── ui-bootstrap-tpls-2.5.0.min.js
│       │   │       ├── stats.html
│       │   │       └── task.html
│       │   ├── wrapper
│       │   │   ├── perfline.py
│       │   │   ├── run_pl
│       │   │   ├── scripts
│       │   │   │   ├── fio-template
│       │   │   │   │   ├── rand_fio
│       │   │   │   │   ├── randmix_20-80_fio
│       │   │   │   │   ├── randmix_80-20_fio
│       │   │   │   │   ├── seq_read_fio
│       │   │   │   │   └── seq_write_fio
│       │   │   │   ├── merge_m0playdb
│       │   │   │   ├── process_addb
│       │   │   │   ├── process_addb_data.sh
│       │   │   │   ├── run_fiobenchmark.sh
│       │   │   │   ├── run_m0crate
│       │   │   │   ├── s3bench_run.sh
│       │   │   │   ├── save_m0traces
│       │   │   │   ├── test_io.yaml.template
│       │   │   │   ├── wait_s3_listeners.sh
│       │   │   │   └── worker.sh
│       │   │   ├── stat
│       │   │   │   ├── 5u84stats.sh
│       │   │   │   ├── collect_static_info.sh
│       │   │   │   ├── extract_disks.py
│       │   │   │   ├── report_generator
│       │   │   │   │   ├── gen_pages
│       │   │   │   │   │   └── gen_home.html
│       │   │   │   │   ├── gen_report.py
│       │   │   │   │   ├── m0crate_log_parser.py
│       │   │   │   │   ├── s3bench_log_parser.py
│       │   │   │   │   ├── styles
│       │   │   │   │   │   └── stats.css
│       │   │   │   │   └── templates
│       │   │   │   │       ├── addb.html
│       │   │   │   │       ├── blktrace.html
│       │   │   │   │       ├── common_info.html
│       │   │   │   │       ├── dstat.html
│       │   │   │   │       ├── home.html
│       │   │   │   │       ├── iostat.html
│       │   │   │   │       ├── navigation.html
│       │   │   │   │       ├── report_summary.html
│       │   │   │   │       ├── text_cluster.html
│       │   │   │   │       ├── text_commit_info.html
│       │   │   │   │       ├── text_cpu.html
│       │   │   │   │       ├── text_disks_mapping.html
│       │   │   │   │       ├── text_haproxy.html
│       │   │   │   │       ├── text_hosts.html
│       │   │   │   │       ├── text_info.html
│       │   │   │   │       ├── text_interfaces.html
│       │   │   │   │       ├── text_lnet.html
│       │   │   │   │       ├── text_memory.html
│       │   │   │   │       ├── text_motr.html
│       │   │   │   │       ├── text_multipath.html
│       │   │   │   │       ├── text_nodes_mapping.html
│       │   │   │   │       └── text_s3_config.html
│       │   │   │   ├── start_stats_service.sh
│       │   │   │   └── stop_stats_service.sh
│       │   │   ├── sys
│       │   │   │   └── config.py
│       │   │   ├── task_validation
│       │   │   │   ├── tasks.py
│       │   │   │   └── validator.py
│       │   │   └── workload
│       │   │       ├── example.yaml
│       │   │       ├── m0crate.128m.yaml
│       │   │       ├── m0crate.16m.yaml
│       │   │       ├── m0crate.1m.yaml
│       │   │       ├── m0crate.256k.yaml
│       │   │       ├── perfline.task.yaml
│       │   │       ├── s3bench.32mb.yaml
│       │   │       ├── s3bench.yaml
│       │   │       └── sleep.yaml
│       ├── handlers
│       │   └── main.yml
│       ├── tasks
│       │   ├── enable_passwordless.yml
│       │   ├── main.yml
│       │   ├── pre-req_perfline.yml
│       │   └── taskq.yml
│       └── vars
│           └── main.yml
└── run_perfline.yml
```
