"""This Module will check the configurations of CSM"""
import sys
import os
#sys.path.append("H:/752260/Documents/CreateUser/")
from csm_rest_s3account import RestS3account
import requests
from subprocess import Popen, PIPE
import yaml
import json

def makeconfig(name):  #function for connecting with configuration file
	with open(name) as config_file:
		configs = yaml.load(config_file, Loader=yaml.FullLoader)
	return configs

conf = makeconfig("config.yml")

def createcsmadmin():
    url = 'https://'+conf["MGMT_VIP"]+':28100/api/v1/preboarding/user'
    p = Popen([
    'curl',
    '-k','-X'
    'POST', url,
    '-H','accept: application/json', '-H', 'Content-Type: application/json','-d','{ \"username\": \"admin\", \"password\": \"Seagate@1\",\"email\": \"admin@seagate.com\"}'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    print(output)
    """url = "https://10.237.65.64:28100/api/v1/preboarding/user"
    headers = {"accept": "application/json","Content-Type": "application/json"}
    r = requests.post(url, data={"username": "admin", "password": "Seagate@1"}, headers=headers, verify=False)
    print(r.json())
    #data = r.json()"""

def s3create():
    try:
        s3user=RestS3account(account_name="perfpro",account_email="perfpro@seagate.com",password="Seagate@1")
        #account_name="s3usertest123",account_email="s3usertest123@seagate.com",password="S3usertest@123"
        response =s3user.create_s3_account(user_type="newuser")
        print(response)
        print(response.text)
        #print(dir(response))
        if response.status_code == 200:
            cred = json.loads(response.text)
            access= cred["access_key"]
            secretkey = cred["secret_key"]
            f = open("credentials",'w')
            str1 = "aws_access_key_id = {}\naws_secret_access_key = {}".format(access,secretkey)
            f.write(str1)
            f.close()
            #access_key  secret_key
        
    except Exception as error:
        # CTP Exception handling not done here as this is being called in setup for every test suit
        # CTP Exception handling shall get complicated
        print("Error occurred during setup : ", error)    
    


def main(argv):
    print("**************************  CSM Admin Creation  **************************")
    createcsmadmin()
    print("\n**************************  s3 User Creation  **************************")
    s3create()
    

if __name__=="__main__":
	main(sys.argv) 
