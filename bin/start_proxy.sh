#!/bin/bash
NUM="$1"
FMT="$2"

rm -f dump.har dump.warc

env VIRTUAL_ENV=v_mitmdump \
    ./v_mitmproxy/bin/mitmdump \
    -m socks5 -p 9001 -s ./har_dump.py --set hardump=./dump.har

# 2> echo "$NUM $FMT"
if [ "$FMT" = "har" ]; then
    cp dump.har har/$NUM.har 2>/dev/null
    ls -lhS dump.har
elif [ "$FMT" = "warc" ]; then
    env VIRTUAL_ENV=v_har2warc ./v_har2warc/bin/har2warc dump.har dump.warc
    cp dump.warc warc/$NUM.warc 2>/dev/null
    ls -lhS dump.warc
fi

