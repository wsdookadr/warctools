#!/bin/bash
#
# Note: this is designed for small warc, less than 200MB in size
#
# Receives a batch number and validates a warc file in warc/
# Writes the output to log/
#
process() {
    i="$1"
    TMP="tmp_1/$i/"
    mkdir -p $TMP/partial/ 2>/dev/null
    cp warc/$i.warc sample.warc $TMP/partial/
    env VIRTUAL_ENV=v_warcio                 \
        ./v_warcio/bin/python ./warc_join.py \
        --indir $TMP/partial/                \
        --out $TMP/test.warc
    timeout 6 \
    ./v_warc2zim/bin/warc2zim                            \
    --favicon favicon.ico                                \
    --verbose                                            \
    --lang en                                            \
    --output $TMP                                        \
    --zim-file tmp.zim                                   \
    --name "big" $TMP/test.warc > log/$i.log 2>&1

    rm -rf "$TMP"
}

WARC_NUM=$(basename "$1" | sed -e 's/\.warc\.gz//; s/\.warc//;')
process $WARC_NUM
