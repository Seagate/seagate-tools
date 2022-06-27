#!/bin/bash

# Fetching mongo-version
mongo_version=$(grep ^mongo_version db_info | awk '{print $3}')

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
host=$(grep ^host db_info | awk '{print $3}')
port=$(grep ^port db_info | awk '{print $3}')
username=$(grep ^username db_info | awk '{print $3}')
password=$(grep ^password db_info | awk '{print $3}')
path=$(grep ^path db_info | awk '{print $3}')
db_name=$(grep ^db_name db_info | awk '{print $3}')

# Updating create_user.js
prev_user=$(grep ^user: create_user.js | awk '{print$(NF-1)}')
prev_user_pass=$(grep ^pwd: create_user.js | awk '{print$(NF-1)}')
prev_database=$(grep db: create_user.js | awk '{print$(NF-1)}')

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
