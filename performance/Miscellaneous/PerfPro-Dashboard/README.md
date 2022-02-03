1.initialize git (tokens, access)
2. git clone https://github.com/Seagate/cortx-test.git (ssh or http)
3. check if pip3 or pip is there
4. python3 -m pip install -r requirements.txt
https://github.com/Seagate/cortx-test/blob/dev/tools/dash_server/requirements.txt
4. pip3 install --upgrade pip
(check which ones are needed to add in requirements.txt)
5. create tmux session; tmux - dashboard-main and dashboard-prod
7. update config files with username and passwords
https://github.com/Seagate/cortx-test/blob/dev/tools/dash_server/config.ini
https://github.com/Seagate/cortx-test/blob/dev/tools/dash_server/Performance/configs.yml



8. inside tmux-
8.1. main: checkout dev; pull latest code; run on port 5012; debug =True
cd /root/dashboards/prod/cortx-test/tools/dash_server
python3 main_app.py


8.2. prod: checkout dev; [pull code with PR on prod]*; run on port 5022; debug=False
