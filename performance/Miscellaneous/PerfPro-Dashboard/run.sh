#!/bin/bash

yum install -y git
GIT_USER=`cat secret | grep GIT_USER_NAME | awk '{print$3}'`
GIT_PASS=`cat secret | grep GIT_USER_PASS | awk '{print$3}'`
git clone --recursive https://$GIT_USER:$GIT_PASS@github.com/Seagate/cortx-test.git -b dev

# install and upgrade pip
if [ -z `rpm -qa | grep -i python3-pip` ]
then
echo "*************Installing pip3 in your system*******************"
yum install -y python3-pip
else
echo "pip3 is already present"
fi
echo "upgrading pip"
pip3 install --upgrade pip

# installing required modules
cur_path=$(pwd)
req_path="/cortx-test/tools/dash_server/requirements.txt"
install_path=$cur_path$req_path
#echo "$install_path"
pip3 install -r $install_path
echo "*************All required package are installed***************"

#making new directories 'prod' and 'main'
mkdir -p  dashboards/prod dashboards/main

# deplyoing tmux sessions
echo "*************Installing tmux in your system*******************"
yum install -y tmux
echo "*************Created new tmux session dashboard-main**********"
tmux new -d -s dashboard-main "bash --init-file port_update_run.sh"
echo "*************Created new tmux session dashboard-prod**********"
tmux new -d -s dashboard-prod "bash --init-file port_update_run.sh"
echo "use: 'tmux attach-session -t dashboard-main' for dashboard-main opertaing at port5012"
echo "use: 'tmux attach-session -t dashboard-prod' for dashboard-port opertaing at port5022"
