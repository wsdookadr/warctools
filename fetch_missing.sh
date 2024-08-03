#!/bin/bash
mkdir missing_warc/
rm -f missing_warc/*
cp missing.txt missing_warc/list.txt
cd missing_warc/

cat list.txt | perl -pne 's{\r\n}{\n}g;' | \
shuf | parallel --progress --no-notice -j4 'echo "{1}"; wget -q --no-warc-compression --warc-file {#} -O/dev/null "{=uq=}"' :::
