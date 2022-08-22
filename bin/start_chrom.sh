#!/bin/bash

CACHE="/tmp/c21"
PDIR="/tmp/c22"
PDDIR="/tmp/c23"
UDIR="/tmp/c24"

for x in $CACHE $PDIR $PDDIR UDIR; do
    rm -rf $x
    mkdir -p $x
done


# --disk-cache-dir=$CACHE \
# --profile-directory=$PDIR \
# --profile-data-directory=$PDDIR \
# --user-data-directory=$UDIR \

HTTPS_PROXY="localhost:9001" HTTP_PROXY="localhost:9001" \
chromium \
--headless \
--aggressive-cache-discard \
--disable-gpu-program-cache \
--disable-gpu-shader-disk-cache \
--disable-lru-snapshot-cache \
--ignore-certificate-errors \
--disable-application-cache \
--gpu-disk-cache-size-kb=0 \
--disk-cache-size=0 \
--media-cache-size=0 \
"$1"
