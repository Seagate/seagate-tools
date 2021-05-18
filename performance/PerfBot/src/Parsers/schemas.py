"""
Schemas to store data in influxDB
"""

def get_performance_schema(time_now, run_ID, latency, iops, throughput, timestamp, mode, tool, filename):
    entry = {
        "measurement": "data",
        "time": time_now,
        "fields":
        {
            "timestamp": timestamp,
            "run_ID": run_ID,
            "tool": tool,
            "latency": float(latency),
            "iops": float(iops),
            "throughput": float(throughput),
            "mode": mode,
            "datafile": filename
        }
    }
    return entry

def get_error_schema(time_now, run_ID, tool, line_number, keyword_matched, file_path, error_details):
    entry = {
            "measurement": "logs",
            "time": time_now,
            "fields":
            {
                "run_ID": run_ID,
                "tool": tool,
                "line_in_file": line_number,
                "keyword": keyword_matched,
                "log_file": file_path,
                "details": error_details
            }
        }
    
    return entry
