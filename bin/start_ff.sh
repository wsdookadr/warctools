#!/bin/bash
URLS="$@"

pkill -f firefox
sleep 1

rm -rf ~/.mozilla/firefox/p1/*
cp -r ff/* ~/.mozilla/firefox/p1/

# remove any cache metadata and data
#
# actually the cache data sits in ~/.cache/mozilla/firefox/
# the exact location is given by about:config browser.cache.disk.parent_directory
# but for this particular case the disk cache size is already set to 0 in the browser
# settings so we only have to delete the metadata
rm -rf ~/.mozilla/firefox/p1/*.sqlite ~/.mozilla/firefox/p1/sessionstore.js

firefox \
--new-instance \
--headless \
--profile ~/.mozilla/firefox/p1 \
${URLS}
