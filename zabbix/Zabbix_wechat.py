#!/usr/bin/env python
#coding:utf8
import time
import requests
import os
import json
import sys
import logging


class Mylog:
    def __init__(self, log_path):
        self.logger = logging.getLogger('Mylogger')
        self.logger.setLevel(logging.INFO)
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(log_path)
        stream = logging.StreamHandler()

        # define log level
        fh.setLevel(logging.INFO)
        stream.setLevel(logging.DEBUG)

        # define log format
        fh.setFormatter(log_format)
        stream.setFormatter(log_format)
        self.logger.addHandler(fh)
        self.logger.addHandler(stream)

    def log(self):
        return self.logger


class ZabbixWechat:
    """
    Report the Zabbix Warning through Wechat
    """
    def __init__(self):
        self.token_file = 'token.txt'
        self.log_file = 'Zabbix_wechat.log'
        self.logger = Mylog(self.log_file).log()
        self.apiUrl_dic = {
            'token': None,
            'get_token': 'https://qyapi.weixin.qq.com/cgi-bin/get_token',
            'sendMess': 'https://qyapi.weixin.qq.com/cgi-bin/message/send',
            'getDepartment': 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=%s',
            'corpid': 'wx23ef45bea127db50',
            'secret': 'i_UZ6z9j-JXioCISF9AD928-YVfzfSmMeZL2bgtr701clccJ5oCmB-KKc99IUYfO'
        }

    def get_token(self):
        """
        Get an  auth_token from API or token.txt
        """
        control = False
        if os.path.exists(self.token_file):
            now_time = time.time()
            token_stat = os.stat(self.token_file)
            token_interval = now_time - token_stat.st_mtime
            if token_stat.st_size and 0 < token_interval < 7200:    # 判断token 是否超过2小时有效期
                self.apiUrl_dic['token'] = open(self.token_file).read().strip()
                self.logger.info("Token_file exist, now use token of Token_file")
                control = True

        if not control:
            with open(self.token_file, 'w') as f:
                url = '{0[get_token]}?corpid={0[corpid]}&corpsecret={0[secret]}'.format(self.apiUrl_dic)
                result = json.loads(requests.get(url).content)
                f.write(result['access_token'])
                self.apiUrl_dic['token'] = result['access_token']
                self.logger.info("Token_file not exist or timed out, now use token from Wechat_Api")

    def get_department(self):
        api_url = self.apiUrl_dic['getDepartment'] % self.apiUrl_dic['token']
        print requests.get(api_url).text

    def sen_message(self, messages1):
        url = '{0[sendMess]}?access_token={0[token]}'.format(self.apiUrl_dic)
        data = json.dumps({
            "safe":"0",
            "agentid": 1,
            "toparty": "3",
            "msgtype": "text",
            "text": {"content": messages1}
        })
        result = json.loads(
            requests.post(url, data=data).content
        )

        if result.get('errmsg') == 'ok':
            self.logger.info("Send ok!")
        else:
            self.logger.error("Send Error")
            self.logger.error(result.get('errmsg'))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit(3)

    messages = sys.argv[1]
    s = ZabbixWechat()
    s.get_token()

