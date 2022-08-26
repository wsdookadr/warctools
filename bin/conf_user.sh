#!/bin/bash

#
# Import mitmproxy's self-signed cert into Chromium's cert store
#
rm -rf .pki/
mkdir -p ~/.pki/nssdb/
certfile=~/.mitmproxy/mitmproxy-ca.pem
certutil --empty-password -N -d sql:.pki/nssdb/

for certDB in $(find ~/.pki -name "cert9.db")
do
    certdir=$(dirname ${certDB});
    certutil -A -n "${certname}" -t "TCu,Cu,Tu" -i ${certfile} -d sql:${certdir}
done
certutil -L -d sql:.pki/nssdb/


# - :~d detectportal.firefox.com:200
# - :~d incoming.telemetry.mozilla.org:200
# - :~d tiles.services.mozilla.org:200
# - :~d services.addons.mozilla.org:200
# - :~d activity-stream-icons.services.mozilla.com:200
# - :~d aus5.mozilla.org:200
# - :~d blocklists.settings.services.mozilla.com:200
# - :~d ciscobinary.openh264.org:200
# - :~d content-signature.cdn.mozilla.net:200
# - :~d discovery.addons.mozilla.org:200
# - :~d download.cdn.mozilla.net:200
# - :~d firefox.settings.services.mozilla.com:200
# - :~d getpocket.cdn.mozilla.net:200
# - :~d img-getpocket.cdn.mozilla.net:200
# - :~d location.services.mozilla.com:200
# - :~d normandy.cdn.mozilla.net:200
# - :~d normandy.services.mozilla.com:200
# - :~d push.services.mozilla.com:200
# - :~d snippets.cdn.mozilla.net:200
# - :~d shavar.services.mozilla.com:200
# - :~d versioncheck-bg.addons.mozilla.org:200
# - :~d firefox-settings-attachments.cdn.mozilla.net:200
# - :~d firefox.settings.services.mozilla.com:200
# - :~d shavar.services.mozilla.com:200
# - :~d services.mozilla.com:200


#
# Block certain domains through mitmproxy
# (for FF, but also various ads)
#
cat<<'EOF' > ~/.mitmproxy/config.yaml
# https://docs.mitmproxy.org/stable/overview-features/#blocklist
# https://docs.mitmproxy.org/stable/concepts-filters/

block_list:
  - :~d adzerk.net:404
  - :~d cdn.cookielaw.org:404
  - :~d mylivechat.com:404
  - :~d petametrics.com:404
  - :~d facebook.com:404
  - :~d youtube.com:404
  - :~d ads.eu.criteo.com:404
  - :~d www.googletagmanager.com:404
  - :~d accounts.google.com:404
  - :~d adservice.google.com:404
  - :~d adservice.google.ro:404
  - :~d ad.doubleclick.net:404
  - :~d googlesyndication.com:404
  - :~d pagead2.googlesyndication.com:404
  - :~d googleads.g.doubleclick.net:404
  - :~d www.youtube-nocookie.com:404
  - :~d stats.g.doubleclick.net:404
  - :~d pixel.wp.com:404
  - :~d ssl.google-analytics.com:404
  - :~d s.pubmine.com:404
  - :~d www.google-analytics.com:404
  - :~d google-analytics.com:404
  - :~d statcounter.com:404
  - :~d stats.wp.com:404
  - :~d amazon-adsystem.com:404
  - :~d outbrain.com:404
  - :~u www.google.com/ads:404
  - :~u disqus.com/recommendations:404
  - :~u platform.twitter.com/widgets/follow_button:404
EOF


