
# Perfline
PerfLine is primarily a CORTX Profiler. It has extended capabilities of running different benchmarks and microbenchmarks and other custom workloads in multi-user shared environment.
It consists of three modules:
- wrapper - Executables including report generator, statistic gather scripts
- webui - Web server based PerfLine UI for interacting with PerfLine
- ansible playbook - Ansible based PerfLine Installation

# Prerequisites
PerfLine can be installed from any machine, To setup PerfLine or deploying PerfLine on a client, following prerequisites must be satisfied:
1. Choose Machine, from which installation will be performed, It can be any machine(PerfLine wont be installed here unless configured to do so)
2. Latest version of seagatetools repo downloaded
3. Ansible package installed (ver. 2.9+)
4. Setup config for cluster nodes
    4.1 Change ./inventories/perfline_hosts/hosts file and set target cluster nodes dns-name/ip. Accordingly for nodes and client groups.
 Build machine is optional to user, if user want to create new build for io-path components on LR2 setup.
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
    4.2 Change ./inventories/perfline_hosts/hosts file and set target ha_type.
    ```
    [all:vars]
    ansible_connection=ssh
    ansible_user=root
    ha_type=pcs
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ```
    For Minimal(io-path components) configuration `ha_type=hare`
    For Complete cluster configuration `ha_type=pcs`

    4.3 Default root password is "seagate1" for cortx cluster including client, If user having different password then please update on "./inventories/perfline_hosts/hosts"
    ```
    cluster_pass=seagate1
    ```

# Installation
1. When prerequisites are satisfied you need to `# cd` to `PerfLine` directory and run:
`# ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v`

2. Wait till ansible installiation finishes on provided nodes under location 
	2.1 executables  at `/root/perfline`
	2.2 results at `/var/perfline`
	2.3 log file at `/var/log/perfline.log`

If you want to install PerfLine into non-default directory you can specify `POSTFIX`
variable at `PerfLine/roles/perfline_setup/vars/main.yml` before playbook execution.
`POSTFIX` variable affects PerfLine directory, artifacts directory, log file location
and systemd services names. By default `POSTFIX` is an empty string. Setting the value
of this variable to `-dev` will change:
  executables: `/root/perfline-dev`
  results: `/var/perfline-dev`
  log file: `/var/log/perfline-dev.log`
  systemd services names: `perfline-dev`, `perfline-ui-dev`

In case you want to install more than one version of PerfLine on the same cluster you have
to specify `POSTFIX` variable described above and change value of `perfline_ui_port` variable
specified in `PerfLine/inventories/perfline_hosts/hosts` file to garantee that different
instances of PerfLine use different ports for UI service.

# Define own workload
As per need, Create a "<any name of your choice>.yaml" file inside `/root/perfline/wrapper/workload` directory. An expample.yaml is already provided for user's reference.
Custom build:
```
1. If user want to use build-deploy(uses seagate internal docker service) feature then user must generate "github personal access token"(github_PAT) and need to provide it along with "github username" in workload yaml file, otherwise user can move ahead with build-deploy(using docker service for external community) without "github_PAT" and "github_username". External docker service is slow and takes more time to build. Hence it is highly encouraged for seagate-internal users to use internal docker service.
2. User have an option to choose build machine either VM or HW machine.
3. No need to mention anything for motr_repo_path, hare_repo_path and s3server_repo_path. This feature is currently disabled, as build service only support building main branch code which is default and need not be metioned vi repo_path parameters.
4. User can provide any working git committ hash/ID combination for io-path components as long as user can ensure build won't fail. CORTX build on cluster would be updated accordingly. If not provided, default is ToT branch mentioned in bullet 3 above.
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

# DISCLAIMER / WARNING
PerfLine is a tool, not a service, which is available to users to install and use at their own setups/machines. For multi-user use, PerfLine provide all required infrastructure with task/run queues and optional email notifications. But, It is outside scope of PerfLine to ensure that nothing runs outside of PerfLine infrastructure on user machines, when PerfLine is executing tasks/runs. This islolation is necessary for accurate data measurements / artifacts collection and must be ensured by user. If not ensured, results might have data which is adulterated unintentionally and accuracy compromised due to user machines being shared and used in parallel to PerfLine.
