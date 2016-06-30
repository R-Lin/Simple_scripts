import requests
import os
import json
import logging
class Zabbix_wechat:
    """
    Report the Zabbix Warning through Wechat
    """
    def __init__(self):
        self.apiUrl_dic = {
            'token': None,
            'getToken': 'https://qyapi.weixin.qq.com/cgi-bin/gettoken',
            'sendMess': 'https://qyapi.weixin.qq.com/cgi-bin/message/send',
            'corpid': 'wx23ef45bea127db50',
            'secret': 'i_UZ6z9j-JXioCISF9AD928-YVfzfSmMeZL2bgtr701clccJ5oCmB-KKc99IUYfO'
        }

    def getToken(self):
        """
        Get an  auth_token from API or token.txt
        """
        if not os.path.exists('token.txt'):
            with open('token.txt', 'w') as f :
                url = '{0[getToken]}?corpid={0[corpid]}&corpsecret={0[secret]}'.format(self.apiUrl_dic)
                result = json.loads(requests.get(url).content)
                f.write(result['access_token'])
        else :
            self.apiUrl_dic['token'] = open('token.txt').read().strip()
        if self.apiUrl_dic.get('token'):
            print "Authen successfully!"

    def senMessage(self, messages):
        """
        :param messages:
        :return:
        """
        url = '{0[sendMess]}?access_token={0[token]}'.format(self.apiUrl_dic)
        data = json.dumps({
            "safe":"0",
            "agentid": 1,
            "touser": "@all",
            "toparty": "@all",
            "totag": "@all",
            "msgtype": "text",
            "text": {"content": messages}
        })
        result = json.loads(
            requests.post(url, data=data).content
        )
        if result.get('errmsg') == 'ok' :
            print
s = Zabbix_wechat()
s.getToken()
messages = '''
????????Trigger: Free disk space is less than 15% on volume D:

Trigger status: PROBLEM



Free disk space on D: (percentage) (sql_server_106.75.131.45:vfs.fs.size[D:,pfree]): 14.42 %



Original event ID: 3977914
'''
s.senMessage(messages)