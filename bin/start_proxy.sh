#!/bin/bash
OUT="$1"
mkdir warc/
rm dump.har dump.warc
~/.local/bin/mitmdump -k -m socks5 -p 9001 -s ./har_dump.py --set hardump=./dump.har 
har2warc dump.har dump.warc
cp dump.warc warc/$OUT

ls -lhS dump.har warc/$OUT
