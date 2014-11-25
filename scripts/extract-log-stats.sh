#!/bin/bash

if [[ $# != 4 ]]; then
    echo "usage: $0 ec2_access_key ec2_secret key bucket_name log_file_name"
    exit
fi

export EC2_ACCESS_KEY=$1
export EC2_SECRET_KEY=$2
BUCKET=$3
LOGFILE=$4

DATE=`date -u +"%Y%m%dT%H%M%SZ"`
DATE_SHORT=`date -u +"%Y%m%d"`
HOST=`uname -n`
HITS=`wc -l < $LOGFILE`
PAGE_HITS=`egrep -cv "GET /static" $LOGFILE`
SEARCH_API_HITS=`grep -c "GET /search/results.json" ${LOGFILE}`
START_DATE=`head -1 $LOGFILE | grep -o "\[.*\]"`
END_DATE=`tail -1 $LOGFILE | grep -o "\[.*\]"`
HTTP_404=`grep -c "HTTP/...\" 404 " ${LOGFILE}`
HTTP_500=`grep -c "HTTP/...\" 500 " ${LOGFILE}`
RESULT="$START_DATE,$END_DATE,$PAGE_HITS,$HITS,$SEARCH_API_HITS,$HTTP_404,$HTTP_500,$HOST"
FILE=stats-${DATE_SHORT}-${HOST}.csv
echo $RESULT > $FILE
./aws put $BUCKET/ $FILE
rm $FILE
