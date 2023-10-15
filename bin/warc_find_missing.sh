#!/bin/bash

WARC="warc/big.warc"

distinct() {
    awk 'seen[$_] != 1 {print; seen[$_]=1; }'
}

filter_uri() {
    awk 'length < 512 && /^http/ { print; }'
}

# grab all images stored in the WARC
env VIRTUAL_ENV=v_warcio ./v_warcio/bin/python warcio index -f warc-target-uri,http:content-type,http:content-length,http:status $WARC | \
jq -r -c '
    . 
    | select(
        (
          (."warc-target-uri"   | test("\\.(png|jpeg|jpg|bmp|gif|svg)$")) or 
          (."http:content-type" != null and (."http:content-type" | test("(png|jpeg|jpg|bmp|gif|svg)$")))
        ) and
        ( ( ."http:status" != null) and (."http:status" | tonumber) == 200) and
        ( ( ."http:content-length" != null) and (."http:content-length" | tonumber) > 5)
      )
    | ."warc-target-uri"
' | \
distinct | filter_uri | sort > res_available.txt

# grab all images refered to by the WARC
./bin/warc_resources.py --imgs --infile $WARC | \
distinct | filter_uri | sort > res_referenced.txt

# get referenced resources that are not available in the WARC
comm -1 -3 res_available.txt res_referenced.txt

# TODO: use bin/warc_get_static.py to fetch all urls in res_todo.txt
