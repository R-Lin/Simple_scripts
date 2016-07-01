#!/bin/bash
TIMEOUT=3
DOMAIN='dns.test.ycf.com'

RESULT=`nslookup ${DOMAIN} -timeout=${TIMEOUT}`
RETURN_CODE=$?
if [ ${RETURN_CODE} -eq 0 ]
then
	# awk 如果gsub替换成功,返回值为替换次数
	# result不为0, 代表有预期的结果,解析正确
	awk -vdomain=${DOMAIN} '{
		result=gsub("111.111.111.111","")
		print result==0?1:0
	}' <<<${RESULT}
	
else :
	echo 1
	
fi
