import datetime
import socket
import os
import sys

import modules.common_functions as cf
import mongodbapi as mapi
import modules.schemas as schemas

class Hsbench:
    run_state = "successful"

    def __init__(self, overwrite_flag) -> None:
        self.bench = "Hsbench"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.record_overwritten = overwrite_flag
        self.host = socket.gethostname()

#### need to be updated
    def extract_s3bench_results(self, file, expected_op):
        _, self.log_file = os.path.split(file)
        with open(file) as report:
            data_obtained = False
            lines = report.readlines()
            for lindex, line in enumerate(lines):
                if data_obtained:
                    break
                if "label" in line:
                    _temp = line.split("_")
                    self.object_size = _temp[1].upper()
                    self.objects = int(_temp[3])
                    self.buckets = int(_temp[5])
                    self.sessions = int(_temp[7][:-1])
                elif "Operation" in line:
                    operation = cf.get_metric_value(line)
                    if operation.lower() == expected_op.lower():
                        self.operation = operation
                        self.total_ops = int(
                            cf.get_metric_value(lines[lindex+2]))
                        self.total_errors = int(
                            cf.get_metric_value(lines[lindex+3]))
                        self.throughput = round(
                            float(cf.get_metric_value(lines[lindex+4])), 6)
                        self.iops = round(
                            self.throughput/float(self.object_size[:-2]), 6)

                        self.latency = {
                            "Max": round(float(cf.get_metric_value(lines[lindex+7])), 6),
                            "Avg": round(float(cf.get_metric_value(lines[lindex+8])), 6),
                            "Min": round(float(cf.get_metric_value(lines[lindex+9])), 6),
                            "99p": round(float(cf.get_metric_value(lines[lindex+14])), 6)
                        }

                        self.ttfb = {
                            "Max": round(float(cf.get_metric_value(lines[lindex+10])), 6),
                            "Avg": round(float(cf.get_metric_value(lines[lindex+11])), 6),
                            "Min": round(float(cf.get_metric_value(lines[lindex+12])), 6),
                            "99p": round(float(cf.get_metric_value(lines[lindex+16])), 6)
                        }
                    data_obtained = True

    def insert_performance_results(self, collection, primary_set, insertion_set):
        status, docs = mapi.count_documents(
            primary_set, self.db_uri, self.db_name, getattr(self, collection))
        if status and not docs:
            updation_status, result = mapi.add_document(
                insertion_set, self.db_uri, self.db_name, getattr(self, collection))
            if updation_status:
                print("S3bench records are successfully inserted in the Database!")
        elif status:
            updation_status, result = mapi.update_documents(
                primary_set, insertion_set, self.db_uri, self.db_name, getattr(self, collection))
            if updation_status:
                print("S3bench records are successfully updated in the Database!")
        else:
            print(
                f"Status {docs[0]} while counting S3bench Mongo DB record: ", docs[1])

        if not updation_status:
            print(
                f"Status {result[0]} while inserting S3bench Mongo DB record: ", result[1])

    def insert_s3bench_results(self, log_path):
        files_found, files = cf.get_files_from_directory(log_path, ".s3bench")
        if not files_found:
            raise FileNotFoundError(
                "S3bench report files cannot be located. No records to push in the database.")

        for file in files:
            for operation in self.ops_list:
                self.extract_s3bench_results(self, file, operation)
                primary_set = schemas.set_s3bench_primary_set(self, operation)

                insertion_set = schemas.set_s3bench_results_schema(
                    self, primary_set, file)

                self.insert_performance_resuls(
                    self, "results_col", primary_set, insertion_set)


def execute_hsbench():
    sobj = Hsbench(sys.argv[2])

    sobj.db_uri = sobj.perfpro_config["database"]["url"]
    sobj.db_name = sobj.perfpro_config["database"]["name"]

    sobj.insert_s3bench_results(sys.argv[1])
