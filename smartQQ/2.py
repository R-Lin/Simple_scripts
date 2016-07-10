import datetime
import time
print int(time.mktime(datetime.datetime.utcnow().timetuple())) * 1000
print int(time.mktime(time.gmtime())* 1000)
a = [1,2,3]
print str(a)