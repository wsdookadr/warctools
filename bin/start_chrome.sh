#!/bin/bash
LIMIT=$1
shift
URLS="$@"
# --ignore-certificate-errors \
timeout $LIMIT chromium \
--remote-debugging-port=9222 \
--disable-http2 \
--no-first-run \
--proxy-server="socks5://127.0.0.1:9001" \
--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
--no-sandbox \
--headless \
--autoplay-policy=no-user-gesture-required \
--disable-gpu \
--use-fake-ui-for-media-stream \
--use-fake-device-for-media-stream \
--disable-sync \
--disable-dev-shm-usage \
--disk-cache-size=0 \
--media-cache-size=0 \
--disable-application-cache \
--media-cache-size=0 \
--disable-lru-snapshot-cache \
--aggressive-cache-discard \
${URLS}
