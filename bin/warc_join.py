#!/usr/bin/env python3
import os
import re
import argparse
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.archiveiterator import ArchiveIterator

def valid_dir(outputdir):
    if not os.path.isdir(outputdir):
        raise argparse.ArgumentTypeError('input directory does not exist')
    return outputdir

def absent_file(f):
    if os.path.isfile(f):
        raise argparse.ArgumentTypeError('file already present')
    return f

def extract_num(s):
    s_num = re.sub("[^0-9]","",s)
    return int(s_num)

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='WARC join tool')
    arg_parser.add_argument('--indir', dest='indir', action='store', required=True, type=valid_dir, help='input directory containing WARC')
    arg_parser.add_argument('--out', dest='out', action='store', required=False, type=absent_file, help='output WARC')
    arg_parser.add_argument('--fix', dest='fix', action='store_true', required=False, help='fix record lengths and checksums')
    arg_parser.add_argument('--dry1',dest='dry1',action='store_true', required=False, help='dry run type 1')
    arg_parser.add_argument('--exclude', dest='exclude', action='store', type=str, required=False, help='exclude WARC records that match the pattern')
    arg_parser.add_argument('--disable-filter', dest='default_filter', action='store_false', required=False, default=True, help='disable default uri filter')

    args = arg_parser.parse_args()

    re_allowed_ct = re.compile(r'^(?:application/http|image/png|text/html|image/jpeg|application/json|application/javascript|image/gif|image/svg\+xml|text/plain|text/javascript|text/css|application/xhtml\+xml|application/vnd.geogebra.file|font/ttf|application/x-javascript|font/woff2|application/octet-stream|font/woff|text/markdown|application/binary|application/font-woff2|application/font-woff|application/xml|image/webp|audio/mpeg|image/x-xbitmap|text/x-c|image/vnd.microsoft.icon|text/xml|image/bmp|text/csv|application/pdf|font/otf|application/vnd.ms-fontobject|image/jpg|image/x-icon|application/x-font-woff|model/gltf-binary).*$')
    re_filtered_uris = re.compile(r'^(?:https://[^\.]+.mylivechat.com|https://shavar.services.mozilla.com|https://[^\.]+.cdn.mozilla.net/chains|https://query.petametrics.com|https://www.google.com/recaptcha|https://www.facebook.com|https://[^\.]+.youtube.com|https://ads.eu.criteo.com|http://www.googletagmanager.com|https://accounts.google.com|https://www.google.com/ads|https://adservice.google.com/|https://adservice.google.ro|https://ad.doubleclick.net|https://[^\.]+.googlesyndication.com|https?://pagead2.googlesyndication.com|https?://googleads.g.doubleclick.net/|https?://www.youtube-nocookie.com|https?://www.youtube.com|https://platform.twitter.com/widgets/follow_button|https://stats.g.doubleclick.net|https://pixel.wp.com/|https://ssl.google-analytics.com/|https://s.pubmine.com|https?://www.google-analytics.com|https?://region\d+.google-analytics.com|https://disqus.com/recommendations|<\?metadata|https://[^\.]+.statcounter.com|https://stats.wp.com|https://[^\.]+.wp.com/[^\.]+.zemanta.com|https://[^\.]+.amazon-adsystem.com|https://[^\.]+.outbrain.com|https://[^\.]+.outbrainimg.com).*$')

    re_exclude = None
    if args.exclude:
        re_exclude = re.compile(args.exclude)

    seen_uri = {}
    MAX_RECORD_LENGTH = 130 * 1024 * 1024

    with open(args.out, 'wb') as output_stream:
        writer = WARCWriter(output_stream, gzip=True)
        L = sorted(filter(lambda x: x.name != "big.warc" and not x.is_dir(), os.scandir(args.indir)), key=lambda e: extract_num(e.name))
        for obj_f in L:
            if obj_f.is_file():
                f = obj_f.path
                if not re.match(r'^.*\.(warc|warc.gz)$', f):
                    continue
                if args.dry1:
                    print(f)
                    continue
                with open(f, 'rb') as input_stream:
                    for record in ArchiveIterator(input_stream):
                        rt = record.rec_headers.get_header('WARC-Type')
                        uri = record.rec_headers.get_header('WARC-Target-URI')
                        rl = record.length

                        if rt not in ['request','response']:
                            continue

                        if rl > MAX_RECORD_LENGTH:
                            continue

                        if args.fix:
                            record.length = None

                        uri1 = re.sub(r'^https://web.archive.org/web/\d+id_/',r'',uri)
                        if uri1 != uri:
                            uri = uri1
                            record.rec_headers.replace_header('WARC-Target-URI',uri)

                        if not uri or (not uri.startswith('http') and not uri.startswith('<http')):
                            continue

                        # uri with no protocol
                        unp = re.sub(r'^https?://','',uri)

                        if (unp,rt) in seen_uri:
                            continue
                        
                        seen_uri[(unp,rt)] = 1

                        if args.default_filter and re_filtered_uris.match(uri):
                            continue

                        if args.exclude and re_exclude.match(uri):
                            continue

                        if rt == 'response':
                            ct = record.http_headers.get_header('Content-Type')
                            if ct and not re_allowed_ct.match(ct):
                                continue

                        if rt == 'request':
                            pass

                        writer.write_record(record)

    if os.stat(args.out).st_size == 0 or args.dry1:
        os.remove(args.out)


