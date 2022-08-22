#!/bin/bash
F="$1"

rm -f with_sitemap.txt without_sitemap.txt;

cat "$F" | \
perl -ne 'm{^(https?://[^/\r\n]+)} && print "$1,$_"; ' | \
parallel --colsep=, --no-notice -j2 'c=$(curl -s -I "{1}/sitemap.xml" | grep "^HTTP" | grep 200 | wc -l); echo "$c,{1},{2}" ;' | \
parallel --colsep=, --no-notice -j1 '
    if [[ "{1}" -eq "1" ]]; then
        echo "sitemap1 \"{2}/sitemap.xml\" >> list_urls2.txt" >> with_sitemap.txt;
    else
        echo "sitemap2 \"{3}\" >> list_urls2.txt" >> without_sitemap.txt;
    fi
'
