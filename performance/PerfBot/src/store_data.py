from influxdb import InfluxDBClient
import yaml
import os

input_folder_path =  "./Input/"


def connect_database():
    file_name = "./config.yml"
    with open(file_name, 'r') as config_file:
        configs = yaml.safe_load(config_file)

        host = configs['database']['host']
        port = configs['database']['port']
        db_name = configs['database']['database']

        client = InfluxDBClient(host=host, port=port, database=db_name)
        return client


def update_parsed_data():
    client = connect_database()

    _, _, filenames = next(os.walk(input_folder_path))

    for files in filenames:
        with open(input_folder_path + files, 'r') as bench_file:
            bench_data = yaml.safe_load(bench_file)

        client.write_points(bench_data)
