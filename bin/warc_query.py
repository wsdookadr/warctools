#!/usr/bin/python3
import os
import re
import argparse
import sqlite3
import subprocess

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='WARC join tool')
    arg_parser.add_argument('--type', dest='type', action='store', default=1, choices=[1,2,3,4], type=int, help='type of search (1|2|3|4)')
    arg_parser.add_argument('--out', dest='out', action='store', default="console", choices=["live","kiwix","console"], type=str, help='output (live|kiwix|console)')
    arg_parser.add_argument('--query', dest='query', action='store', required=True, type=str, help='actual query')
    arg_parser.add_argument('--ex', dest='ex', action='store', type=bool, help='print example page')
    arg_parser.add_argument('--page', dest='page', action='store', type=int, required=False, help='which page of the results to print')

    args = arg_parser.parse_args()

    DB="db/big.db"
    BROWSER="google-chrome-stable"

    Q=[""] * 20

    # fts5 search, will search all columns for pattern
    Q[1] = """
    SELECT DISTINCT url
    FROM warc_fts
    WHERE warc_fts MATCH ?
    ;
    """

    # fts4 search, will search in the text column
    # will order the results by number of occurences of the matched pattern per document
    Q[2] = """
    SELECT DISTINCT url, occ FROM (
        SELECT url, (length(offsets(warc_fts4)) - length(replace(offsets(warc_fts4), ' ', '')) + 1)/4 AS occ
        FROM warc_fts4
        WHERE text MATCH ? AND url <> ''
        ORDER BY occ DESC
    );
    """

    # sort results by text size
    Q[3] = """
    SELECT DISTINCT url
    FROM warc_fts
    WHERE warc_fts MATCH ?
    ORDER BY text_size
    """

    con = sqlite3.connect(DB)
    cur = con.cursor()

    if args.out == 'console':
        for r in cur.execute(Q[args.type], (args.query,)):
            print("\t".join(map(str, reversed(r))))
    elif args.out == 'live':
        for r in cur.execute(Q[args.type], (args.query,)):
            subprocess.Popen([BROWSER, r[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif args.out == 'kiwix':
        for r in cur.execute(Q[args.type], (args.query,)):
            v = re.sub(r'https?://','http://localhost:8083/big/A/',r[0])
            subprocess.Popen([BROWSER, v], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



