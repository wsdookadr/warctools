#!/bin/bash
LIMIT=$1
shift
URLS="$@"

echo "LIMIT=$LIMIT"

# start with a fresh profile (any cache/cookies are wiped out)
rm -rf ~/.mozilla/firefox/p1/*
cp -r ff/* ~/.mozilla/firefox/p1/

# remove any cache metadata and data
#
# actually the cache data sits in ~/.cache/mozilla/firefox/
# the exact location is given by about:config browser.cache.disk.parent_directory
# but for this particular case the disk cache size is already set to 0 in the browser
# settings so we only have to delete the metadata
rm -rf ~/.mozilla/firefox/p1/*.sqlite ~/.mozilla/firefox/p1/sessionstore.js

timeout $LIMIT firefox \
--headless \
--profile ~/.mozilla/firefox/p1 \
${URLS}
