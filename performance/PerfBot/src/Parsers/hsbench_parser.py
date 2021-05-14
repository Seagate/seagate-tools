import json
import os
import re


def extract_HSBench_logs(reference_doc, HS_destination_file_path):
    with open(HS_destination_file_path, "w") as modified:
        with open(reference_doc, 'r') as reference_file:

            for line in reference_file:
                if 'Loop:' in line or 'Mode:' in line:
                    modified.write(line)


def convert_HSlogs_to_JSON(ID, reference_doc, HS_input_file_path):
    data = []
    with open(reference_doc, 'r') as reference_file:
        for line in reference_file:
            not_needed_chars = ('', '-', '[', ']', ',')
            stripped_data = re.split(" |,", line)
            for element in stripped_data:
                if element in not_needed_chars:
                    stripped_data.remove(element)

            entry = {
                "measurement": ID+"_hsbench",
                "time": stripped_data[0]+" "+stripped_data[1],
                "fields":
                {
                    "latency": float(stripped_data[20]),
                    "iops": float(stripped_data[15]),
                    "throughput": float(stripped_data[13]),
                    "mode": stripped_data[9]
                }
            }
            data.append(entry)

    with open(HS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)

    os.remove(reference_doc)
