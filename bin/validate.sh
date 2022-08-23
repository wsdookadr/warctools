#!/bin/bash
#
# Note: this is designed for small warc, less than 200MB in size
#
process() {
    i="$1"
    TMP="tmp/$i/"
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

export -f process

find warc/ -name "*.warc"              | \
grep -v "big.warc"                     | \
xargs -I{} basename "{}"               | \
sed -e 's/\.warc\.gz//; s/\.warc//;'   | \
xargs -I{} -P4 bash -c 'process "{}"'

echo "The following WARC did not pass warc2zim validation:"
grep -r -L "^set index" log/ | sed -e 's/log/warc/g'
