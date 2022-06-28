#!/bin/bash

source dashboards/venv/bin/activate

CFT_DB_USERNAME=$(grep CFT_DB_USER_NAME secret | awk '{print$3}')
CFT_DB_USERPASS=$(grep CFT_DB_USER_PASS secret | awk '{print$3}')

PERF_DB_USERNAME=$(grep PERF_DB_USER_NAME secret | awk '{print$3}')
PERF_DB_USERPASS=$(grep PERF_DB_USER_PASS secret | awk '{print$3}')

GIT_USER=$(grep GIT_USER_NAME secret | awk '{print$3}')
GIT_PASS=$(grep GIT_USER_TOKEN secret | awk '{print$3}')

JIRA_USERNAME=$(grep JIRA_USER_NAME secret | awk '{print$3}')
JIRA_USERPASS=$(grep JIRA_USER_PASS secret | awk '{print$3}')

session_name=$(tmux display-message -p '#S')

if [ "$session_name" == 'dashboard-main' ]
then
echo "working in 'dashboard-main' enviornment'"
cd dashboards/main/

# Accessing seagate-tools repository
if [ -z "$GIT_USER"  ]
then
# Open-Source cloning
git clone --recursive https://github.com/Seagate/seagate-tools.git -b main
else
# Private repository cloning
git clone --recursive https://"$GIT_USER":"$GIT_PASS"@github.com/Seagate/seagate-tools.git -b main
fi


# Updating username and passswords of configs.yml
python3.7 ../../update_config_yml.py "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

# Updating username and passswords of configs.ini
python3.7 ../../update_config_ini.py "$CFT_DB_USERNAME" "$CFT_DB_USERPASS" "$PERF_DB_USERNAME" "$PERF_DB_USERPASS" "$JIRA_USERNAME" "$JIRA_USERPASS"

cd seagate-tools/dashboards/cortx-companion/
sed -i 's/port=5002/port=5012/g' main_app.py
python3.7 main_app.py

elif [ "$session_name" == 'dashboard-prod' ]
then
echo "working in 'dashboard-prod' enviornment'"

cd dashboards/prod/

# Accessing seagate-tools repository
if [ -z "$GIT_USER"  ]
then
# Open-Source cloning
git clone --recursive https://github.com/Seagate/seagate-tools.git -b main
else
# Private repository cloning
git clone --recursive https://"$GIT_USER":"$GIT_PASS"@github.com/Seagate/seagate-tools.git -b main
fi


# Updating username and passswords of configs.yml
python3.7 ../../update_config_yml.py "$PERF_DB_USERNAME" "$PERF_DB_USERPASS"

# Updating username and passswords of configs.ini
python3.7 ../../update_config_ini.py "$CFT_DB_USERNAME" "$CFT_DB_USERPASS" "$PERF_DB_USERNAME" "$PERF_DB_USERPASS" "$JIRA_USERNAME" "$JIRA_USERPASS"

cd seagate-tools/dashboards/cortx-companion/
sed -i 's/port=5002/port=5022/g' main_app.py
sed -i 's/debug=True/debug=False/g' main_app.py
python3.7 main_app.py
fi
