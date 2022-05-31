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
            for operation in self.ops_list:
                self.extract_s3bench_results(self, file, operation)
                primary_set = schemas.set_copy_object_primary_set(self, operation)

                insertion_set = schemas.set_copy_object_insertion_schema(
                    self, primary_set, file)

                self.insert_performance_results(
                    self, self.col["results"], primary_set, insertion_set)
    


def copy_object():
    config = cf.import_perfpro_config()
    #copy_obj = S3bench(config["run"]["overwrite"])
    copy_obj = CopyObject(config["run"]["overwrite"])
    copy_obj.config = config
    cf.get_build_info(copy_obj,config)
    cf.get_solution(copy_obj,config)
    copy_obj.ops_list = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag" , "CopyObject"]
    copy_obj.additional_op = "Copy_op"

    copy_obj.db_uri = config["database"]["url"]
    copy_obj.db_name = config["database"]["name"]

    copy_obj.insert_s3bench_results(sys.argv[1])


if __name__ == "__main__":
    copy_object()

