#!/bin/bash

yum install -y git
GIT_USER=`cat secret | grep GIT_USER_NAME | awk '{print$3}'`
GIT_PASS=`cat secret | grep GIT_USER_PASS | awk '{print$3}'`
git clone --recursive https://$GIT_USER:$GIT_PASS@github.com/Seagate/cortx-test.git -b dev
if [ $? -eq 0 ]
then
echo "************Cloned the 'Cortx-test' repository***************"
else
echo "************Wrong USERNAME or PASSWORD provided**************"
echo "************************ EXITING*****************************"
exit 
fi

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

CFT_DB_USERNAME=`cat secret | grep CFT_DB_USER_NAME  | awk '{print$3}'`
CFT_DB_USERPASS=`cat secret | grep CFT_DB_USER_PASS  | awk '{print$3}'`
PERF_DB_USERNAME=`cat secret | grep PERF_DB_USER_NAME | awk '{print$3}'`
PERF_DB_USERPASS=`cat secret | grep PERF_DB_USER_PASS | awk '{print$3}'`

# updating username and passswords of configs.yml
# <file_path: cortx-test/tools/dash_server/Performance/configs.yml>
python3 update_config_yml.py $PERF_DB_USERNAME $PERF_DB_USERPASS


# updating username and passswords of configs.ini
# <file_path: cortx-test/tools/dash_server/config.ini>
python3 update_config_ini.py $CFT_DB_USERNAME $CFT_DB_USERPASS $PERF_DB_USERNAME $PERF_DB_USERPASS

#making new directories 'prod' and 'main'
mkdir prod main

# deplyoing tmux sessions
echo "*************Installing tmux in your system*******************"
yum install tmux
echo "*************Created new tmux session dashboard-main**********"
tmux new -d -s dashboard-main "bash --init-file port_update_run.sh"
echo "*************Created new tmux session dashboard-prod**********"
tmux new -d -s dashboard-prod "bash --init-file port_update_run.sh"
echo "use: 'tmux attach-session -t dashboard-main' for dashboard-main opertaing at port5012"
echo "use: 'tmux attach-session -t dashboard-prod' for dashboard-port opertaing at port5022"



