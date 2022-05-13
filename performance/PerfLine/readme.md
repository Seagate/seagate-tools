# Perfline

PerfLine is primarily a cortx Profiler. It has extended capabilities of running different benchmarks and microbenchmarks and other custom workloads in multi-user shared environment.
It consists of three modules:

-   wrapper - Executables including report generator, statistic gather scripts
-   webui - Web server based PerfLine UI for interacting with PerfLine
-   ansible playbook - Ansible based PerfLine Installation

## Prerequisites

PerfLine can be installed from any machine. Below prerequisites must be satisfied to setup PerfLine or deploying PerfLine on a client:

1.  Please follow below link to deploy CORTX cluster using the services framework:
    [service_framework](https://seagate-systems.atlassian.net/wiki/spaces/PUB/pages/754155622/CORTX+Kubernetes+Deployment+Document+using+Services+Framework)

    Stable version of `cortx-k8s` repository is required to clone into `/root/cortx-k8s` directory of primary server node.
    It's recommended to use version v0.0.22 or below version of `cortx-k8s`.

    NOTE:  starting from `cortx-k8s` v0.1.0 the default s3 application is RGW. In case if you need to use
    s3server please use v0.0.22 (commit c4773d6fe7b6d1c2b76a69ea2ab0f9582fc660e0) of `corxt-k8s`
    and update `S3_APP` value of the `perfline.conf` file using command below:

        sed -i 's/S3_APP="rgw"/S3_APP="s3srv"/' ./roles/perfline_setup/files/perfline.conf

2.  Choose host machine, from which installation of PerfLine will be performed on remote machine. It can be any machine.
    **Note: PerfLine won't be installed on the same host machine until unless you configured it on "hosts" file as mention in step 5.1**

3.  Clone latest version of seagate-tools repo on your host machine.
4.  Ensure about Ansible package must be installed (ver. 2.9+) on host machine.
5.  Configure neccessary cluster details

    5.1.  Update `./inventories/perfline_hosts/hosts` file and set target cluster nodes dns-name/ip. Accordingly for nodes and client groups.

    **Note: Here is no limit on adding cluster nodes. you can add as much you want.**

        [nodes]
        srvnode-1 ansible_host=<PRIMARY NODE-FQDN>
        srvnode-2 ansible_host=<SECONDARY NODE-FQDN>
        srvnode-3 ansible_host=<TERTIARY NODE-FQDN>

        [client]
        client-1 ansible_host=<CLIENT NODE-FQDN>

    5.2  Update `./inventories/perfline_hosts/hosts` file and set target `ha_type`.

        [all:vars]
        ansible_connection=ssh
        ansible_user=root
        ha_type=pcs
        ansible_ssh_common_args='-o StrictHostKeyChecking=no'

    **Note: For LR cluster below options would be required. But for LC setup, It should be `ha_type=hare`.**

    -   For Minimal(io-path components) configuration `ha_type=hare`.
    -   For Complete cluster configuration `ha_type=pcs`.

    5.3   It will allow user to run perfline workload automatically like a cron jobs for a list of stable build. This workloads
    will run over the weekends( from friday mid night). If you do not want to enable daemon service then please mark it as `"enable_daemon_service=no"`.

        enable_daemon_service='yes'

    5.4  It's mandatory to add root password for cortx cluster including client.
    **Note : It's mandatory to use common password for all.**

        cluster_pass=

## Installation

1.  When prerequisites are satisfied you need to `# cd` to `PerfLine` directory and run:
    `# ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v`

2.  Wait till ansible installiation finishes on provided nodes under location
    1.  executables  at `/root/perfline`
    2.  results at `/var/perfline`
    3.  log file at `/var/log/perfline.log`

### Multiple Instance of PerfLine

-   If you want to install PerfLine into non-default directory you can specify `PURPOSE`.

-   Variable at `PerfLine/roles/perfline_setup/vars/main.yml` before playbook execution.

-   `PURPOSE` variable affects PerfLine directory, artifacts directory, log file location and systemd services names.

    For example:
    By default `PURPOSE` is an empty string. Setting the value
    of this variable to `-dev` will change:
        executables: `/root/perfline-dev`
        results: `/var/perfline-dev`
        log file: `/var/log/perfline-dev.log`
        systemd services names: `perfline-dev`, `perfline-ui-dev`

  **Note : In case, if you want to install more than one version of PerfLine on the same cluster then you have to specify `PURPOSE` variable described above and change the value of `perfline_ui_port` variable which is specified in `PerfLine/inventories/perfline_hosts/hosts` file to guarantee that different instances of PerfLine use different ports for UI service.**

## Define own workload

As per need, Create a `"<any name of your choice>.yaml"` file inside `/root/perfline/wrapper/workload` directory. An example.yaml is already provided for user's reference.

## Custom build

1.  User have an optional feature to update LR Cluster either using URL or can use specific commitID of IO-PATH components.
2.  User can provide any working git committ hash/ID combination for io-path components as long as user can ensure build won't fail. CORTX build on cluster would be updated accordingly.

## Workload

Order of execution and multiple execution of same workload are allowed for benchmarks and workloads sections.

For ex:

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
          EndPoint: http://s3.seagate.com:30080
      - m0crate:
          NR_INSTANCES_PER_NODE: 2
          NR_THREADS: 2
          BLOCK_SIZE: 2m
          IOSIZE: 4m


    execution_options:
      mkfs: false
      collect_m0trace: false
      collect_addb: false
      addb_duration: all
      analyze_addb: false
      backup_result: false

**Note : `benchmarks` section is not supported on LC setup.**

-   New option `addb_duration` is added in `execution_options` secton which will be resposible for collecting addb data for last N minute/second/hr or all.

    Ex:
    addb_duration: 5min

## Starting workload

Workload can be started only from client_node machine
For starting workload on a cluster you need to run tasks, which describing amount/size of files you want to upload/download and how many clients will perform load.

You can find examples of such tasks at `/root/perfline/wrapper/workload`
After you choose/wrote task description, you need to `# cd /root/perfline/wrapper` and than run task with:

`# ./perfline.py  -a < workload/<example>.yaml`

or

`# python3 perfline.py  -a < workload/<example>.yaml`

## Additional info

### Webui

After successful execution of ansible playbook, you should be able to access webui page from browser at `"http://<client_ip>:8005"`.

-   At the main page you will see 4 graphs, that display the results of performance loads for different IO/Session sizes. Garphs can be generated only when you have some history of data on your machine.
-   At Queue page you will find current running tasks and short info about them.
-   At Results page you will be able to see all complete tasks, read/write results will be displayed as short description on results tab for each task. Tasks status, links to their artifacts and report page. If you go to report page you could see detailed report for executed task, including hardware, network, block devices, statistic sctipts infos.

### 8005 is a default port. If you want to change it, you should do it before perfline installation with these steps

-   Update 'perfline_ui_port' variable in 'inventories/perfline_hosts/hosts' as per your choice.

**Note : Ensure that same port will not being used by any services on client machine.**

### Below option is only applied for `LR` setup

-   If you have different `PUBLIC_DATA_INTERFACE_NAME` other than `data0|enp179s0|enp175s0f0|eth0` interface, then you have to provide `PUBLIC_DATA_INTERFACE_NAME` in `roles/perfline_setup/vars/main.yml`. These interface name will be going to use by iperf workload only.

## Daemon services

This feature will allow user to run nightly build, test and run perfline workload for subsequent build number till date. It would be required to specify the build number to `/root/perfline/wrapper/.latest_stable_build` on client server. It's a one time activity. It will take the list of build above it and including "BUILDNO" value.

    BUILDNO=307

## DISCLAIMER / WARNING

PerfLine is a tool, not a service, which is available to users to install and use at their own setups/machines. For multi-user use, PerfLine provide all required infrastructure with task/run queues and optional email notifications. But, It is outside scope of PerfLine to ensure that nothing runs outside of PerfLine infrastructure on user machines, when PerfLine is executing tasks/runs. This islolation is necessary for accurate data measurements / artifacts collection and must be ensured by user. If not ensured, results might have data which is adulterated unintentionally and accuracy compromised due to user machines being shared and used in parallel to PerfLine.

## Known Issues

Description:

-   Perfline installation process will generate it's own key-pair, and it will add new identity file on "/etc/sshd/ssh_config" then it will execute reload  sshd service on all cortx servers. But we had noticed, Cortx cluster automatically reverted back to previous version of "ssh_config" file, which is responsible for connection lost.

-   Solution: This issues occurred due to puppet service.
    To solve this issues, Please run below command on all cortx servers:

        systemctl stop puppet
        systemctl disable puppet
