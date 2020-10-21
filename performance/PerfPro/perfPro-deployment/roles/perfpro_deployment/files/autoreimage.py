import requests
import time
import os
import argparse
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# inputs
parser = argparse.ArgumentParser(description='Pre Test Setup configuration.')
parser.add_argument('-p', '--primary_hostname', help='Primary Host', required=True)
parser.add_argument('-s', '--secondary_hostname', help='Secondary Host', required=False)
parser.add_argument('-un', '--username', help='User Name', required=True)
parser.add_argument('-pw', '--password', help='Password', required=True)

args = parser.parse_args()
print('* Passed following args')
print('\tprimary_hostname:{0}'.format(args.primary_hostname))
primary_host = args.primary_hostname       # 'sm7-r18.pun.seagate.com'
hosts = [primary_host]
if args.secondary_hostname:
    print('\tsecondary_hostname:{0}'.format(args.secondary_hostname))
    secondary_host = args.secondary_hostname   # 'sm8-r18.pun.seagate.com'
    hosts.append(secondary_host)

username = args.username
password = args.password

hostname = 'https://ssc-satellite1.colo.seagate.com/'
api_ver = 'api/v2/'
endpoint_host = hostname + api_ver + 'hosts/'


"""
From https://seagatetechnology.sharepoint.com/sites/EOS.Lab/SitePages/Satellite-API-Rebuild-Bare-Metal-Host.aspx

1 . Mark host for rebuild (Notice you call the specific hostname that you want to rebuild) This should return "true"
curl --user 509589 -k -H "Content-Type:application/json" -H "Accept:application/json" -X PUT -d '{"host":{"build": "true"}}' https://ssc-satellite1.colo.seagate.com/api/v2/hosts/smc-test-14-m11.colo.seagate.com | jq -r '.build'

2 . Reboot Host (Notice you call the specific host plus /power at the end of the URL) This should return "power": true
Note: User is the service account username/GID. GID is applicable only for the Lab team members.
curl --user 509589 -k -H "Content-Type:application/json" -H "Accept:application/json" -X PUT -d '{"power_action": "reset"}' https://ssc-satellite1.colo.seagate.com/api/v2/hosts/smc14-test-m11.colo.seagate.com/power | jq

3. Check the status of the build. (Same as first command but without the PUT). This will return "true" if the server is 
actively being imaged, and "false" if the server is done imaging.
Note: There is a delay from when the server is done being imaged and accessible from SSH. This is because the server is 
booting for the first time.
curl --user 509589 -k -H "Content-Type:application/json" -H "Accept:application/json" https://ssc-satellite1.colo.seagate.com/api/v2/hosts/smc15-m11.colo.seagate.com | jq -r '.build'
"""


def check_ping(node):
    host_up = True if os.system("ping -c 1 " + node) == 0 else False
    if host_up:
        return True
    else:
        return False


def send_build_request(node):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = '{"host":{"build": "true"}}'
    response = requests.put(endpoint_host + node, headers=headers, data=data, verify=False, auth=(username, password))
    if response.status_code == requests.codes.ok:
        if response.json()['build']:
            print('Build host request on {0} successfully completed'.format(node))
        else:
            print('Build host {0} received build False. Expected to receive True'.format(node))
            print('Will not proceed further')
            exit(0)
    else:
        print('Build request for {0} host failed with status code {1}, expected 200'.format(node, response.status_code))
        print('Will not proceed further')
        print('Request Body:', response.request.body)
        print('Request Headers:', response.request.headers)
        print('Response:', response.json())
        exit(1)


def reboot_host(node):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = '{"power_action": "reset"}'
    response = requests.put(endpoint_host + node + '/power', headers=headers,
                            data=data, verify=False, auth=(username, password))
    if response.status_code == requests.codes.ok:
        if response.json()['power']:
            print('Reboot host {0} response is success'.format(node))
        else:
            print('Reboot host {0} received power False. Expected to receive True'.format(node))
            print('Will not proceed further')
            exit(0)
    else:
        print('Reboot request for {0} host failed with status code {1}'.format(node, response.status_code))
        print('Request Body:', response.request.body)
        print('Request Headers:', response.request.headers)
        print('Response:', response.json())
        exit(1)


def check_build_status(node):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.get(endpoint_host + node, headers=headers, verify=False, auth=(username, password))
    if response.status_code == requests.codes.ok:
        return response.json()['build']
    else:
        print('Check build status request for {0} host failed with status code {1}'.format(node, response.status_code))
        print('Request Body:', response.request.body)
        print('Request Headers:', response.request.headers)
        print('Response:', response.json())
        exit(1)


def check_reimage_status(node):
    if check_build_status(node):
        print('Reimage is already in progress on node {0}'.format(node))
        print('Please wait for it to complete or cancel this from https://ssc-satellite1.colo.seagate.com/hosts/{0}'.format(node))
        print('Then restart this script')
        exit(1)


if __name__ == "__main__":

    print('* Checking if hostname is reachable')
    for host in hosts:
        if not check_ping(host):
            print("Unable to connect to {0}".format(host))
            #exit(1)

    # Check previous reimage status before starting new reimage
    print('* Checking if reimage already in progress')
    for host in hosts:
        check_reimage_status(host)

    # send build request for both nodes
    print('* Sending reimage request to both the nodes')
    for host in hosts:
        send_build_request(host)

    # send power cycle for both nodes
    print('* Power cycling both the nodes')
    for host in hosts:
        reboot_host(host)

    print('* Polling for reimge completion')
    # 3. for 60 minutes for each 5 minutes
    #     send check build status
    #     if response build is true:
    #         continue
    #     else if response build is false:
    #         reimage complete
    reimg_in_progress0 = True
    reimg_in_progress1 = True
    # For 60 minutes
    t_end = time.time() + 60 * 60
    while time.time() < t_end:
        # Check every 3 minutes
        time.sleep(180)

        if reimg_in_progress0:
            reimg_in_progress0 = check_build_status(hosts[0])
            if reimg_in_progress0:
                print('Host {0} is still being reimaged'.format(hosts[0]))
            else:
                print('Host {0} reimage complete'.format(hosts[0]))

        if len(hosts) == 2 and reimg_in_progress1:
            reimg_in_progress1 = check_build_status(hosts[1])
            if reimg_in_progress1:
                print('Host {0} is still being reimaged'.format(hosts[1]))
            else:
                print('Host {0} reimage complete'.format(hosts[1]))

        if ((len(hosts) == 1) and (not reimg_in_progress0)) or \
           ((len(hosts) == 2) and (not reimg_in_progress0) and (not reimg_in_progress1)):
            # wait for 15 minutes to let server reboot
            print('Checking if host is reachable by ping')
            ping0 = False
            ping1 = False
            t_end = time.time() + 60 * 15
            while time.time() < t_end:
                # try pinging both the setups for 10 minutes, 1 minute interval
                time.sleep(60)
                ping0 = check_ping(hosts[0])
                if len(hosts) == 2:
                    ping1 = check_ping(hosts[1])
                if (len(hosts) == 1) and ping0:
                    print('host {0} is reachable by ping'.format(hosts[0]))
                    exit(0)
                    break
                elif (len(hosts) == 2) and ping0 and ping1:
                    print('Hosts {0} & {1} are reachable by ping'.format(hosts[0], hosts[1]))
                    exit(0)
                    break
            if (not ping0) and (not ping1):
                print('Unable to ping both nodes after reimage.')
                print('Please check status manually from BMC IP.')
                exit(1)
            elif not ping0:
                print('Unable to ping node {0} after reimage.'.format(hosts[0]))
                print('Please check status manually from BMC IP.')
                exit(1)
            elif not ping1:
                print('Unable to ping node {0} after reimage.'.format(hosts[1]))
                print('Please check status manually from BMC IP.')
                exit(1)
            break

    if reimg_in_progress0 and reimg_in_progress1:
        print("Reimage is not complete within 60 minutes for both of the nodes. Please check status manually")
        exit(1)
    elif reimg_in_progress0:
        print("Reimage is not complete within 60 minutes for {0} nodes. Please check status manually.".format(hosts[0]))
        exit(1)
    elif reimg_in_progress1:
        print("Reimage is not complete within 60 minutes for {0} nodes. Please check status manually.".format(hosts[1]))
        exit(1)
