#!/bin/bash
#
# Note: this is designed for small files, maybe <40MB in size
#
process() {
    i="$1"
    TMP="tmp/$i/"
    mkdir -p $TMP 2>/dev/null
    timeout 6 \
    ./v_warc2zim/bin/warc2zim                            \
    --verbose                                            \
    --lang en                                            \
    --output $TMP                                        \
    --zim-file tmp.zim                                   \
    --name "big" warc/$i.warc > log/$i.log 2>&1
}

export -f process

find warc/ -name "*.warc"              | \
xargs -I{} basename "{}"               | \
sed -e 's/\.warc\.gz//; s/\.warc//;'   | \
xargs -I{} -P4 bash -c 'process "{}"'


echo "The following WARC did not pass warc2zim validation:"
grep -r -L "^set index" log/ | sed -e 's/log/warc/g'
