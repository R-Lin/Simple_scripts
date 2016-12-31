# coding: utf8
import requests
import re
import os
import time


class WeiboSpider(object):
    def __init__(self):
        self.req = requests.session()
        self.expand_list = ['feed_list_reason']
        self.pattern_expand_compile = {}
        self.pattern_expand = {
            'feed_list_reason': r'.*?feed_list_reason[\\n>"\s]+([^<]+)<',
            'common': r'user_name\\">(.*?)<\\/a.*feed_time[^>]+> ([^<]+)<.*nofollow\\">([^<]+)<.*feed_list_content.*?\\n([^<]+?)<'
        }
        self.cookies = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'SINAGLOBAL=8941961474304.336.1468425131019; wvr=6; YF-Page-G0=e3ff5d70990110a1418af5c145dfe402; SCF=Av0bboGkPJIQlP04diBpYdATRux4ZqjtsBgE8FdiFEwVrXjh9YCW1bDHm-mRsLYPB7Hh_O6pPYhtojrGE2EQISI.; SUB=_2A251Y7RUDeRxGedG7FEY9C7EwjuIHXVWGKKcrDV8PUNbmtBeLWvBkW8MEJ5truSQrwNSbA3qtsXai19lBg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF_k7IEwzXZLX8h6B4Sp22I5JpX5KMhUgL.Fo2RS0e4Sh5R1KM2dJLoIpUki--ciKL8iK.NqJibi--ci-ihi-24P7tt; SUHB=0wnECWt_828SvZ; ALF=1514731395; SSOLoginState=1483195396; _s_tentry=login.sina.com.cn; UOR=www.dilidili.com,widget.weibo.com,login.sina.com.cn; Apache=808014887079.5511.1483195445905; ULV=1483195446339:32:9:7:808014887079.5511.1483195445905:1483161129581; YF-V5-G0=55f24dd64fe9a2e1eff80675fb41718d',
            'Host': 'weibo.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',

        }
        self.req.headers.update(self.cookies)

    def _pattern_init(self):
        # 初始化正则模式编译字典
        for pattern_compile in self.pattern_expand:
            if pattern_compile == 'common':
                self.pattern_expand_compile[pattern_compile] = re.compile(self.pattern_expand[pattern_compile])
            else:
                # 在通用模式上再补充额外正则
                self.pattern_expand_compile[pattern_compile] = re.compile(
                    self.pattern_expand['common'] + self.pattern_expand[pattern_compile]
                )

    def start(self, target_url):
        self._pattern_init()
        result = []
        html_page = self.req.get(target_url).content
        weibo_list = re.findall('(WB_detail.*?)(?:<!)+', html_page)
        for weibo_each in weibo_list:
            flag = 0
            tmp_result = ''
            try:
                for content_flag in self.expand_list:
                    if content_flag in weibo_each:
                        tmp_result = '\t'.join(
                            re.findall(self.pattern_expand_compile[content_flag], weibo_each)[0]
                        ) + '(From Expand %s)\n' % content_flag
                        flag = 1
                        break
                if not flag:
                    tmp_result = '\t'.join(re.findall(self.pattern_expand_compile['common'], weibo_each)[0]) + '\n'
            except IndexError:
                with open(os.path.join('weibo_spider_log','false.log'), 'a') as fw:
                    fw.write(weibo_each + '\n')
            else:
                result.append(re.sub(r'\s{6,}', '  ', tmp_result.replace(r'\\/', '')))
        return result[::-1]

if __name__ == '__main__':
    # 最好就是链接获取: 对方微博-> 主页-> 全部微博
    # Example:
    url_list = [
        'http://weibo.com/u/1831326341?profile_ftype=1&is_all=1#_0',
        'http://weibo.com/u/5708545231?profile_ftype=1&is_all=1#_0'
    ]
    ws = WeiboSpider()
    file_store_dir = 'weibo_spider_log'
    run_log = os.path.join(file_store_dir, 'run.log')
    if not os.path.exists(file_store_dir):
        os.mkdir(file_store_dir)

    for url in url_list:
        result_list = ws.start(url)
        record_list = []
        tmp_name = ''
        if '?' in url:
            tmp_name = re.findall(r'([^/]+)(?=\?)', url)
        filename = os.path.join(file_store_dir, tmp_name[0] + '.txt' if tmp_name else 'weibo_result.txt')
        if os.path.exists(filename):
            # 读取老文件记录
            with open(filename) as f:
                record_list = f.readlines()
            for _ in record_list:
                if _ in result_list:
                    result_list.remove(_)
        result_list = record_list + result_list
        with open(filename, 'w') as f1, open(run_log, 'a') as f2:
            for line in result_list:
                f1.write(line)
            f2.write('%s Result had update on %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename))
        print '%s Result had update on %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename)

