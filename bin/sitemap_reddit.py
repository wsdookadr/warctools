#!/usr/bin/python3
import sys
import re
import time
import json
import requests
import datetime
import argparse

#
# Note: There is a map of reddit here https://anvaka.github.io/map-of-reddit
# 

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='reddit sitemap generator')
    arg_parser.add_argument('--sub'   ,dest='sub'  , action='store', required=True, help='get all threads for this sub')
    arg_parser.add_argument('--query' ,dest='query', action='store', required=False, default=None, help='search for threads with at least one comment matching')
    arg_parser.add_argument('--debug' ,dest='debug', action='store_true', default=False, required=False, help='print entire response instead of just urls')

    args = arg_parser.parse_args()

    base_sub  = "https://api.pushshift.io/reddit/search/submission/?size=500&sort=desc&sort_type=created_utc&subreddit={0}&before={1}"
    base_subq = "https://api.pushshift.io/reddit/search/comment/?size=500&sort=desc&sort_type=created_utc&subreddit={0}&before={1}&q={2}"

    old_ts = int(time.time())

    done = False
    while True:
        if args.sub and not args.query:
            u = base_sub.format(args.sub,old_ts)
        elif args.sub and args.query:
            u = base_subq.format(args.sub,old_ts,args.query)
        r = requests.get(u)

        try:
            j = r.json()
        except Exception as e:
            done = True

        if done or (len(j["data"]) == 0):
            break

        if not args.debug:
            if args.sub and not args.query:
                for x in j["data"]:
                    if "full_link" in x:
                        print(x["full_link"])
            elif args.sub and args.query:
                for x in j["data"]:
                    if "permalink" in x:
                        v = "https://www.reddit.com" + x["permalink"]
                        v = re.sub(r'\/[^\/]+\/$','',v)
                        print(v)
        else:
            print(json.dumps(j, indent=4, sort_keys=True))

        old_ts = min(list(map(lambda x: x["created_utc"], j["data"])))
        old_dt = datetime.datetime.fromtimestamp(old_ts).strftime('%Y-%m-%d %H:%M:%S')
        print(u,file=sys.stderr)
        print(old_ts,old_dt,file=sys.stderr)


