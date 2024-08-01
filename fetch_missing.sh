#!/bin/bash
mkdir missing_warc/
rm -f missing_warc/*
cp missing.txt missing_warc/list.txt
cd missing_warc/
i=0
while read URL; do
    i=$((i+1))
    URL=$(echo "$URL" | perl -pne 's{\r\n}{}g;s{\n}{}g;')
    wget --no-warc-compression --warc-file $i -O/dev/null "$URL"
done < list.txt
