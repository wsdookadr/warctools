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

def validate_warc(i):
    warc_file="warc/{0}.warc".format(i)
    if os.path.isfile(warc_file):
        subprocess.Popen(["/bin/bash","warc_validate.sh",str(i)])

def list_to_batches(L, n):
    A = []
    B = []
    for x in L:
        B += [x]
        if len(B) == n:
            A.append(B)
            B = []
    if len(B) > 0:
        A.append(B)
    return A

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='operator script for femtocrawl')
    arg_parser.add_argument('--url-list'     ,dest='url_list'      ,action='store', required=True , help='input file list')
    arg_parser.add_argument('--browser'      ,dest='browser'       ,action='store', required=False, default='firefox', choices=['chromium','firefox'], help='browser to use')
    arg_parser.add_argument('--batch-timeout',dest='batch_timeout' ,action='store', required=False, default=25,help='batch timeout')
    arg_parser.add_argument('--batch-size'   ,dest='batch_size'    ,action='store', required=False, default=10, help='batch size')
    arg_parser.add_argument('--output-type'  ,dest='output_type'   ,action='store', required=False, default='warc', choices=['har','warc'], help='output type')
    args = arg_parser.parse_args()

    if args.browser == 'chromium':
        start_script = 'start_chrome.sh'
    elif args.browser == 'firefox':
        start_script = 'start_ff.sh'

    with open(args.url_list, 'r') as fh:
        all_urls = list(fh)
    batches = list_to_batches(all_urls, args.batch_size)

    i = 0
    for batch in batches:
        i += 1
        print("i=",i)
        if os.path.isfile("warc/{0}.warc".format(i)):
            continue
        batch_num = str(i)
        proc_proxy = subprocess.Popen(["/bin/bash","start_proxy.sh",batch_num,args.output_type])
        sleep(1)
        subprocess.Popen(["/bin/bash",start_script,str(args.batch_timeout)] + batch)
        sleep(int(args.batch_timeout))

        kill_mitm()
        try:
            proc_proxy.wait(timeout=7)
        except subprocess.TimeoutExpired as e:
            pass
        proc_proxy.send_signal(signal.SIGKILL)
        validate_warc(i)

    sleep(1)

