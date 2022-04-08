"""This Module will update S3 user credentials in client machine"""
import sys
import json

def main(argv):
    access = sys.argv[1] 
    secretkey = sys.argv[2]
    content = "[default]\naws_access_key_id = {}\naws_secret_access_key = {}".format(access,secretkey)
    try:
        with open("/root/.aws/credentials",'w') as f:
            f.write(content)
    except Exception as e:
        print(e)
    

if __name__=="__main__":
	main(sys.argv) 
