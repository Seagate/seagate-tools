#!/bin/bash

source dashboards/venv/bin/activate
# echo "$VIRTUAL_ENV"


CFT_DB_USERNAME=$(cat secret | grep CFT_DB_USER_NAME  | awk '{print$3}')
CFT_DB_USERPASS=$(cat secret | grep CFT_DB_USER_PASS  | awk '{print$3}')

PERF_DB_USERNAME=$(cat secret | grep PERF_DB_USER_NAME | awk '{print$3}')
PERF_DB_USERPASS=$(cat secret | grep PERF_DB_USER_PASS | awk '{print$3}')

GIT_USER=$(cat secret | grep GIT_USER_NAME | awk '{print$3}')
GIT_PASS=$(cat secret | grep GIT_USER_TOKEN | awk '{print$3}')


session_name=$(tmux display-message -p '#S')
# echo "$session_name"


if [ "$session_name" == 'dashboard-main' ]
then
echo "working in 'dashboard-main' enviornment'"
cd dashboards/main/

# Accessing cortx-test repository
if [ -z "$GIT_USER"  ]
then
# open-source cloning
git clone --recursive https://github.com/Seagate/cortx-test.git -b dev
else
# Private repository cloning
git clone --recursive https://"$GIT_USER":"$GIT_PASS"@github.com/Seagate/cortx-test.git -b dev
fi


# updating username and passswords of configs.yml
# <file_path: cortx-test/tools/dash_server/Performance/configs.yml>
python3.7 ../../update_config_yml.py "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

# updating username and passswords of configs.ini
# <file_path: cortx-test/tools/dash_server/config.ini>
python3.7 ../../update_config_ini.py "$CFT_DB_USERNAME" "$CFT_DB_USERPASS" "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

cd cortx-test/tools/dash_server/
sed -i 's/port=5002/port=5012/g' main_app.py
python3.7 main_app.py

elif [ "$session_name" == 'dashboard-prod' ]
then
echo "working in 'dashboard-prod' enviornment'"

cd dashboards/prod/

# Accessing cortx-test repository
if [ -z "$GIT_USER"  ]
then
# open-source cloning
git clone --recursive https://github.com/Seagate/cortx-test.git -b dev
else
# Private repository cloning
git clone --recursive https://"$GIT_USER":"$GIT_PASS"@github.com/Seagate/cortx-test.git -b dev
fi


# updating username and passswords of configs.yml
# <file_path: cortx-test/tools/dash_server/Performance/configs.yml>
python3.7 ../../update_config_yml.py "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

# updating username and passswords of configs.ini
# <file_path: cortx-test/tools/dash_server/config.ini>
python3.7 ../../update_config_ini.py "$CFT_DB_USERNAME" "$CFT_DB_USERPASS" "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

cd cortx-test/tools/dash_server/
sed -i 's/port=5002/port=5022/g' main_app.py
sed -i 's/debug=True/debug=False/g' main_app.py
python3.7 main_app.py
fi
