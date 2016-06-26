#coding:utf8
import requests
import json
import sys

class Zabbix:
    """
    Provide Fuction:
        showGroup : get information of chosen GroupID ;
        showTem: get information of chosen TemplateName ;
        showApp: get information of chosen Application ;
        showHost: get information of chosen HostID ;
        createHost: create host to zabbix_server ;
        deleteHost: delete chosen HostID ;

    """
    def __init__(self):
        self.header = {"Content-Type":"application/json"}
        self.api_url = 'http://192.168.9.30/zabbix/api_jsonrpc.php'
        self.username = 'admin'
        self.passwd = 'zabbix'
        self.hostname = None
        self.ip = None
        self.temid = None
        self.hostid = None
        def auth():
            """
            Return Auth_token
            """
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {"user": self.username, "password": self.passwd},
                "id": 1
                })
            result_dic  = json.loads(requests.post(self.api_url, data=data, headers=self.header).content)
            return result_dic['result']
        self.auth = auth()

    def get_para_dic(self):
        """
        Return: relevant parameter dict ["function.api", "api_paramter"]
        """
        self.para_dic = {
            'deleteHost': ["host.delete", self.hostid],
            'showGroup':["group.get", {"output": ["name", "groupid"]}],
            'showHost': ["host.get", {"output": ["hostid", "host", "name", "available"]}],
            "showApp":["application.get", {"output": "extend","hostids": self.hostid,"sortfield": "name"}],
            'showTem': ["template.get",{"output": "extend", "filter": {"host": ["Template OS Linux", "Template OS Windows"]}}],
            'createHost': ["host.create",{
                "inventory_mode": 0,
                "host": self.hostname,
                "groups": [{"groupid": 2}],
                "templates": [{"templateid": self.temid}],
                "interfaces":[{"ip" : self.ip, "dns" : "","useip": 1, "main" : 1,"type" : 1,"port" : "10050" }],
                 }]
        }
    def action( self, action, hostid=None, hostname=None, ip=None, temid=None):
        """
        Return: All host information
        """
        if action in ["createHost", "showApp", "deleteHost"]:
            if action == "createHost" :
                if not (temid and hostname and ip):
                    print '\033[31m[ERROR]\033[0m : Not only HostID, But also need temId, hostName and hostIp'
                    print "\033[32m[参数]\033[0m : hostname=主机名 , ip=主机IP, temid=模板ID"
                    sys.exit()
                else:
                    self.hostname = hostname
                    self.ip = ip
                    self.temid = temid
            elif not hostid:
                    print "\033[31m[ERROR]\033[0m : Please Input hostID"
                    print "\033[32m[参数]\033[0m : hostid=主机ID"
                    sys.exit()

        self.hostid = hostid if isinstance(hostid, list) else [hostid]
        self.get_para_dic()
        data = json.dumps({
        "jsonrpc": "2.0",
        "method": self.para_dic[action][0],
        "params": self.para_dic[action][1],
        "auth": self.auth,
        "id": 1
        })
        result_dic = json.loads(requests.post(self.api_url, data=data, headers=self.header).content)
        return result_dic['result']

# print z.action("createHost", temid='10001', ip='192.168.1.1', hostname='Xuanxuantest')
#print z.action('deleteHost', hostid=['10108'])
# print z.action('showHost',['10109'])
