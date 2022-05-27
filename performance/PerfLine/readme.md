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
    It's recommended to use version v0.6.0 (commit 9469028b18aad22a34e0154a0f64ae6bb8028072) of `cortx-k8s`.

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

## 'Build and deploy' feature

PerfLine allows to deploy a cluster using any prebuilt Cortx docker images (stable/custom).
Also PerfLine is able to build custom Cortx images in case if user specifies list of commits
and repos of the source code.

### Deployment the cluster with prebuilt Cortx docker images

User may specify list of PODs and corresponding Cortx images to deploy. In that case
PerfLine will update PODs and images in the `solution.yaml` file and redeploy the cluster.

Example of `custom_build` section in the `workload.yaml` file:

    custom_build:
      images:
        cortxdata:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
        cortxcontrol:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
        cortxserver:
          image: ghcr.io/seagate/cortx-rgw:2.0.0-735
        cortxha:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
        cortxclient:
          image: ghcr.io/seagate/cortx-all:2.0.0-735

User may specify any Cortx images (stable/custom). But at the same time user is responsible for the
correct choice of them. Cortx images have to be compatible with the current version of Cortx
framework (cortx-k8s project). And they have to be compatible with the corresponding PODs as well.
PerfLine doesn't take care about it. In case if specified images are not compatible with framework
and/or PODs PerfLine task fails.

### Deployment the cluster with 'patched' prebuilt Cortx docker images

From time to time developers want to check how their changes affect the behaviour of the cluster.
In that case developers may to build custom Cortx images from the source code (using Jenkins job) and then to specify these images as described above.
But building Cortx from source code takes up to several hours. In order to reduce time for testing patches PerfLine provides 'patch the prebuilt image' feature. An idea of this feature is not to build Cortx images from scratch but replace binary files of Motr/Hare in a prebuilt image with the binary files built by developer itself.
For example developer has sources of Motr/Hare in the /root directory. Developer builds Motr/Hare projects using `make` commands. It takes less time than building Cortx docker images (especially once Motr/Hare are already build for the first time). As a result of `make` Motr/Hare directories contains binary files. These files will be copied into specified prebuilt Cortx docker image (actually a new temporary image will be created). Then PerfLine will redeploy the cluster.

Example of `custom_build` section in the `workload.yaml` file:

    custom_build:
      images:
        cortxdata:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
          motr_patch: /root/cortx-motr
          hare_patch: /root/cortx-hare
        cortxcontrol:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
        cortxserver:
          image: ghcr.io/seagate/cortx-rgw:2.0.0-735
        cortxha:
          image: ghcr.io/seagate/cortx-all:2.0.0-735
        cortxclient:
          image: ghcr.io/seagate/cortx-all:2.0.0-735

There is only difference from the previous example. It is `motr_patch`/`hare_patch` fields in the `cortxdata` POD description. In this case PerfLine will generate a new temporary docker image based on `ghcr.io/seagate/cortx-all:2.0.0-735`. PerfLine will replace all Motr/Hare binary files in the temporary image with files located in the `/root/cortx-motr` and `/root/cortx-hare` directories. Then PerfLine will copy the image to all nodes and redeploy the cluster.

  **Note : User is responsible for building Motr/Hare manually before scheduling a PerfLine task. Also user is responsible for providing compatibility between Motr/Hare and other components/files in the base Cortx docker image. PerfLine doesn't provide any guarantee.**

Temporary Cortx docker images are being used for deployment the cluster. Once task is finished all temporary images will be removed by PerfLine automtically.

### Building Cortx docker images from the source code

PerfLine is able to build custom Cortx images from the source code and use them for deployment the cluster.
In order to build Cortx images user has to provide list of commits/repos for required Cortx components.

For example:

    custom_build:
      sources:
        motr:
          repo: "https://github.com/Seagate/cortx-motr.git"
          branch: 7d8c1957
        rgw:
          repo: "https://github.com/Seagate/cortx-rgw.git"
          branch: 107dce0a93f84722936f2dd10bb5273402d45772
        rgw-integration:
          repo: https://github.com/Seagate/cortx-rgw-integration.git
          branch: 04b3de2df1b8ebf4711e5984dd9908b62fa579a1
        hare:
          repo: "https://github.com/Seagate/cortx-hare.git"
          branch: e405edf
        utils:
          repo: https://github.com/Seagate/cortx-utils.git
          branch: 27067f11608ddd2a7b5b5b0a7e5266b9472323a6
        prvsnr:
          repo: https://github.com/Seagate/cortx-prvsnr.git
          branch: 9c2b067d0621b65e83ba2216490039d8dfa3862c

List of projects in the `sources` section may include any set of Cortx submodules (cortx-motr/cortx-hare/cortx-rgw/etc). Full list of Cortx submodules can be found [here](https://github.com/Seagate/cortx).
Each project description in the `sources` section has to include `repo` field and `branch` field.
`repo` field can be either an URL for a remote git repo or path to local directory on the primary PerfLine node. For example:

    custom_build:
      sources:
        motr:
          repo: "/root/cortx-motr"
          branch: "my_feature_branch"

In the above example Motr repo specified as a local path. This local repo (on the primary PerfLine node) will be used as source code for Motr building.

`branch` field can contain either commit hash or branch name. For example:

    custom_build:
      sources:
        motr:
          repo: "https://github.com/Seagate/cortx-motr.git"
          branch: 7d8c1957
        rgw:
          repo: "https://github.com/Seagate/cortx-rgw.git"
          branch: my_feature_branch

In the above example Motr commit is represented by commit hash and RGW commit is represented by branch name. PerfLine will checkout specified commits/branches during 'build' phase execution.

**Note : User is responsible for compatibility all Cortx components with each other.**

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
      url: "http://cortx-storage.colo.seagate.com/releases/cortx/github/stable/centos-7.8.2003/272"
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
