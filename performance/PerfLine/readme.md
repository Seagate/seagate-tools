
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
  iostat: false
  dstat: false
  blktrace: false
  glances: false
  
# List of benchmarks and parameters. This section must include
# at least one benchmark (custom/fio/s3bench/m0crate).
benchmarks:
  - custom:
      cmd: sleep 1
  - lnet:
      LNET_OPS: read,write,ping              # user can pass value operation separated by ',' Ex: read,write,ping
  - fio:
      Duration: 600
      BlockSize: 8M
      NumJobs: 32
      Template: seq_read_fio       #Template for fio like seq_read_fio, seq_write_fio, randmix_80-20_fio, randmix_20-80_fio and rand_fio
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
  - iperf:
      Interval: 1
      Duration: 60
      Parallel: 2


execution_options:
  mkfs: false
  collect_m0trace: false
  collect_addb: false
  backup_result: false
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

