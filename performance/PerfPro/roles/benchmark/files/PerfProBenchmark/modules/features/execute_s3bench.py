from  modules.benchmark.s3bench import S3bench
import common_functions as cf
import sys


def execute_s3bench():
    config = cf.import_perfpro_config()
    sobj = S3bench(config["run"]["overwrite"])
    sobj.config = config
    cf.get_build_info(sobj,config)
    cf.get_solution(sobj,config)

    sobj.db_uri = config["database"]["url"]
    sobj.db_name = config["database"]["name"]

    sobj.insert_s3bench_results(sys.argv[1])


if __name__ == "__main__":
    execute_s3bench()
