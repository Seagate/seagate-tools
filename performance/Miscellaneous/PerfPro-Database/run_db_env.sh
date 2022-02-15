# fetching mongo-version 
mongo_version=$(cat db_info | grep ^mongo_version | awk '{print $3}')

# copying congiguration file
cp $(pwd)/mongo_release_info /etc/yum.repos.d/mongodb-org-$mongo_version.repo

# updating mongo_version info in configuration file
sed -i "s/mongo_version/$mongo_version/g" /etc/yum.repos.d/mongodb-org-$mongo_version.repo

# installing mongodb
yum install -y mongodb-org

# starting mongo services
systemctl start mongod

# settting rlimit for mongo
echo "mongod soft nproc 32000" >> /etc/security/limits.d/20-nproc.conf

# restarting mongo services
systemctl restart mongod

# starting mongo shell
mongosh < create_user.js

# fetching DB details
host=$(cat db_info | grep ^host | awk '{print $3}') 
port=$(cat db_info | grep ^port | awk '{print $3}')
username=$(cat db_info | grep ^username | awk '{print $3}')
password=$(cat db_info | grep ^password | awk '{print $3}')
path=$(cat db_info | grep ^path | awk '{print $3}')
db_name=$(cat db_info | grep ^db_name | awk '{print $3}')

# Dumping the database
#mongodump --host $host --username $username --password $password --port $port -d $db_name -o $path-$(date +%F)

# restoring the database
mongorestore --host localhost --port $port --db $db_name --nsExclude "$db_name.*.json" $path-$(date +%F)/$db_name/
