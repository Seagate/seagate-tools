# PerfPro-Dashboard
Automates the development environment for perfpro dashboard on the system.

---

## Directory Structure

 1. run.sh
    -It is a shell script.
    -Executes the required steps to setup the dashboard.
    -Uses other files for configurations and credentials.
 
 2. port_update_run.sh
    -Runs dashboards in tmux session.
 
 3. update_config_ini.py
    -To update the required 'ini' type configuration files.
 
 4. update_config_yml.py
    -To update the required 'yml' type configuration files.
 
 5. secret
    -Contains the git and dashboards related information
    -It has **key = value** format.
    -Only file need to be edited by user as per requirements.

## Steps to setup
Note: use root user mode.

 1. Fill the **secret** file template.
 2. Provide execution permission to **run.sh** file.
 3. Run the shell script using below command:-
 > `/path/to/run.sh`

## How to Use

 1. Attach tmux sessions using following commands.
 > `tmux attach-session -t dashboard-main`
 > `tmux attach-session -t dashboard-prod`
