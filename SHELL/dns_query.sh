#!/bin/bash
RNDC_FILE='/var/named/chroot/var/logs/named_stats.txt'
RNDC_FILE_BK='/var/named/chroot/var/logs/named_stats.txt.bk'
[ -e ${RNDC_FILE} ] && cat  ${RNDC_FILE}  >> ${RNDC_FILE_BK}

OLD_RESULT=`grep -oP '\d+(?= QUERY)' ${RNDC_FILE}`
> ${RNDC_FILE}
rndc stats
NEW_RESULT=`grep -oP '\d+(?= QUERY)' ${RNDC_FILE}`
RESULT=$((${NEW_RESULT} - ${OLD_RESULT}))
echo ${RESULT}


