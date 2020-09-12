# PerfPro
## Installation


Install required packages in activated virtual environment.
```

pip install PyYAML==5.3.1
pip install requests==2.24.0
pip install jsonschema==3.2.0
pip3 install pymongo==3.11.0

```

## Running Scripts
```
For inserting all s3bench log file data into MongoDb Database

python3 s3bench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting all cosbench csv file data into MongoDb Database

python3 cosbench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting all hsbench json file data into MongoDb Database

python3 hsbench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting Syatem data into MongoDb Database

python3 systemreport.py [timestamp][benchmark][main.yml path]
```
```
For inserting configuration data into MongoDb Database

python3 addconfiguration.py [main.yml path][config.yml path]
```
```
For creating S3 user with predefined credentials
it will create csm admin if not present

python3 main_createusers.py
```
