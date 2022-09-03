#!/bin/bash

# extract links when a sitemap is available
sitemap1() {
    URL="$1"
    curl -k -L "$URL" | xmlstarlet fo --recover --noindent | grep "<loc>" | sed -e 's/<loc>//;s/<\/loc>//;'
}

# generic sitemap
sitemap2() {
    URL="$1"
    DOMAIN=$(echo "$URL" | awk -F[/:] '{print $4}')
    wget --no-parent --spider -Ptemp_dir -r "$URL" --regex-type pcre --domains="$DOMAIN" \
    --exclude-domains "linkedin.com,tumblr.com,reddit.com,whatsapp.com,getpocket.com,twitter.com,facebook.com,google.com" \
    --reject-regex ".*(redirect=|tumblr.com|linkedin.com|reddit.com|twitter.com|facebook.com|accounts.google.com|replytocom=|share=facebook|share=twitter|plus.google.com|feed=|wp-json|wp-content|wp-includes|oembed|/feed/).*" \
    -R "*redirect=*,*tumblr.com*,*linkedin.com*,*reddit.com*,*twitter.com*,*facebook.com*,*accounts.google.com*,*replytocom=*,*share=facebook*,*share=twitter*,*plus.google.com*,*feed=*,*wp-json*,*wp-content*,*wp-includes*,*oembed*,*/feed/*" \
    2>&1 | grep '^--' | awk '{ print $3 }' | grep -v '\.\(css\|js\|png\|gif\|jpg\|JPG\)$'
    rm -rf temp_dir
}

# mediawiki / wiki sitemap
sitemap3() {
    BASE="$1"
    DOMAIN=$(echo "$BASE" | awk -F[/:] '{print $4}')
    # MAIN_FILTER="$2"

    wget --no-parent -Ptemp_dir -r --spider -p -e robots=off -U mozilla \
         --regex-type pcre --accept-regex ".*($DOMAIN|Special:AllPages).*" \
         --reject-regex ".*(w\/index.php\?|Special:|Talk:|User:|Template:|action=|revision=|oldid=|printable=|title=api.php|load.php|wiki/images).*" \
         "$BASE" 2>&1 | tee log1.txt | \
         grep '^--' | awk '{ print $3 }' | grep -v '\.\(css\|js\|png\|gif\|jpg\|JPG\)$'

    rm -rf temp_dir
}

# nested blogspot/wordpress sitemap

sitemap4() {
    URL="$1"
    curl -L "$URL" | xmlstarlet format | grep "<loc>" | perl -pne 's{<loc>}{}g;s{</loc>}{}g; s{.*CDATA\[}{}g; s{\]\].*}{}g;' | xargs -I{} bash -c 'curl -L "{}" | xmlstarlet format' | grep "<loc>" | perl -pne 's{<loc>}{}g;s{</loc>}{}g; s{.*CDATA\[}{}g; s{\]\].*}{}g;' | sed -e 's/^\s\+//'
}


sitemap5() {
    URL="$1"
    mkdir temp_dir
    cd temp_dir
    httrack -s0 -*xmlrpc* -*.json -*/images/* -*google.com* -*twitter.com* -*facebook.com* -*/wp-content/* -*/wp-json/* -*/oembed/* -*/feed/* -*/wp-includes/* "$URL"
    rm -rf temp_dir
}


# phpbb forum

sitemap6() {
    URL="$1"
    DOMAIN=$(echo "$URL" | awk -F[/:] '{print $4}')
    wget --no-parent --spider -Ptemp_dir -r "$URL" --regex-type pcre --domains="$DOMAIN" --exclude-domains "twitter.com,facebook.com,google.com" \
    --accept-regex ".*(showthread.php|forumdisplay.php|viewtopic.php|viewforum.php|index.php).*" \
    --reject-regex ".*(showthread.php.*pid=|showthread.php.*action=|posting.php|search.php|ucp.php|search.php|memberlist.php|view=print|twitter.com|facebook.com|accounts.google.com|plus.google.com|feed=|wp-json|wp-content|wp-includes|oembed|/feed/).*" 2>&1 | \
    grep '^--' | awk '{ print $3 }' | grep -v '\.\(css\|js\|png\|gif\|jpg\|JPG\)$'
    rm -rf temp_dir
}

# TODO
#
# should be a generic pattern-based max-page search (bsearch)
# followed by crawling those pages and their links
sitemap_wp_nositemap() {
    URL="$1"
    export URL
    M=$(seq 60 | parallel -j20 --no-notice 'c=$(eval curl -L -s -o /dev/null -w "%{http_code}" "$URL/page/{}"); echo "$c {}"' | awk '$1 == 200 {print $2;}' | sort -n -r | head -1)
    echo $M
}

# enhanced version of sitemap2, specifically tuned for wordpress sites
# (tested, rejection rules are working fine)
sitemap7() {
    URL="$1"
    wget -r -Ptemp_dir --max-redirect=2 --no-clobber --regex-type pcre --spider --convert-links --reject-regex '.*(wp-content|\/feed\/|wp-json|wp-includes|share=|replytocom=|feed=|oembed).*' "$URL" \
    2>&1 | grep '^--' | awk '{ print $3 }' | grep -v '\.\(css\|js\|png\|gif\|jpg\|JPG\)$'
    rm -rf temp_dir
}

