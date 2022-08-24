#!/usr/bin/python3
import sys
import os
import re
import argparse
import subprocess
import urllib
import lxml.html
import lxml.etree as et
from io import StringIO, BytesIO, BufferedReader
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecord
from warcio.limitreader import LimitReader
import sqlite3

def valid_dir(outputdir):
    if not os.path.isdir(outputdir):
        raise argparse.ArgumentTypeError('input directory does not exist')
    return outputdir

def create_db(db_path):
    sql='''
    PRAGMA ENCODING = "UTF-8";
    CREATE VIRTUAL TABLE warc_fts USING fts5(
        url,
        fmt,
        raw_size,
        text_size,
        text
    );

    CREATE VIRTUAL TABLE warc_fts4 USING fts4(
        url,
        fmt,
        raw_size,
        text_size,
        text
    );
    '''
    con = sqlite3.connect(db_path)
    con.executescript(sql)
    con.close()


def import_batch(db_path, batch):
    sql1='INSERT INTO warc_fts VALUES(?,?,?,?,?);'
    sql2='INSERT INTO warc_fts4 VALUES(?,?,?,?,?);'

    con = sqlite3.connect(db_path)
    con.execute('PRAGMA journal_mode = WAL')
    con.execute('PRAGMA synchronous = OFF')


    try:
        c = con.cursor()
        c.executemany(sql1, batch)
        con.commit()
    except con.Error as e:
        print(e)

    try:
        c = con.cursor()
        c.executemany(sql2, batch)
        con.commit()
    except con.Error as e:
        print(e)

    con.close()

def optimize_db(db_path):
    sql='''
    INSERT INTO warc_fts(warc_fts)   VALUES('optimize');
    INSERT INTO warc_fts4(warc_fts4) VALUES('optimize');
    VACUUM;
    '''
    con = sqlite3.connect(db_path)
    con.executescript(sql)
    con.close()

def process_html(buf):
    r = lxml.html.fromstring(buf)
    for u in r.xpath('//script|//style'):
        u.drop_tree()
    text = r.text_content()
    text = text.strip()
    if text == "":
        return

    t1 = re.sub(r'[^a-zA-Z0-9_\-]',' ',text)
    t2 = re.sub(r'[\n\r\t]+',' ',t1)
    t3 = re.sub(r'\s+',' ',t2)
    text = t3

    raw_size,text_size = 0,0
    try:
        raw_size = int(record.http_headers.get_header('Content-Length'))
        text_size = len(text)
    except Exception as e:
        raw_size,text_size = 0,0

    if uri is not None and raw_size is not None and text_size is not None and text is not None:
        return (uri, "html", str(raw_size), str(text_size), text)
    else:
        return None

def process_pdf(buf):
    process = subprocess.Popen(
        ['pdftotext','-','-'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    p = process.communicate(input=buf)

    text = p[0].decode()
    t1 = re.sub(r'[^a-zA-Z0-9_\-]',' ',text)
    t2 = re.sub(r'[\n\r\t]+',' ',t1)
    t3 = re.sub(r'\s+',' ',t2)
    text = t3

    raw_size,text_size = 0,0
    try:
        raw_size = int(record.http_headers.get_header('Content-Length'))
        text_size = len(text)
    except Exception as e:
        raw_size,text_size = 0,0

    if uri is not None and raw_size is not None and text_size is not None and text is not None:
        return (uri, "pdf", str(raw_size), str(text_size), text)
    else:
        return None

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='WARC text extraction tool')
    arg_parser.add_argument('--infile', dest='infile', action='store', required=True, help='WARC file to extract text from')
    arg_parser.add_argument('--out', dest='out',action='store', required=True, help='DB path')

    args = arg_parser.parse_args()
    re_filtered_uris = re.compile(r'^(?:https://[^\.]+\.taboola.com|https://(?:[^\.]+\.)?disqus.com|https://www.geogebra.org|https://[^\.]+\.wp.com|https://fonts.googleapis.com/css|https://public-api.wordpress.com/wp-admin/rest-proxy|https://widgets.wp.com/likes/).*$')

    create_db(args.out)

    i = 0

    batch = []
    if args.infile:
        with open(args.infile, 'rb') as input_stream:
            for record in ArchiveIterator(input_stream):
                rt = record.rec_headers.get_header('WARC-Type')
                uri = record.rec_headers.get_header('WARC-Target-URI')
                rl = record.length
                ct = None

                if not uri or not uri.startswith("http"):
                    continue

                if re_filtered_uris.match(uri):
                    continue

                if rt != "response":
                    continue
                ct = record.http_headers.get_header('Content-Type')

                if re.match(r'.*(\.gif|\.png|\.jpeg|\.jpg)$', uri):
                    continue

                try:
                    stream = record.content_stream()
                    buf = stream.read()

                    row = None
                    if ct and 'html' in ct:
                        row = process_html(buf)
                    elif ct and 'pdf' in ct:
                        row = process_pdf(buf)
                    
                    if row is not None:
                        i += 1
                        batch += [row]
                except Exception as e:
                    continue

                if i == 30:
                    import_batch(args.out, batch)
                    i = 0
                    batch = []

            if i > 0:
                import_batch(args.out, batch)
                i = 0
                batch = []

        optimize_db(args.out)

