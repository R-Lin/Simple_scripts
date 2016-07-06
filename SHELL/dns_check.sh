#!/bin/bash
TIMEOUT=3
DOMAIN='dns.test.ycf.com'
nslookup ${DOMAIN} -timeout=${TIMEOUT} &> /dev/null
[ $? -eq 0 ] && echo 0 || echo 1
