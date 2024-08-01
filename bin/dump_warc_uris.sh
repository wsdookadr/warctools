#!/bin/bash

stty -onlcr
WARC="warc/big.warc"
distinct() {
    awk 'seen[$_] != 1 {print; seen[$_]=1; }'
}

source ~/v_warcio/bin/activate
~/v_warcio/bin/warcio index -f warc-target-uri,http:content-type,http:content-length,http:status $WARC | \
jq -r -c '
.
| select(( ."http:status" != null) and ((."http:status" | tonumber) == 200))
| ."warc-target-uri"
' | \
grep -v "^jq: " | \
distinct | perl -pne 's{\r\n}{}g; s{\n}{}g; $_.="\n";' 

