# Environment deployment

CORTX stack deployment requires many manual steps to be run before developer may start working on code.
Typical installation steps require: 
1.  Installation of K8s environment using Jenkins job
2.  Building custom/main/stable CORTX images (cortx-data, cortx-rgw, cortx-control) using Jenkins job
3.  Installation of Service Framework scripts using Jenkins job
4.  Manual steps for cluster deployment/bootstrap/stop/start
5.  Manual run of workloads and tests
6.  Manual collection of run artifacts, like logs, traces, configuration files and ADDB stobs.

While PerfLine standard setup automates items 4-6, there are still one-time manual actions required for cluster deployment. Goal of this `env` component is automate items 1 and 3 from the list, and allow fast deployment cycle at the cost of pre-defined node configuration (see Requirements section).

## Requirements

The following HW pre-requisites shall be met for each cluster node prior to installation:
1.  RAM: 16 Gb
2.  CPU: 8 Cores
3.  Disk: At least 8 disks, 25Gb+ each
4.  Disk layout
    There is a specific requirement for disks layout. 
    ```console
    # ls /dev/sd*
    /dev/sdb  /dev/sdc  /dev/sdd  /dev/sde  /dev/sdf  /dev/sdg  /dev/sdh  /dev/sdi
    ```

Software limitations:
1.  CORTX Service Framework deployment scripts path can't be changed and will be installed at `/root/deploy-scritps`
    
## Installation

1.  Clone `seagate-tools` repo
    ```console
    # git clone https://github.com/Seagate/seagate-tools
    # cd performance/PerfLine/env
    ```

2.  Specify hostname, username and passwords for all cluster nodes in `input.yaml` file
    In case of the latest version of `cortx-re`, `Service Framework` and `PerfLine` components are required, corresponding fields may be skipped, and installation script will use the latest ones.
    ```yaml
    specification:
      config: auto
      nodes:
        - hostname: node1-hostname   # <- Specify hostname 
          username: node1-username   # <- Specify username
          password: node1-password   # <- Specify password
        - hostname: node2-hostname   # <- Specify hostname 
          username: node2-username   # <- Specify username
          password: node2-password   # <- Specify password
        - hostname: node3-hostname   # <- Specify hostname 
          username: node3-username   # <- Specify username
          password: node3-password   # <- Specify password
      cortx_re:
        repo: https://github.com/Seagate/cortx-re
        branch: main
      service_framework:
        repo: https://github.com/Seagate/cortx-k8s
        branch: v0.8.0
	disk:                        # <- Specify Service Framework 
                                     # PODs local filesystem, or leave
                                     # empty by default
      perfline:
        repo: https://github.com/seagate/seagate-tools.git
        branch: main
      durability:
        sns: 1+0+0
        dix: 1+0+0
    ```
   
3.  Run installation script
    ```console
    # ./install_dev_env.sh input.yaml
    ```

4.  Wait until installation is completed (~15 minutes)

5.  Check PerfLine installation by running PerfLine example workload
    ```console
    # cd ~/perfline/wrapper
    # ./perfline.py -a < workload/example.yaml
    ```

## Partial installation

Installation script allows to perform partial installation, if it's required to deploy cluster without one of components. For instance, if it's only required to deploy cluster without PerfLine installation, or redo PerfLine installation withou re-installation of K8s framework and re-deployment of cluster.
`install_dev_env.sh` provides list of options that can be used to meet user goals:
```console
# ./install_dev_env.sh --help
Usage : ./install_dev_env.sh [--spec input.yaml] [--skip-k8s] [--skip-deployment] [--skip-perfline]
where,
    --spec file - Run script with specified specification file.
                  Default input.yaml is used when not specified.
    --skip-k8s - Skip K8s env installation.
    --skip-deployment - Skip CORTX cluster deployment.
    --skip-perfline - Skip PerfLine installation.
```

### Examples

Cluster deployment without PerfLine

```console
# ./install_dev_env.sh --skip-perfline
```

Re-installtion of PerfLine (assumed that cluster already deployed)

```console
# ./install_dev_env.sh --skip-k8s --skip-deployment
```