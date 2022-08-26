#!/bin/bash
#
# attempt to disable Firefox's auto-update
# https://github.com/mozilla/policy-templates
# https://support.mozilla.org/en-US/kb/customizing-firefox-using-policiesjson
#
cat<<EOF > /usr/lib/firefox-esr/distribution/policies.json
{
  "policies": {
    "AppAutoUpdate": false,
    "ExtensionUpdate": false,
    "BackgroundAppUpdate": false,
    "DisableAppUpdate": true,
    "DisableFeedbackCommands": true,
    "DisableFirefoxStudies": true,
    "DisablePocket": true,
    "DisableSystemAddonUpdate": true,
    "DisableTelemetry": true,
    "ExtensionUpdate": false,
    "NetworkPrediction": true,
    "PromptForDownloadLocation": false,
    "FirefoxHome": {
      "Search": true,
      "TopSites": false,
      "SponsoredTopSites": false,
      "Highlights": false,
      "Pocket": false,
      "SponsoredPocket": false,
      "Snippets": false,
      "Locked": false
    },
  }
}
EOF


