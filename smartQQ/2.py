import datetime
import time
print int(time.mktime(datetime.datetime.utcnow().timetuple())) * 1000
print int(time.mktime(time.gmtime())* 1000)
try:
    a = {'1':2}
    print a['3']
except KeyError as E :
    print E.message == '3'
