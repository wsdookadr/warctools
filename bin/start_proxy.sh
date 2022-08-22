#!/bin/bash
OUT="$1"
mkdir warc/
rm dump.har dump.warc
env VIRTUAL_ENV=v_mitmdump ./v_mitmproxy/bin/mitmdump -k -m socks5 -p 9001 -s ./har_dump.py --set hardump=./dump.har
env VIRTUAL_ENV=v_har2warc ./v_har2warc/bin/har2warc dump.har dump.warc
cp dump.warc warc/$OUT

ls -lhS dump.har warc/$OUT
