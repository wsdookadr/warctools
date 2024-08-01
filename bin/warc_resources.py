#!/usr/bin/env python3
import os
import re
import argparse
import urllib
import lxml.html
import lxml.etree as et
from io import StringIO, BytesIO
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecord
from warcio.limitreader import LimitReader

#
#
# This extracts all latex image urls from all WARCs in a given directory:
#
#   ./bin/warc_patch_mathjax.py --infile warc/big.warc --get-latex-imgs 2>/dev/null
#
#

def valid_dir(outputdir):
    if not os.path.isdir(outputdir):
        raise argparse.ArgumentTypeError('input directory does not exist')
    return outputdir

def absent_file(f):
    if os.path.isfile(f):
        raise argparse.ArgumentTypeError('file already present')
    return f

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='WARC join tool')
    arg_parser.add_argument('--infile', dest='infile', action='store', required=True, help='input WARC')
    arg_parser.add_argument('--get-latex-imgs', dest='get_latex_imgs', action='store_true', required=False, help='switch to extract latex image urls')
    arg_parser.add_argument('--imgs', dest='imgs', action='store_true', required=False, help='get images matching substring')
    arg_parser.add_argument('--url-filter', dest='url_filter', action='store', required=False, help='filter for warc web pages to extract links from')
    arg_parser.add_argument('--pdfs', dest='pdfs', action='store_true', required=False, help='grab pdf urls')
    arg_parser.add_argument('--js', dest='js', action='store_true', required=False, help='grab script urls')
    arg_parser.add_argument('--css', dest='css', action='store_true', required=False, help='grab css style urls')
    arg_parser.add_argument('--links', dest='links', action='store_true', required=False, help='all links')

    args = arg_parser.parse_args()

    seen = {}

    # extraction
    if args.infile and (args.get_latex_imgs or args.imgs or args.pdfs or args.js or args.css or args.links):
        with open(args.infile, 'rb') as input_stream:
            for record in ArchiveIterator(input_stream):
                rt = record.rec_headers.get_header('WARC-Type')
                uri = record.rec_headers.get_header('WARC-Target-URI')
                rl = record.length
                ct = None

                if rt != 'response':
                    continue

                ct = record.http_headers.get_header('Content-Type')

                if not ct or 'html' not in ct:
                    continue

                if args.url_filter and not re.match(args.url_filter, uri):
                    continue

                stream = record.content_stream()
                buf = stream.read()

                try:
                    r = lxml.html.fromstring(buf)
                    r.make_links_absolute(uri)
                except Exception as e:
                    continue

                if args.get_latex_imgs:
                    for e in r.xpath('//img[contains(@src,"latex.php")]'):
                        print(e.attrib['src'])

                elif args.imgs:
                    for e in r.xpath('//img'):
                        if 'src' in e.attrib and re.match(r'^http',e.attrib['src']):
                            print(e.attrib['src'])

                if args.pdfs:
                    for e in r.xpath('//a[contains(@href,".pdf")]'):
                        print(e.attrib['href'])

                if args.js:
                    for e in r.xpath('//script'):
                        if 'src' in e.attrib:
                            print(e.attrib['src'])

                if args.css:
                    for e in r.xpath('//link[contains(@href,".css")]'):
                        if 'href' in e.attrib:
                            print(e.attrib['href'])

                if args.links:
                    for e in r.xpath('//a'):
                        if 'href' in e.attrib and re.match(r'^http',e.attrib['href']):
                            print(e.attrib['href'])


