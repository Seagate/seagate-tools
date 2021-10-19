"""This Module will check the configurations of CSM"""
import sys
import os
#sys.path.append("H:/752260/Documents/CreateUser/")
from csm_rest_s3account import RestS3account
import requests
from subprocess import Popen, PIPE
import yaml
import json

'''
def makeconfig(name):  #function for connecting with configuration file
	with open(name) as config_file:
		configs = yaml.load(config_file, Loader=yaml.FullLoader)
	return configs

conf = makeconfig(sys.argv[1])

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
'''

def s3create():
    try:
        s3user=RestS3account(account_name="perfpro",account_email="perfpro@seagate.com",password="Seagate@1")
        response =s3user.create_s3_account(user_type="newuser")
        #print(response)
        #print(response.text)
        ansible_response = dict()
        ansible_response["status"] = response.status_code
        if response.status_code == 200 or response.status_code == 201:
            ansible_response["access"] = response.json()["access_key"]
            ansible_response["secret"] = response.json()["secret_key"]
        print(json.dumps(ansible_response))
    except Exception as error:
        print("Error occurred during setup : ", error)    
    


def main(argv):
#    print("**************************  CSM Admin Creation  **************************")
#    createcsmadmin()
#    print("\n**************************  S3 User Creation  **************************")
    s3create()
    

if __name__=="__main__":
	main(sys.argv) 
