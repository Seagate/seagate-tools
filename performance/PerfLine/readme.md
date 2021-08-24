
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
 
    ```
    [nodes]
    srvnode-1 ansible_host=<PRIMARY NODE-FQDN>
    srvnode-2 ansible_host=<SECONDARY NODE-FQDN>
    srvnode-3 ansible_host=<TERTIARY NODE-FQDN>

    [client]
    client-1 ansible_host=<CLIENT NODE-FQDN>

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

    4.3 It will allow user to run perfline workload automatically like a cron jobs for a list of stable build. This workloads will run over the weekends( from friday mid night). If you do not want to enable daemon service then please mark it as "no".

    ```
    enable_daemon_service='yes'
    ```
    4.4 Default root password is "seagate1" for cortx cluster including client, If user having different password then please update on "./inventories/perfline_hosts/hosts"
    ```
    cluster_pass=
    ```

# Installation
1. When prerequisites are satisfied you need to `# cd` to `PerfLine` directory and run:
`# ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v`

2. Wait till ansible installiation finishes on provided nodes under location 
	2.1 executables  at `/root/perfline`
	2.2 results at `/var/perfline`
	2.3 log file at `/var/log/perfline.log`

If you want to install PerfLine into non-default directory you can specify `PURPOSE`
variable at `PerfLine/roles/perfline_setup/vars/main.yml` before playbook execution.
`PURPOSE` variable affects PerfLine directory, artifacts directory, log file location
and systemd services names. By default `PURPOSE` is an empty string. Setting the value
of this variable to `-dev` will change:
  executables: `/root/perfline-dev`
  results: `/var/perfline-dev`
  log file: `/var/log/perfline-dev.log`
  systemd services names: `perfline-dev`, `perfline-ui-dev`

In case you want to install more than one version of PerfLine on the same cluster you have
to specify `PURPOSE` variable described above and change value of `perfline_ui_port` variable
specified in `PerfLine/inventories/perfline_hosts/hosts` file to garantee that different
instances of PerfLine use different ports for UI service.

# Define own workload
As per need, Create a "<any name of your choice>.yaml" file inside `/root/perfline/wrapper/workload` directory. An expample.yaml is already provided for user's reference.
Custom build:
```
1. User have an optional feature to update R2 Cluster either using URL or can use specific commitID of IO-PATH components.
2. User can provide any working git committ hash/ID combination for io-path components as long as user can ensure build won't fail. CORTX build on cluster would be updated accordingly.
```
Order of execution and multiple execution of same workloads are allowed for benchmarks and workloads sections.. 

For ex:
```
common:
  version: 1
  description: Perf benchmark example
  priority: 1
  batch_id: null
  user: user@seagate.com
  send_email: false

#Either of the option you to choose like URL or IO-PATH components
custom_build:
  url: ""
  motr:
    repo: "https://github.com/Seagate/cortx-motr.git"
    branch: b64b1bba
  s3server:
    repo: "https://github.com/Seagate/cortx-s3server.git"
    branch: c482a593
  hare:
    repo: "https://github.com/Seagate/cortx-hare.git"
    branch: daddc4a

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
  - iperf:
      Interval: 1
      Duration: 60
      Parallel: 2

workloads:
  - custom:
      cmd: sleep 1
  - s3bench:
      BucketName: mybucket
      NumClients: 10
      NumSample: 100
      ObjSize: 32Mb
      EndPoint: https://s3.seagate.com
  - m0crate:
      NR_INSTANCES_PER_NODE: 2
      NR_THREADS: 2
      BLOCK_SIZE: 2m
      IOSIZE: 4m


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

# Daemon services
If user has enable daemon service then It would required to specify the build number to '/root/perfline/wrapper/.latest_stable_build' on client server. It's a one time activity. It will take the list of build above it and including "BUILDNO" value.
```
BUILDNO=307
```

# DISCLAIMER / WARNING
PerfLine is a tool, not a service, which is available to users to install and use at their own setups/machines. For multi-user use, PerfLine provide all required infrastructure with task/run queues and optional email notifications. But, It is outside scope of PerfLine to ensure that nothing runs outside of PerfLine infrastructure on user machines, when PerfLine is executing tasks/runs. This islolation is necessary for accurate data measurements / artifacts collection and must be ensured by user. If not ensured, results might have data which is adulterated unintentionally and accuracy compromised due to user machines being shared and used in parallel to PerfLine.

# Known Issues
Description:
- Perfline installation process will generate it's own key-pair, and it will add new identity file on "/etc/sshd/ssh_config" then it will execute reload  sshd service on all cortx servers. But we had noticed, Cortx cluster automatically reverted back to previous version of "ssh_config" file, which is responsible for connection lost.
 
- Solution: This issues occurred due to puppet service. 
To solve this issues, Please run below command on all cortx servers:
```
systemctl stop puppet
systemctl disable puppet
```
