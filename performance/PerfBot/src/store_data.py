from influxdb import InfluxDBClient
import os
import yaml

cwd = os.getcwd()
input_folder_path = cwd + "/src/Input/"


def connect_database():
    file_name = cwd + "/src/config.yml"
    with open(file_name) as config_file:
        configs = yaml.safe_load(config_file)

        host = configs['database']['host']
        port = configs['database']['port']
        db_name = configs['database']['database']

        client = InfluxDBClient(host=host, port=port, database=db_name)
        return client


if __name__ == '__main__':
    client = connect_database()

    _, _, filenames = next(os.walk(input_folder_path))

    for files in filenames:
        with open(input_folder_path + files) as bench_file:
            bench_data = yaml.safe_load(bench_file)

        client.write_points(bench_data)
