# Cortx-Companion Environment Setup Automation

This directory contains the automation scripts to setup the dashboard environment for development and production where two dashboards are hosted in Dev and Prod mode. This has a dependency on pre hosted mongoDB database with collection names as mentioned in [PerfPro-Database](https://github.com/Seagate/seagate-tools/tree/main/performance/PerfPro/setup-env/)

## Directory Structure

1.  **run.sh**
    -   Executes the required steps to setup the dashboard.
    -   Uses other files for configurations and credentials.

2.  **port_update_run.sh**
    -   Runs dashboards in tmux session.

3.  **update_config_ini.py**
    -   Updates the required 'ini' type configuration files.

4.  **update_config_yml.py**
    -   Updates the required 'yml' type configuration files.

5.  **secret**
    -   Contains the git and dashboards related information.
    -   It has `key = value` format.
    -   Only file need to be edited by user as per requirements.

## Steps to setup

**_Note: use root user mode_**.

1.  Fill the **secret** file template.
2.  Provide execution permission to **run.sh** file.
3.  Run the shell script using below command: `/path/to/run.sh`.

## How to Use

-   Attach tmux sessions using following commands.
    -   To open **main** dashboard: `tmux attach-session -t dashboard-main`.
    -   To open **prod** dashboard: `tmux attach-session -t dashboard-prod`.
