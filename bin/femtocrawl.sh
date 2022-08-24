#!/bin/bash
i=0
tabs=10
delay=25
INPUT="$1"

group_in_batches() {
    awk -v tabs=$tabs '
        BEGIN{n=0; };
        { n++; if(n>tabs){n=0; print s;s=""; }; s = s "\""$1"\" ";  };
        END { print s; };
    '
}

cat "$INPUT"     | \
group_in_batches | \
while read x; do
    pkill -INT -f mitmdump
    pkill -KILL -f firefox

    i=$((i+1))
    echo "i=$i"

    if [[ -f "warc/$i.warc" ]]; then
        continue
    fi

    sleep 3

    ./start_proxy.sh "$i.warc" &

    sleep 1

    eval ./start_ff.sh $x >/dev/null 2>&1 &
    eval echo $x > warc/$i.urls

    sleep $delay
done

pkill -INT -f mitmdump
pkill -KILL -f firefox
i=$((i+1))

sleep 1
