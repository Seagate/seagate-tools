import paramiko
import time
import os
import yaml
user_name = "root"
port =  22
nfs_mount_point = "/mnt/support_bundle/"
nfs_loc = "/mnt/support_bundle/PerfPro/support_bundle/"
support_bundle_loc = "/var/log/seagate/support_bundle/"

from datetime import datetime as DT
now=DT.now()
time_string = now.strftime("%m-%d-%Y-%H:%M:%S")

###Reading conf file######
conf_yaml = open('/root/PerfProBenchmark/config.yml')
parse_conf = yaml.load(conf_yaml , Loader=yaml.FullLoader)
node1 = parse_conf.get('NODE1')
node2 = parse_conf.get('NODE2')
nfs_server=parse_conf.get('NFS_SERVER')
nfs_export=parse_conf.get('NFS_EXPORT')
build = parse_conf.get('BUILD')
passwd = parse_conf.get('CLUSTER_PASS')

########################################Node1################################

try:

#######################################Generate support bundle###############
    cmd1 = "mkdir {}; mount {}:{} {}; cortxcli support_bundle generate {}; mkdir -p {}".format(nfs_mount_point,nfs_server,nfs_export,nfs_mount_point,build,nfs_loc)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(node1, port, user_name, passwd)
    stdin, stdout, stderr = ssh_client.exec_command(cmd1)
    output1 = stdout.readlines()
    id = (output1[2].strip('|\n').strip('|').strip())

    print("Generating link for support bundle for bundle id " + id + " in /tmp/support_bundle")
    
    remotefilepath1 = "{}{}_{}.tar.gz".format(support_bundle_loc,id,node1)
    remotefilepath2 = "{}{}_{}.tar.gz".format(support_bundle_loc,id,node2)


### Code for checking tar.gz file  in /var/log/seagate/support_bundle/  #########

    timeout = 3600
    endtime = time.time() + timeout
    ftp_client=ssh_client.open_sftp()
    while time.time() <= endtime:
        try:
            ftp_client.stat(remotefilepath1)
            print("Generated support bundlle {}_{}.tar.gz".format(id,node1))
            print("Generated support bundlle {}_{}.tar.gz".format(id,node2))
            break
        except Exception:
            print("Waiting for sometime as support bundle is being generated for bundle id {}".format(id))
            time.sleep(60)
    ftp_client.close()

    print("Copying support bundle for {} at NFS location".format(id))
    
    cmd2= "mkdir {}{}_{};cp {} {}{}_{}".format(nfs_loc,node1,time_string,remotefilepath1,nfs_loc,node1,time_string)
    stdin, stdout, stderr = ssh_client.exec_command(cmd2)
    output2 = stdout.readlines()

####################################### For Node2#####################################

    ssh_client1 = paramiko.SSHClient()
    ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client1.connect(node2,port, user_name, passwd)

    cmd3 = "mkdir {};mount {}:{} {}".format(nfs_mount_point,nfs_server,nfs_export,nfs_mount_point)
    cmd4= "mkdir {}{}_{};cp {} {}{}_{}".format(nfs_loc,node2,time_string,remotefilepath2,nfs_loc,node2,time_string)

    stdin, stdout, stderr = ssh_client1.exec_command(cmd3)
    output3 = stdout.readlines()
    stdin, stdout, stderr = ssh_client1.exec_command(cmd4)
    output4 = stdout.readlines()
    time.sleep(120)

#######################################Printing message for copying##################

    print('copied support bundle using ' + str(build) + ' for ' + node1 + ' in /PerfPro/support_bundle folder at NFS location')
    print('copied support bundle using ' + str(build) + ' for ' + node2 + ' in /PerfPro/support_bundle folder at NFS location')

### Code for checking status for support bundle id######
    print("Checking status for support bundle " + id)
    cmd11 = "cortxcli support_bundle status {}".format(id)
    stdin, stdout, stderr = ssh_client.exec_command(cmd11)
    output11 = stdout.readlines()
    print("Printing status for bundle id " + id)
    for op in output11:
        print(op)
except paramiko.AuthenticationException:
    print("Please check password")
except IndexError:
    print("Support bundle status is not generated yet")
