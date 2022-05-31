"""Performance Sanity using PerfPro

This file includes Sanity Class for performing Perf-Sanity Operations.

System Arguments:
1. log file path (string) - Path to benchmark results directory of S3bench report
2. Repository (string/ dictionary) - dictionary of sanity build GitHub Repository details
3. PR ID (string) - GitHub Pull Request ID
4. User (string) - Username on whose PR sanity is triggered upon
5. GID (string) - GID of the User

Command: python3 sanity.py <log_path> <repository> <pr_id> <user> <gid>
"""

#!/usr/bin/env python3

from modules.benchmark.s3bench import S3bench
import modules.schemas as schemas
import modules.common_functions as cf
import modules.mongodbapi as mapi

import sys
import ast

perfpro_config_path = "./perfpro_config.yml"


class Sanity(S3bench):
    def __init__(self, overwrite_flag) -> None:
        super().__init__(overwrite_flag)

    def insert_sanity_run_details(self, repo_details, pr_id):
        rd_schema = schemas.get_sanity_details_schema()
        rd_schema["other_repos"] = list(repo_details)
        rd_schema["PR_ID"] = pr_id
        for repo in list(repo_details):
            if repo["category"].lower() == "motr":
                key = "motr_repository"
            elif repo["category"].lower() == "rgw":
                key = "rgw_repository"
            elif repo["category"].lower() == "hare":
                key = "hare_repository"
            else:
                continue

            rd_schema[key] = repo["repo"]

        cf.update_or_insert_document(rd_schema, rd_schema, "run_details_col", "run_id")

    def insert_sanity_config(self, username, gid):
        sc_schema = schemas.get_sanity_config_schema()
        sc_schema["User"] = username
        sc_schema["GID"] = gid
        sc_schema["run_ID"] = self.run_id
        sc_schema["Nodes"] = self.perfpro_config["cluster"]["nodes"]
        sc_schema["Nodes_Count"] = len(sc_schema["Nodes"])
        sc_schema["Clients"] = self.perfpro_config["cluster"]["clients"]
        sc_schema["Clients_Count"] = len(sc_schema["Clients"])
        sc_schema["Cluster_Fill"] = self.perfpro_config["cluster"]["fill_percent"]

        cf.update_or_insert_document(sc_schema, sc_schema, "config_col", "config_id")

    def insert_sanity_results(self, log_path):
        files_found, files = cf.get_files_from_directory(log_path, ".s3bench")
        if not files_found:
            raise FileNotFoundError(
                "S3bench report files cannot be located. No records to push in the database.")

        for file in files:
            for operation in self.ops_list:
                self.extract_s3bench_results(self, file, operation)
                primary_set = schemas.set_sanity_primary_set(self, operation)

                insertion_set = schemas.set_sanity_results_schema(
                    self, primary_set, file)

                self.insert_performance_results(
                    self, "results_col", primary_set, insertion_set)


def sanity_main():
    sobj = Sanity(True)
    sobj.ops_list = ["Write", "Read"]

    sobj.perfpro_config = cf.import_perfpro_config()

    sobj.db_uri = sobj.perfpro_config["sanity"]["database"]["url"]
    sobj.db_name = sobj.perfpro_config["sanity"]["database"]["name"]
    sobj.results_col = sobj.perfpro_config["sanity"]["database"]["collections"]["results"]
    sobj.config_col = sobj.perfpro_config["sanity"]["database"]["collections"]["config"]
    sobj.run_details_col = sobj.perfpro_config["sanity"]["database"]["collections"]["run_details"]

    sobj.insert_sanity_run_details(
        sys, list(ast.literal_eval(sys.argv[2])), sys.argv[3])
    sobj.insert_sanity_config(sys.argv[4], sys.argv[5])

    sobj.insert_sanity_results(sys.argv[1])
