#!/usr/bin/python3
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
# Examples:
#
# This patches all web pages in the WARC archives in a given directory, and joins together
# all the responses:
# 
#   rm out1.warc ; ./bin/warc_patch_mathjax.py --indir warc/ --out out1.warc
#
# This extracts all latex image urls from all WARCs in a given directory:
#
#   ./bin/warc_patch_mathjax.py --indir warc/ --get-latex-imgs 2>/dev/null
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

mjax_includes_0='''
<style warc-mathjax-patch="1">
.fixedButton{
    position: fixed;
    bottom: 0px;
    right: 0px; 
    padding: 20px;
    background: lightgoldenrodyellow;
    opacity: 0.8;
}

.roundedFixedBtn{
  height: 30px;
  line-height: 40px;  
  width: 130px;  
  font-size: 15px;
  text-align: center;
  cursor: pointer;
}
</style>
'''

mjax_includes_1='''
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML" crossorigin="anonymous" warc-mathjax-patch="1">
function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function enableMJ() {
    var d = document;
    var latexImgs = Array.apply(null, d.querySelectorAll('img')).filter((x) => x.src.match(/latex.php/) )

    latexImgs.forEach((el) => {
        var span = d.createElement('span');

        var origsrc = el.src;
        var tex = el.src;
        tex = tex.replace(/^.*\?latex=/,"").replace(/\\x26bg=.*$/,"");
        tex = decodeURIComponent( decodeURI(tex).replace(/\+/g," ") );
        span.setAttribute("class","math notranslate nohighlight patchedmjx");
        span.textContent = " \\\\( " + tex + " \\\\) ";
        console.log(tex);
        insertAfter(span, el);
        span.setAttribute('tex',tex);
        el.setAttribute('src','');
        el.setAttribute('srcset','');
        el.setAttribute('alt','');
        el.setAttribute('origsrc',origsrc);
    });

    MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    d.getElementById('switchMJButton').onclick = disableMJ;
    d.getElementById('switchMJButton').textContent = "disable mathjax";
};

function disableMJ() {
    var d = document;
    d.querySelectorAll('span.patchedmjx').forEach((el) => {
        let parent = el.parentNode;
        parent.removeChild(el);
    });

    var latexImgs = Array.apply(null, d.querySelectorAll('img'))
        .filter((x)=> x.hasAttribute("origsrc"))
        .filter((x)=> x.getAttribute("origsrc").match(/latex.php/));
    latexImgs.forEach((el) => {
        el.setAttribute("src",el.getAttribute("origsrc"));
    });
    MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    d.getElementById('switchMJButton').onclick = enableMJ;
    d.getElementById('switchMJButton').textContent = "enable mathjax";
};

var switchMJButton = document.createElement("span");
switchMJButton.setAttribute("id","switchMJButton");
switchMJButton.setAttribute("class","fixedButton roundedFixedBtn");
switchMJButton.textContent = "enable mathjax";
switchMJButton.onclick = enableMJ;

document.body.appendChild(switchMJButton);

</script>
'''

mjax_includes_2='''
<script type="text/x-mathjax-config" warc-mathjax-patch="1">
MathJax.Hub.Config({
  inlineMath: [ ['$','$'], ['\\\\(','\\\\)'] ],
  CommonHTML: {
    scale: 125
  },
  TeX: {
    Macros: {
      textsc: ['\\\\style{font-variant-caps: small-caps}{\\\\text{#1}}', 1],
    },
  },
  chtml: {
    mtextFont: "serif"
  },
  svg: {
    mtextFont: "serif"
  },  
});
</script>
'''



if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='WARC join tool')
    arg_parser.add_argument('--indir', dest='indir', action='store', required=True, type=valid_dir, help='input directory containing WARC')
    arg_parser.add_argument('--out', dest='out', action='store', required=False, type=absent_file, help='output WARC')
    arg_parser.add_argument('--get-latex-imgs', dest='get_latex_imgs', action='store_true', required=False, help='switch to extract latex image urls')
    arg_parser.add_argument('--imgs', dest='imgs', action='store_true', required=False, help='get images matching substring')
    arg_parser.add_argument('--url-filter', dest='url_filter', action='store', required=False, help='regex filter for web pages')
    arg_parser.add_argument('--pdfs', dest='pdfs', action='store_true', required=False, help='grab pdf urls')
    arg_parser.add_argument('--js', dest='js', action='store_true', required=False, help='grab script urls')
    arg_parser.add_argument('--css', dest='css', action='store_true', required=False, help='grab css style urls')

    args = arg_parser.parse_args()

    seen = {}

    # extraction
    if args.indir and (args.get_latex_imgs or args.imgs or args.pdfs or args.js or args.css):
        for obj_f in sorted(os.scandir(args.indir), key=lambda e: e.name):
            if obj_f.is_file():
                f = obj_f.path
                with open(f, 'rb') as input_stream:
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
                                if 'src' in e.attrib:
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

    # patching
    if args.indir and args.out:
        with open(args.out, 'wb') as output_stream:
            writer = WARCWriter(output_stream, gzip=True)
            for obj_f in sorted(os.scandir(args.indir), key=lambda e: e.name):
                if obj_f.is_file():
                    f = obj_f.path
                    print("f=",f)
                    with open(f, 'rb') as input_stream:
                        for record in ArchiveIterator(input_stream):
                            rawPayload = BytesIO(record.raw_stream.read())
                            record_copy = ArcWarcRecord(record.format, record.rec_type, record.rec_headers, rawPayload, record.http_headers, record.content_type, record.length)
                            rt = record.rec_headers.get_header('WARC-Type')
                            uri = record.rec_headers.get_header('WARC-Target-URI')
                            rl = record.length
                            ct = None

                            if rt in ["metadata","warcinfo","resource"]:
                                continue

                            if (rt,uri) in seen:
                                continue

                            if args.url_filter and not re.match(args.url_filter, uri):
                                continue
                            print(rt, uri)

                            if rt == 'request':
                                writer.write_record(record_copy)
                                seen[(rt,uri)] = 1
                                continue

                            if rt == 'response':
                                ct = record.http_headers.get_header('Content-Type')

                                if not ct:
                                    seen[(rt,uri)] = 1
                                    continue

                                if 'html' not in ct:
                                    writer.write_record(record_copy)
                                    seen[(rt,uri)] = 1
                                    continue

                            if rt == 'response' and record.http_headers.get_statuscode() not in ["200","201","202","302","304"]:
                                writer.write_record(record_copy)
                                seen[uri] = 1
                                continue

                            if rt == 'response':
                                stream = record.content_stream()
                                buf = stream.read()
                                len_old = len(buf)

                                try:
                                    r = lxml.html.fromstring(buf)
                                except Exception as e:
                                    writer.write_record(record_copy)
                                    seen[(rt,uri)] = 1
                                    continue

                                num_eqs = len(r.xpath('//img[contains(@src,"latex.php")]'))

                                if num_eqs == 0:
                                    writer.write_record(record_copy)
                                    seen[(rt,uri)] = 1
                                    print("HERE!")
                                    continue

                                # remove patched elements so we can repatch it if that's the case
                                for e in r.xpath('//*[@warc-mathjax-patch="1"]'):
                                    e.getparent().remove(e)

                                h = r.xpath('//head')[0]
                                h.append(et.XML(mjax_includes_0))
                                h = r.xpath('//body')[0]
                                h.append(et.XML(mjax_includes_1))
                                h = r.xpath('//body')[0]
                                h.append(et.XML(mjax_includes_2))

                                try:
                                    new_buf = lxml.html.tostring(r)
                                except Exception as e:
                                    writer.write_record(record_copy)
                                    seen[(rt,uri)] = 1
                                    continue

                                payload = LimitReader(BytesIO(new_buf), len(new_buf))
                                record.http_headers.replace_header('Content-Length', str(len(new_buf)))

                                # warcio recomputes Content-Length and the block/payload digests
                                # if None is passed as the record length
                                new_record = ArcWarcRecord(
                                        record.format,
                                        record.rec_type,
                                        record.rec_headers,
                                        payload,
                                        record.http_headers,
                                        record.content_type,
                                        None)
                                writer.write_record(new_record)
                                seen[(rt,uri)] = 1


