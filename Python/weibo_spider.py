# coding: utf8
import requests
import re
import os
import time


class WeiboSpider(object):
    def __init__(self, result_reverse=True):
        self.reverse = result_reverse
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
            'Connection': 'keep-alive',
            'Host': 'weibo.com',
            'Referer': 'http://weibo.com/wu2198?refer_flag=0000015010_&from=feed&loc=nickname&is_all=1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            'Cookie': 'SINAGLOBAL=8941961474304.336.1468425131019; wvr=6; YF-V5-G0=2da76c0c227d473404dd0efbaccd41ac; '
                      'SCF=Av0bboGkPJIQlP04diBpYdATRux4ZqjtsBgE8FdiFEwVgW3vAGH6e2s90zIRtWW5n4W6nfcKRwI_dr336Lbz8jY.; '
                      'SUB=_2A251YhSqDeRxGedG7FEY9C7EwjuIHXVWFgFirDV8PUNbmtBeLVPakW8cp40bbBwMZhs1woZPcoZS8ZJ_7g..; '
                      'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF_k7IEwzXZLX8h6B4Sp22I5JpX5KMhUgL.Fo2RS0e4Sh5R1KM2dJLoIpUki--ciKL8iK.NqJibi--ci-ihi-24P7tt;'
                      ' SUHB=05iLV9y7I4PP5V; ALF=1514641528; SSOLoginState=1483105530; YF-Page-G0=f27a36a453e657c2f4af998bd4de9419;'
                      ' _s_tentry=login.sina.com.cn; UOR=www.dilidili.com,widget.weibo.com,login.sina.com.cn;'
                      ' Apache=4540898540504.192.1483105611969; ULV=1483105612430:29:6:4:4540898540504.192.1483105611969:1483018706967'

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
                result.append(re.sub(r'\s{4,}', '', tmp_result.replace(r'\\/', '')))
        if not self.reverse:
            return result
        return result[::-1]

if __name__ == '__main__':
    # 最好就是链接获取: 对方微博-> 主页-> 全部微博
    # Example:
    url_list = [
        'http://weibo.com/u/1831326341?profile_ftype=1&is_all=1#_0',
        'http://weibo.com/u/5371503934?profile_ftype=1&is_all=1#_0'
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

        result_list += record_list
        uniq_result_list = set(result_list)
        with open(filename, 'w') as f1, open(run_log, 'a') as f2:
            for line in result_list:
                if line in uniq_result_list:
                    f1.write(line)
                    uniq_result_list.remove(line)
            f2.write('%s Result had update on %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename))
        print '%s Result had update on %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), filename)

