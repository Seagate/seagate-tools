import os
import sys
import paramiko
import yaml
import re
import subprocess

conf_yaml = open(sys.argv[1])
parse_conf = yaml.load(conf_yaml , Loader=yaml.FullLoader)

nodes=parse_conf.get('NODES')
node1 = nodes[0][1]
passwd=parse_conf.get('CLUSTER_PASS')
PC_full=parse_conf.get('PC_FULL')
endpoints=parse_conf.get('END_POINTS')

prebench=sys.argv[2]


def server(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=node1 ,port='22' , username='root', password=passwd)
    command= cmd
    stdin, stdout, stderr = ssh.exec_command(command)
    out=stdout.readlines()
    resp=''.join(out)
    return (resp)

result = server('hctl status --json')

def read_result(value):
    for line in result.split("\n"):
        if (value in line):
            strip=line.strip()
            strip_r=re.split(': |,',strip)
            return(strip_r[1])

total_disk=int(read_result("fs_total_disk"))
avail_disk=int(read_result("fs_avail_disk"))


print('Total_disk (B):',total_disk ,'\nAvailble_disk (B):', avail_disk)

pre_fill=int(total_disk*PC_full/100)

print('PC_Full % :',PC_full ,'\nPre_Fill data size (B):',pre_fill )

def fill_data(pre_fill):
    obj_size=128
    Pre_fill_mb=int(pre_fill/1048576)
    num_obj=int(Pre_fill_mb/obj_size)
    num_bucket=10
    num_obj_per_bucket=int(num_obj/num_bucket)
    num_clients=200
    print('pre_fill size(MB) :' , Pre_fill_mb , '\nNumber of objects per bucket(10 buckets)(128Mb Object size)', num_obj_per_bucket )
    for i in range(num_bucket):
        subprocess.call([f"/{prebench}", "-ep", f"{str(endpoints)}", "-nc", f"{num_clients}", "-ns", f"{num_obj_per_bucket}", "-s", f"{str(obj_size)+'Mb'}", "-nb", f"{i}"])

def pre_fill_calc():
    if (avail_disk==total_disk):
        PF=pre_fill
        print ('System will be filled with size of data: ', PF)

    elif (avail_disk>=total_disk-pre_fill):
        PF=pre_fill-(total_disk-avail_disk)
        print ('System will be filled with size of data: ', PF)

    elif (avail_disk<total_disk-pre_fill):
        print('Avail disk space on system is less than or equals to required Pre filled data')
        return

    fill_data(PF)

pre_fill_calc()

