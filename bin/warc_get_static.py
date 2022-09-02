#!/usr/bin/env python3
import os
import re
import argparse
import subprocess
import signal
from time import sleep
def kill_mitm():
    os.system('''
    pkill -INT -f mitmdump
    '''
    )

#
# This will take a list of urls for static resources and make requests to them via
# a local mitmproxy instance. The responses will be discarded into /dev/null. The
# proxy will record the traffic and write it to storage.
#
# It will then convert each batch's traffic to WARC.
# Curl will be used as an HTTP client because it knows socks5.
#

if __name__ == '__main__':
    with open(args.url_list, 'r') as fh:
        all_urls = list(fh)

    batches = list_to_batches(all_urls, args.batch_size)

    # TODO: compute how many numbered warcs there are and add another one
    for b in batches:
        proc = []
        proc_proxy = subprocess.Popen(["/bin/bash","start_proxy.sh",batch_num,args.output_type])
        sleep(1)

        # start each request in a bg process
        for u in b:
            p = subprocess.Popen(['/usr/bin/curl','-x','socks5://127.0.0.1:9001',u])
            proc.append(p)

        # wait for bg processes
        for p in proc:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired as e:
                pass
            p.send_signal(signal.SIGKILL)
        kill_mitm()

        try:
            proc_proxy.wait(timeout=1)
        except subprocess.TimeoutExpired as e:
            pass

