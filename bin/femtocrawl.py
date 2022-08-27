#!/usr/bin/env python3
import os
import re
import argparse
import subprocess
from time import sleep

def kill_browser_mitm(browser):
    os.system('''
    pkill -INT -f mitmdump
    pkill -f {0}
    killall {0}-esr
    killall {0}
    '''.format(browser)
    )

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
        kill_browser_mitm(args.browser)
        sleep(3)
        batch_num = str(i)
        subprocess.Popen(["/bin/bash","start_proxy.sh",batch_num,args.output_type])
        sleep(1)
        subprocess.Popen(["/bin/bash",start_script,str(args.batch_timeout)] + batch)
        sleep(int(args.batch_timeout))
    kill_browser_mitm(args.browser)
    sleep(1)



