# python3 makeReport.py <logs location> eg. [python makeReport.py benchmark.log]
# Import third-party modules
import socket
import sys
from datetime import datetime
import csv
import os

csvFileName = 'S3benchCSVReport.csv'

# Function to iterate through all files in specified location
# Input - 'filepath'(string) , 'extension'(String)
# Returns - 'list of files'(list)
def getallfiles(directory,extension):#function to return all file names with perticular extension
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist

# Function to write in report
# Input - 'all useful files' location'(list), 'hostname'(string)
# Returns - none
def writeCSV(fileLocation,host):
    oplist = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]
    Objsize= 1
    obj = "NA"
    with open(csvFileName, 'w', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['Bench','Operation','ObjectSize','HOST','Throughput','IOPS','MaxLatency','AvgLatency','MinLatency','MaxTTFB','AvgTTFB','MinTTFB','Timestamp','Log_File'])
        for file in fileLocation:
            f = open(file)
            _, filename = os.path.split(file)
            linecount = len(f.readlines())
            if linecount < 151:
                lines = f.readlines()
                max_lines = linecount
            else:
                lines = f.readlines()[-150:]
                max_lines = 150
            count=0
            while count<max_lines:
                if "objectSize (MB):" in lines[count].strip().replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    Objsize = float(r[1])
                    if(Objsize.is_integer()):
                        obj=str(int(Objsize))+"Mb"
                    else:
                        obj=str(round(Objsize*1024))+"Kb"

                if "Operation:" in lines[count].replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    opname = r[1]
                    if opname in oplist:
                        count-=1
                        throughput="NA"
                        iops="NA"
                        if opname=="Write" or opname=="Read":
                            count+=1
                            throughput = float(lines[count+3].split(":")[1])
                            iops=round((throughput/Objsize),6)
                            throughput = round(throughput,6)
                        lat={"Max":float(lines[count+4].split(":")[1]),"Avg":float(lines[count+5].split(":")[1]),"Min":float(lines[count+6].split(":")[1])}
                        ttfb={"Max":float(lines[count+7].split(":")[1]),"Avg":float(lines[count+8].split(":")[1]),"Min":float(lines[count+9].split(":")[1])}
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        wr.writerow(['S3bench',opname,obj,host,throughput,iops,lat['Max'],lat['Avg'],lat['Min'],ttfb['Max'],ttfb['Avg'],ttfb['Min'],timestamp,filename]) # writes in csv
                        count += 9
                count +=1

        myfile.close()

# Main function to trigger reports and send parameters
# Input - 'directory of logs'(string)
if __name__ == "__main__":
    location = sys.argv[1] 
    host = socket.gethostname()
    flist = getallfiles(location,'log')
    writeCSV(flist,host)

# End