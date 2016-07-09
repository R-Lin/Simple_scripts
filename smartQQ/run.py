# coding:utf8
import re
import sys
import time
import json
import ini


class SmartQQ():
    """
    A simple robot! For Fun!
    """
    def __init__(self):
        self.qtwebqq = None
        self.clientid = 53999199
        self.psessionid = ''
        self.vfwebqq = None
        self.para_dic = {}
        self.url_request = ini.get_req()
        self.log = ini.log()
        self.url_dic = {
            'qrcode': 'https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4',
            'groupName': 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            'pollMessage': 'http://d1.web2.qq.com/channel/poll2',
            'para': "".join((
                'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq',
                '&appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&',
                'f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001')),
            'check_scan': ''.join((
                'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0[appid]}',
                '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=',
                '2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-0&mibao_css={0[mibao_css]}',
                '&t=undefined&g=1&js_type=0&js_ver={0[js_ver]}&login_sig={0[sign]}&pt_randsalt=0'))}

    def downQrcode(self):
        """
         Download the Qrcode png
        """
        try:
            url = self.url_dic['qrcode'].format(
                self.para_dic['appid']
            )
            with open('qrcode.png', 'wb') as f:
                f.write(self.url_request.get(url, verify=True).content)
                self.log.info('Qrcode file is qrcode.png ! Please scan qrcode immediatety')
        except Exception as messages:
            self.log.error(messages)
            self.log.error('Webbrowser open or down failed! Please retry')
            sys.exit()

    def getPara(self):
        """
        Return a dict that contains appid, sign, js_ver, mibao_cass
        """
        html = self.url_request.get(self.url_dic['para'])
        self.para_dic['appid'] = re.findall(r'<input type="hidden" name="aid" value="(\d+)" />', html.text)[0]
        self.para_dic['sign'] = re.findall(r'g_login_sig=encodeURIComponent\("(.*?)"\)', html.text)[0]
        self.para_dic['js_ver'] = re.findall(r'g_pt_version=encodeURIComponent\("(\d+)"\)', html.text)[0]
        self.para_dic['mibao_css'] = re.findall(r'g_mibao_css=encodeURIComponent\("(.+?)"\)', html.text)[0]

    def checkLogin(self):
        """
        Loop to check the QRcode status
        """
        url = self.url_dic['check_scan'].format(self.para_dic)
        while 1:
            result = eval(self.url_request.get(url, verify=True).text[6:-3])
            self.log.info(result[4])
            if result[0] == '0':
                redirect_url = result[2]
                self.url_request.get(redirect_url)  # visit redirect_url to modify the session cookies
                break
            time.sleep(3)

        self.qtwebqq = self.url_request.cookies['ptwebqq']
        r_data = {
            'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(
                        self.qtwebqq,
                        self.clientid,
                        self.psessionid,
                    )
        }
        self.url_request.headers['Referer'] = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        result = json.loads(self.url_request.post( 'http://d1.web2.qq.com/channel/login2', data=r_data).text)
        self.psessionid = result['result']['psessionid']
        vfwebqq_url = "http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid={1}&psessionid={2}&t={3}".format(
                        self.qtwebqq,
                        self.clientid,
                        self.psessionid,
                        str(int(time.time()*1000))
                    )
        result2 = json.loads(self.url_request.get(vfwebqq_url).text)
        self.vfwebqq = result2['result']['vfwebqq']

    def poll(self):
        """
        Poll the messages
        """
        if not self.vfwebqq or not self.psessionid:
            self.log("Please login")
            self.loggin()
        else:
            data = {'r':json.dumps(
                {"ptwebqq": self.qtwebqq,
                 "clientid": self.clientid,
                 'psessionid': self.psessionid,
                 "key": ""
                 })}
            while 1:
                mess = json.loads(
                    self.url_request.post(self.url_dic['pollMessage'], data=data).text
                )
                print mess
                print mess['result']['values']
                time.sleep(1)
    def login(self):
        self.getPara()
        self.downQrcode()
        self.checkLogin()

a = SmartQQ()
a.login()
a.poll()
