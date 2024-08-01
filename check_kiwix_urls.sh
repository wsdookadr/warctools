#!/bin/bash
#
# post-processing to assess which pages did not make it into the warc
# 
URL_FILE="$1"
IP=$(ip route get 1 | perl -ne 'm{src (\d+\.\d+\.\d+\.\d+)} && print "$1\n";')
http_status() {
    RAW_URL="$1"
    URL=$(echo "$1" | perl -pne 's{^https?://}{}g;')
    STATUS=$(curl -I -s -o /dev/null -w "%{http_code}"  "http://$IP:8083/content/big/$URL")
    echo -e "$STATUS\t$RAW_URL"
}
export -f http_status
cat "$URL_FILE" | parallel --no-notice --progress -j6 -k http_status "{1}" ::: | awk '$1 != 200 { print $2; }' > not_found_in_kiwix.txt
