#!/bin/bash
#
# Overview: Receives a file with urls (one per line), preferably the original one fed into Browsertrix as the seedFile.
# Checks if every url in that file is available in the ZIM file.
# This is a form of validation to find which urls did not make it into the ZIM.
# 
# Note: Everything including and following "?" (all url params) are URI-encoded inside the ZIM
# Reference: https://wiki.openzim.org/wiki/ZIM_file_format#Path_Encoding_in_the_ZIM
URL_FILE="$1"
#IP=$(ip route get 1 | perl -ne 'm{src (\d+\.\d+\.\d+\.\d+)} && print "$1\n";')

http_status() {
    RAW_URL="$1"
    URL=$(echo "$1" | perl -MURI::Escape=uri_escape -pne 'chomp; s{^https?://}{}g; if(m{\?}){ ($a,$b)=split(m{\?}); $_="$a%3F".uri_escape($b); };   $_.="\n";')
    STATUS=$(curl -I -s -o /dev/null -w "%{http_code}"  "http://192.168.1.150:8083/content/big/$URL")
    echo -e "$STATUS\t$RAW_URL"
}
export -f http_status
#cat "$URL_FILE" | parallel --no-notice --progress -j6 -k http_status "{1}" ::: # | awk '$1 != 200 { print $2; }' > not_found_in_kiwix.txt
cat "$URL_FILE" | parallel --progress --no-notice -j6 -k http_status "{1}" ::: | awk '$1 != 200 { print $2; }' | tee not_found_in_kiwix.txt
