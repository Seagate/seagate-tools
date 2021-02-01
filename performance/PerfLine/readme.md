

# Perfline
This is perfline module that allows to run cortx-motr workloads. 
It consists of three modules:
- wrapper - main functionality, report generator, statistic gather scripts
- webui - web server for presenting workload result and controlling over new workloads
- ansible playbook - ansible script for fast perfline setup

# Prerequisites
For automated deploying perfline on a client, following prerequisites must be satisfied:
1. Actual version of seagatetools repo downloaded
2. Ansible package installed (ver. 2.9+)
3. Machine, from which installation will be performed, should have ssh access to cluster nodes by their dns-name/ip (ssh-copy-id) from both end(client-to-srvnode1/2,srvnode1/2-to-client).
4. Setup config for cluster nodes  
    4.1 Change ./inventories/perfline_hosts/hosts file and set target cluster nodes dns-name/ip. Accordingly for nodes and client groups.
    ```
    [nodes]
    srvnode-1 ansible_host=<PRIMARY NODE-FQDN>
    srvnode-2 ansible_host=<SECONDARY NODE-FQDN>

    [client]
    client-1 ansible_host=<CLIENT NODE-FQDN>
    ```
    4.2 Change ./roles/perfline_setup/files/wrapper/sys/config.py and set target nodes names and ha_type.   
    ```
    nodes = 'target1.seagate.com,target2.seagate.com'
    ha_type = 'hare'
    ```
    For VMs configuration `ha_type = hare`  
    For cluster configuration `ha_type = pcs`  

# Installation
When prerequisites is satisfied you need to `# cd` to `PerfLine` directory and run:  
`# ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v`  
After that wait till ansible will copy and install all required artifacts on target nodes and also copy required script on client node to run perfline workload within `/root/perfline`.  

# Define own workload
As per your test cases, Create a "<example>.yaml" file inside `/root/perfline/wrapper/workload` directory . For ex:
```
  common:
  version: 1
  description: Perf benchmark - s3bench, size=, clients=, num=
  priority: 1
  batch_id: null
  user: user@seagate.com
  send_email: false

workload:
  - cmd: sleep 1

benchmark:
  fio: false
  s3bench: True

parameter:
  BucketName: seagate-b1
  NumClients: 128
  NumSample: 2048
  ObjSize: 128Mb

execution_options:
  mkfs: false
  no_m0trace_files: true
  no_m0trace_dumps: true
  no_addb_stobs: true
  no_addb_dumps: true
  no_m0play_db: true
```

# Starting workload
Workload can be started only from client_node machine  
For starting workload on a cluster you need to run tasks, which describing amount/size of files you want to upload/download and how many clients will perform load.  
You can find examples of such tasks at `/root/perfline/wrapper/workload`
After you choose/wrote task description, you need to `# cd /root/perfline/wrapper` and than run task with:  
`# python3 perfline.py  -a < workload/<example>.yaml`  
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
│   └── perfline_hosts
│       └── hosts
├── readme.md
├── roles
│   └── perfline_setup
│       ├── files
│       │   ├── chronometry
│       │   │   ├── addb2db.py
│       │   │   ├── addb2new.py
│       │   │   ├── common
│       │   │   │   ├── common_funcs
│       │   │   │   ├── patch_motr_role_mappings
│       │   │   │   ├── remote_execution
│       │   │   │   ├── sw_ver_check_funcs
│       │   │   │   └── timeout_funcs
│       │   │   ├── corruption_workload
│       │   │   ├── endless_m0crate
│       │   │   ├── endless_s3bench
│       │   │   ├── fio_tests
│       │   │   ├── fom_req.py
│       │   │   ├── fom_req.sh
│       │   │   ├── get_hw_conf.exp
│       │   │   ├── hist__client_req.py
│       │   │   ├── hist__fom_req.py
│       │   │   ├── hist__fom_req_r.py
│       │   │   ├── hist__fom_to_rpc.py
│       │   │   ├── hist__ioo_req.py
│       │   │   ├── hist.py
│       │   │   ├── hist__s3req.py
│       │   │   ├── hist__srpc_to_crpc.py
│       │   │   ├── hist__stio_req.py
│       │   │   ├── io_req.py
│       │   │   ├── ios-hist.sh
│       │   │   ├── io_workload
│       │   │   ├── kill_endless_m0crate
│       │   │   ├── md_req.py
│       │   │   ├── no_motr_trace.patch
│       │   │   ├── p0
│       │   │   ├── p0_hare
│       │   │   ├── queues.py
│       │   │   ├── req_utils.py
│       │   │   ├── restart_ios.sh
│       │   │   ├── run_corruption_task
│       │   │   ├── run_s3_corruption
│       │   │   ├── run_s3_task
│       │   │   ├── run_task
│       │   │   ├── s3_build_fix
│       │   │   │   ├── BUILD.template
│       │   │   │   ├── headers.template
│       │   │   │   ├── libs.template
│       │   │   │   └── rebuildall.sh
│       │   │   ├── s3_corruption_workload
│       │   │   ├── s3_req.py
│       │   │   ├── s3server_integration
│       │   │   │   ├── check_and_create_s3_cred
│       │   │   │   ├── functions
│       │   │   │   ├── patch_haproxy_config
│       │   │   │   ├── s3cli_aws
│       │   │   │   ├── s3cli_configure_aws
│       │   │   │   ├── s3cli_patch_hosts
│       │   │   │   ├── s3cli_s3bench
│       │   │   │   ├── s3_create_user
│       │   │   │   ├── s3_overrides.py
│       │   │   │   └── s3srv_build_prepare
│       │   │   ├── s3_workload
│       │   │   ├── task_queue
│       │   │   │   ├── batch_enqueue
│       │   │   │   ├── batch_results
│       │   │   │   ├── config.py
│       │   │   │   ├── config.yaml
│       │   │   │   ├── issues.txt
│       │   │   │   ├── m0crate.corruption.sample.yaml
│       │   │   │   ├── motr.sample.yaml
│       │   │   │   ├── print_task_results
│       │   │   │   ├── s3bench.corruption.sample.yaml
│       │   │   │   ├── s3.sample.yaml
│       │   │   │   ├── st.sh
│       │   │   │   ├── task_queue.py
│       │   │   │   ├── task_queue.sh
│       │   │   │   ├── tasks.py
│       │   │   │   └── validator.py
│       │   │   └── test_io.yaml.template
│       │   ├── filter.py
│       │   ├── huey_consumer
│       │   ├── perfline.service
│       │   ├── main.py
│       │   ├── perfline
│       │   │   ├── perfline
│       │   │   │   ├── tasks.py
│       │   │   │   └── validator.py
│       │   │   ├── perfline.py
│       │   │   ├── run_pl
│       │   │   ├── scripts
│       │   │   │   ├── merge_m0playdb
│       │   │   │   ├── process_addb
│       │   │   │   ├── save_m0traces
│       │   │   │   ├── wait_s3_listeners.sh
│       │   │   │   └── worker.sh
│       │   │   ├── stat
│       │   │   │   ├── blktrace_start.sh
│       │   │   │   ├── blktrace_stop.sh
│       │   │   │   ├── collect_static_info.sh
│       │   │   │   ├── dstat_start.sh
│       │   │   │   ├── dstat_stop.sh
│       │   │   │   ├── iostat_start.sh
│       │   │   │   ├── iostat_stop.sh
│       │   │   │   └── report_generator
│       │   │   │       ├── gen_pages
│       │   │   │       │   └── gen_home.html
│       │   │   │       ├── gen_report.py
│       │   │   │       ├── styles
│       │   │   │       │   └── stats.css
│       │   │   │       └── templates
│       │   │   │           ├── blktrace.html
│       │   │   │           ├── common_info.html
│       │   │   │           ├── dstat.html
│       │   │   │           ├── home.html
│       │   │   │           ├── iostat.html
│       │   │   │           ├── navigation.html
│       │   │   │           ├── report_summary.html
│       │   │   │           ├── text_cluster.html
│       │   │   │           ├── text_commit_info.html
│       │   │   │           ├── text_cpu.html
│       │   │   │           ├── text_disks_mapping.html
│       │   │   │           ├── text_haproxy.html
│       │   │   │           ├── text_hosts.html
│       │   │   │           ├── text_info.html
│       │   │   │           ├── text_interfaces.html
│       │   │   │           ├── text_lnet.html
│       │   │   │           ├── text_memory.html
│       │   │   │           ├── text_motr.html
│       │   │   │           ├── text_multipath.html
│       │   │   │           ├── text_nodes_mapping.html
│       │   │   │           └── text_s3_config.html
│       │   │   ├── sys
│       │   │   │   └── config.py
│       │   │   └── workload
│       │   │       ├── perfline.task.yaml
│       │   │       ├── s3bench.100k.yaml
│       │   │       ├── s3bench.128m.yaml
│       │   │       ├── s3bench.16m.yaml
│       │   │       ├── s3bench.1m.yaml
│       │   │       ├── s3bench.32mb.yaml
│       │   │       ├── s3bench.mkfs.yaml
│       │   │       ├── s3bench.yaml
│       │   │       └── sleep.yaml
│       │   ├── record.py
│       │   ├── webui
│       │   │   ├── config.py
│       │   │   ├── install-systemd-service
│       │   │   ├── mero-128m.yaml
│       │   │   ├── perfline_proxy.sh
│       │   │   ├── perf_result_parser.py
│       │   │   ├── pl_api.py
│       │   │   ├── pl-web-ctl
│       │   │   ├── pl-web.service.template
│       │   │   ├── s3-128m.yaml
│       │   │   ├── s3bench_mkfs.yaml
│       │   │   ├── s3bench.yaml
│       │   │   ├── server.py
│       │   │   ├── stats
│       │   │   ├── stats.py
│       │   │   ├── styles
│       │   │   │   └── report.css
│       │   │   └── templates
│       │   │       ├── artifacts.html
│       │   │       ├── gif
│       │   │       │   ├── beavis.gif
│       │   │       │   ├── dog.gif
│       │   │       │   └── spinner.gif
│       │   │       ├── index.html
│       │   │       ├── log.html
│       │   │       ├── queue.html
│       │   │       ├── results.html
│       │   │       ├── scripts
│       │   │       │   ├── angular.min.js
│       │   │       │   ├── angular-route.min.js
│       │   │       │   ├── bootstrap.min.css
│       │   │       │   ├── bootstrap.min.js
│       │   │       │   ├── jquery.min.js
│       │   │       │   └── ui-bootstrap-tpls-2.5.0.min.js
│       │   │       ├── stats.html
│       │   │       └── task.html
│       │   └── webui.service
│       ├── handlers
│       │   └── main.yml
│       ├── tasks
│       │   ├── main.yml
│       │   └── taskq.yml
│       └── vars
│           └── main.yml
└── run_perfline.yml
```
