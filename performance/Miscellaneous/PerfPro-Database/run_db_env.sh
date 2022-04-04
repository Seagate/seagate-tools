#!/bin/bash

# Fetching mongo-version 
mongo_version=$(cat db_info | grep ^mongo_version | awk '{print $3}')

# Copying congiguration file
cp $(pwd)/mongo_release_info /etc/yum.repos.d/mongodb-org-"$mongo_version".repo

# Updating mongo_version info in configuration file
sed -i "s/mongo_version/${mongo_version}/g" /etc/yum.repos.d/mongodb-org-"$mongo_version".repo

# Installing mongodb
yum install -y mongodb-org

# Starting mongo services
systemctl start mongod

# Settting rlimit for mongo
echo "mongod soft nproc 32000" >> /etc/security/limits.d/20-nproc.conf

# Restarting mongo services
systemctl restart mongod

# Fetching DB details
host=$(cat db_info | grep ^host | awk '{print $3}')
port=$(cat db_info | grep ^port | awk '{print $3}')
username=$(cat db_info | grep ^username | awk '{print $3}')
password=$(cat db_info | grep ^password | awk '{print $3}')
path=$(cat db_info | grep ^path | awk '{print $3}')
db_name=$(cat db_info | grep ^db_name | awk '{print $3}')

# Updating create_user.js
prev_user=$(cat create_user.js |grep ^user: | awk '{print$(NF-1)}')
prev_user_pass=$(cat create_user.js |grep ^pwd: | awk '{print$(NF-1)}')
prev_database=$(cat create_user.js |grep db: | awk '{print$(NF-1)}')

sed -i "s/^user: ${prev_user}/user: \"${username}\"/g" create_user.js
sed -i "s/^pwd: ${prev_user_pass}/pwd: \"${password}\"/g" create_user.js
sed -i "s/db: ${prev_database}/db: \"${db_name}\"/g" create_user.js


# Starting mongo shell
mongosh < create_user.js

echo "********************* Setup the Mongo Development Enviornment****************************"
if [ $# -eq 0 ]
then
exit
elif [ "$1" == "dump" ]
then
# Dumping the database
mongodump --host "$host" --username "$username" --password "$password" --port "$port" -d "$db_name" -o "$path"-$(date +%F)

# Restoring the database
mongorestore --host localhost --port "$port" --db "$db_name" --nsExclude "$db_name.*.json" "$path"-"$(date +%F)"/"$db_name"/

echo "****************************Data is Dumped and Restored**********************************"
fi
