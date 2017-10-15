import requests
import json
from zabbix_client import ZabbixServerProxy

url = "http://update.winupon.com/zabbix/api_jsonrpc.php"
headers = {"Content-Type": "application/json-rpc"}
#auth: 6c281e2f01a18b6bd19af33a0600043d
def apiinfo():
    data = {
        "jsonrpc": "2.0",
        "method": "apiinfo.version",
        "id": 1,
        "auth": None,
        "params": {}
    }
    r = requests.get(url, headers=headers,data=json.dumps(data))
    print(r.status_code)
    print(r.content)

def login():
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": "shenzm",
            "password": "shenzm"
        },
        "id": 1,
        "auth": None
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))
    print(r.status_code)
    print(r.content)

def get_host():
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host"],
            "selectInterfaces": ['ip'],
        },
        "auth": "6c281e2f01a18b6bd19af33a0600043d",
        "id": 1
    }
    r = requests.get(url, headers=headers,data=json.dumps(data))
    print(r.status_code)
    print(r.content)

if __name__ == '__main__':
    apiinfo()
    #login()
    #get_host()