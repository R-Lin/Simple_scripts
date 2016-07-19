# coding:ISO-8859-1
import requests
import pyquery

url = 'http://www.szyangxiao.net/6554.shtml'
h = requests.get(url)
print h.content.decode('gbk').encode('utf8')
print h.encoding

