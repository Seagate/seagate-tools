GIT_USER=`cat secret | grep GIT_USER_NAME | awk '{print$3}'`
GIT_PASS=`cat secret | grep GIT_USER_PASS | awk '{print$3}'`
session_name=`tmux display-message -p '#S'`
echo "$session_name"
if [ $session_name == 'dashboard-main' ]
then
echo "working in 'dashboard-main' enviornment'"
cd main/
git clone --recursive https://$GIT_USER:$GIT_PASS@github.com/Seagate/cortx-test.git -b dev
cd cortx-test/tools/dash_server/
sed -i 's/port=5002/port=5012/g' main_app.py
python3 main_app.py
elif [ $session_name == 'dashboard-prod' ]
then
echo "working in 'dashboard-prod' enviornment'"
cd prod/
git clone --recursive https://$GIT_USER:$GIT_PASS@github.com/Seagate/cortx-test.git -b dev
cd cortx-test/tools/dash_server/
sed -i 's/port=5002/port=5022/g' main_app.py
sed -i 's/debug=True/debug=False/g' main_app.py
python3 main_app.py
fi
