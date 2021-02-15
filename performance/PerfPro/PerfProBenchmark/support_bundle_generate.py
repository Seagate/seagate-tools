import paramiko
import time
user_name = "root"
passwd = "Seagate!23"
port =  22
node1 = "iu10-r22.pun.seagate.com"
cmd1 =    "cortxcli support_bundle generate build"
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(node1,port, user_name, passwd)
    stdin, stdout, stderr = ssh_client.exec_command(cmd1)
    output = stdout.readlines()
    id =(output[2].strip('|\n').strip('|').strip())
    print("Generating support bundle for bundle id " + id + " in /tmp/support_bundle" )
    print("Wait ... checking the status for bundle id " + id)
    time.sleep(60)
    cmd2 = "cortxcli support_bundle status {}".format(id)
    #print(cmd2)
    stdin, stdout, stderr = ssh_client.exec_command(cmd2)
    output = stdout.readlines()
    print("Printing status for bundle id " + id)
    print(output[5])
except IndexError:
    print("Support bundle is not generated")

