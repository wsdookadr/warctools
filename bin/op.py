#!/usr/bin/env python3
import os
import re
import argparse
def valid_dir(outputdir):
    if not os.path.isdir(outputdir):
        raise argparse.ArgumentTypeError('input directory does not exist')
    return outputdir

#
#
# dir structure:
# 
# warc/    - all the single-batch warcs that were captured by femtocrawl (including all their resources)
# har/     - where har are kept (if the har output format is selected)
# log/     - this contains the logs for validation (running warc2zim for each batch). they correspond to files in warc/
# zim/     - contains the zim file converted after joining together all warc in warc/
# db/      - contains an sqlite database with full text indexes to allow offline searches
# input/   - scripts that produce the list_urls.txt file
#
#
#

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='operator script for femtocrawl')
    arg_parser.add_argument('--output-type' ,dest='output_type'   ,action='store', required=False, default='warc', choices=['har','warc'], help='output type')
    arg_parser.add_argument('--browser'     ,dest='browser'       ,action='store', required=False, default='firefox', choices=['chromium','firefox'], help='browser to use')
    arg_parser.add_argument('--shell'       ,dest='shell', action='store_true', required=False, help='starts the container and provides a shell')
    arg_parser.add_argument('--attach'      ,dest='attach', action='store_true', required=False, help='attach to first femtocrawl container found')
    arg_parser.add_argument('--clean'       ,dest='clean', action='store_true', required=False, help='cleans any data from previous crawls')
    arg_parser.add_argument('--crawl'       ,dest='crawl', action='store_true', required=False, help='runs docker on default input file')
    arg_parser.add_argument('--join'        ,dest='join', action='store_true'  , required=False, help='joins all warc into a single warc(prep for zim conversion)')
    arg_parser.add_argument('--exclude'     ,dest='exclude', action='store'  , required=None, help='exclude entries matching pattern')
    arg_parser.add_argument('--validate'    ,dest='validate', action='store_true', required=False, help='validates the warc against warc2zim')
    arg_parser.add_argument('--zim'         ,dest='zim', action='store_true', required=False, help='converts warc/big.warc into zim/big.zim')
    arg_parser.add_argument('--index'       ,dest='index', action='store_true', required=False, help='index warc')
    arg_parser.add_argument('--kiwix'       ,dest='kiwix', action='store_true', required=False, help='start kiwix server with zim/big.zim')
    arg_parser.add_argument('--symcreate'   ,dest='symcreate', action='store', default=None, type=valid_dir, required=False, help='create dir structure at a the given location and symlinks pointing there')
    arg_parser.add_argument('--symclear'    ,dest='symclear', action='store_true', default=None, required=False, help='clear symlinks')
    arg_parser.add_argument('--resource-links',dest='resource_links', action='store_true', default=None, required=False, help='extract links')
    arg_parser.add_argument('--resource-pdfs',dest='resource_pdfs', action='store_true', default=None, required=False, help='extract pdfs')
    arg_parser.add_argument('--find-missing',dest='find_missing', action='store_true', default=None, required=False, help='find missing resources')
    arg_parser.add_argument('--dump-warc-uris',dest='dump_warc_uris', action='store_true', default=None, required=False, help='list all uris stored in warc')

    VERSION="0.5.0"

    args = arg_parser.parse_args()

    if args.dump_warc_uris:
        os.system('''
        set -x
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/db:/home/user/db/:Z       \\
        wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./dump_warc_uris.sh' > warc_uris.txt
        '''.format(VERSION)
        )

    if args.find_missing:
        os.system('''
        set -x
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/db:/home/user/db/:Z       \\
        wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./warc_find_missing.sh' > missing.txt
        '''.format(VERSION)
        )

    if args.resource_links:
        os.system('''
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/db:/home/user/db/:Z       \\
        wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./v_warcindex/bin/python ./warc_resources.py --links --infile warc/big.warc'
        '''.format(VERSION)
        )
    if args.resource_pdfs:
        os.system('''
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/db:/home/user/db/:Z       \\
        wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./v_warcindex/bin/python ./warc_resources.py --pdfs --infile warc/big.warc'
        '''.format(VERSION)
        )
    if args.symcreate:
        # creates the dir structure at the given directory and
        # symlinks all the dirs back here
        os.system('''
        for x in  warc zim db log input; do
            rm -f $x
            mkdir -p {0}/$x 2>/dev/null
            ln    -s {0}/$x
        done
        '''.format(args.symcreate)
        )

    if args.symclear:
        os.system('''
        rm -f warc zim db log input
        '''
        )

    if args.attach:
        os.system('''
        mkdir log/ warc/ input/ 2>/dev/null
        id=$(docker ps | rg "femtocrawl" | head -1 | awk '{print $1}')
        docker exec -ti $id bash
        '''
        )
    if args.shell:
        os.system('''
        mkdir log/ warc/ input/ 2>/dev/null
        docker run --rm=true -ti               \\
            -v `pwd`/db:/home/user/db/:Z       \\
            -v `pwd`/log:/home/user/log/:Z     \\
            -v `pwd`/input:/home/user/input/:Z \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/zim:/home/user/zim/:Z   \\
            wsdookadr/femtocrawl:{0} bash
        '''.format(VERSION)
        )
    if args.clean:
        os.system('''
        rm -rf warc/*
        rm -rf zim/*
        rm -rf db/*
        '''
        )
    if args.crawl:
        os.system('''
        mkdir {2}
        docker run --rm=true -ti               \\
            -v `pwd`/log:/home/user/log/:Z \\
            -v `pwd`/input:/home/user/input/:Z \\
            -v `pwd`/{2}:/home/user/{2}/:Z   \\
            wsdookadr/femtocrawl:{0} './femtocrawl.py --batch-timeout 24 --url-list input/list_urls.txt --browser {1} --output-type {2}'
        '''.format(VERSION,args.browser,args.output_type)
        )
    if args.join:
        exc=""
        if args.exclude:
            exc="--exclude \"{0}\"".format(args.exclude)
        cmd='''
        rm -f warc/big.warc 2>/dev/null
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcio ./v_warcio/bin/python ./warc_join.py --indir warc/ --out warc/big.warc {1}'
        '''.format(VERSION,exc)
        os.system(cmd)
    if args.validate:
        os.system('''
        rm -f log/* 2>/dev/null
        mkdir log/ 2>/dev/null
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/log:/home/user/log/:Z     \\
            wsdookadr/femtocrawl:{0} './validate.sh'
        '''.format(VERSION)
        )
    if args.index:
        os.system('''
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/   \\
            -v `pwd`/db:/home/user/db/       \\
            wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./v_warcindex/bin/python ./warc_index.py --infile warc/big.warc --out db/big.db'
        '''.format(VERSION)
        )
    if args.zim:
        os.system('''
        rm -f zim/big.zim 2>/dev/null
        mkdir zim/ warc/ 2>/dev/null
        docker run --rm=true -ti                                \\
            -v `pwd`/warc:/home/user/warc/:Z                    \\
            -v `pwd`/zim:/home/user/zim/:Z                      \\
            wsdookadr/femtocrawl:{0}                            \\
            'env VIRTUAL_ENV=v_warc2zim ./v_warc2zim/bin/warc2zim --verbose --lang eng --output zim/ --zim-file big.zim --name "big" warc/big.warc'
        '''.format(VERSION)
        )
    if args.kiwix:
        os.system('''
        mkdir log/ 2>/dev/null
        echo "Access the ZIM archive at http://localhost:8083/"
        docker run --rm=true -ti             \\
            -p 8083:8083                     \\
            -v `pwd`/zim:/home/user/zim/:Z   \\
            wsdookadr/femtocrawl:{0} '/usr/bin/kiwix-serve -i 0.0.0.0 --threads 30 --port 8083 /home/user/zim/big.zim'
        '''.format(VERSION)
        )



