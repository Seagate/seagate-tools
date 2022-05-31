from  modules.benchmark.s3bench import S3bench
import common_functions as cf
import sys
import modules.mongodbapi as mapi
import modules.schemas as schemas


class CopyObject(S3bench):

    def __init__(self,overwrite_flag):

        super().__init__(overwrite_flag)

    def insert_s3bench_results(self, log_path):
        files_found, files = cf.get_files_from_directory(log_path, ".s3bench")
        if not files_found:
            raise FileNotFoundError(
                "S3bench report files cannot be located. No records to push in the database.")

        for file in files:
                fname = file.strip(".log")
                ind_list = fname.split("_")
                self.cluster_state = str(ind_list[-9])
            for operation in self.ops_list:
                self.extract_s3bench_results(self, file, operation)
                primary_set = schemas.set_degraded_IO_primary_set(self, operation)

                insertion_set = schemas.set_degarded_IO_insertion_schema(
                    self, primary_set, file)

                self.insert_performance_results(
                    self, self.col["results"], primary_set, insertion_set)


def degraded_IO():
    config = cf.import_perfpro_config()
    dobj = DegradedIO(config["run"]["overwrite"])
    dobj.config = config
    cf.get_build_info(dobj,config)
    cf.get_solution(dobj,config)
    dobj.ops_list = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]

    dobj.db_uri = config["database"]["url"]
    dobj.db_name = config["database"]["name"]

    dobj.insert_s3bench_results(sys.argv[1])


if __name__ == "__main__":
    degraded_IO()

