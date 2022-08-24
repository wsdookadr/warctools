#!/bin/bash

~/.local/bin/virtualenv v_mitmproxy
chmod +x ./v_mitmproxy/bin/activate
source ./v_mitmproxy/bin/activate
pip3 install mitmproxy==8.1.1 && pip3 cache purge
deactivate

~/.local/bin/virtualenv v_har2warc
chmod +x ./v_har2warc/bin/activate
source ./v_har2warc/bin/activate
pip3 install har2warc==1.0.4 && pip3 cache purge
deactivate

~/.local/bin/virtualenv v_warcio
chmod +x ./v_warcio/bin/activate
source ./v_warcio/bin/activate
pip3 install warcio==1.7.4 && pip3 cache purge
deactivate

~/.local/bin/virtualenv v_warc2zim
chmod +x ./v_warc2zim/bin/activate
source ./v_warc2zim/bin/activate
pip3 install warc2zim==1.4.3 && pip3 cache purge
deactivate

~/.local/bin/virtualenv v_warcindex
chmod +x ./v_warcindex/bin/activate
source ./v_warcindex/bin/activate
pip3 install warcio==1.7.4 && pip3 cache purge
pip3 install lxml==4.6.3 && pip3 cache purge
deactivate
