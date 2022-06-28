# !/bin/bash

# Installing git
yum install -y git
GIT_USER=$(grep GIT_USER_NAME secret | awk '{print$3}')
GIT_PASS=$(grep GIT_USER_TOKEN secret | awk '{print$3}')

# Making new directories 'prod' and 'main'
mkdir -p  dashboards/prod dashboards/main

# Install and Configure python3.7
cur_path=$(pwd)
yum install -y gcc openssl-devel bzip2-devel libffi libffi-devel zlib-devel xz-devel
wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz -P dashboards/
tar -xvzf dashboards/Python-3.7.12.tgz -C dashboards/
cd dashboards/Python-3.7.12/
./configure --enable-optimizations
make altinstall
echo "*********************Installed and Configured Python3.7.12***********************"
cd "$cur_path"/

# Install and upgrade pip
if [ -z $(rpm -qa | grep -i python3-pip) ]
then
    echo "******************Installing and Upgrading pip in your system********************"
    yum install -y python3-pip
else
    echo "pip3 is already present"
fi
pip3.7 install --upgrade pip

# Create virtual environment
pip3.7 install virtualenv
virtualenv -p /usr/local/bin/python3.7 dashboards/venv
source dashboards/venv/bin/activate
echo "**************************Created Virtual Environment***************************"

# Installing required modules
cur_path=$(pwd)
req_path="/../requirements.txt"
install_path=$cur_path$req_path
pip3.7 install -r "$install_path"
echo "***********************All required package are installed***********************"


# Deplyoing tmux sessions
echo "**************************Installing tmux in your system************************"
yum install -y tmux
echo "**********************Created new tmux session dashboard-main*******************"
tmux new -d -s dashboard-main "bash --init-file port_update_run.sh"
echo "************** *******Created new tmux session dashboard-prod*******************"
tmux new -d -s dashboard-prod "bash --init-file port_update_run.sh"
echo "use: 'tmux attach-session -t dashboard-main' for dashboard-main opertaing at port5012"
echo "use: 'tmux attach-session -t dashboard-prod' for dashboard-port opertaing at port5022"
