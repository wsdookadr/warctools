#!/usr/bin/env python3
import os
import re
import argparse

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='operator script for femtocrawl')
    arg_parser.add_argument('--shell'   ,dest='shell', action='store_true', required=False, help='starts the container and provides a shell')
    arg_parser.add_argument('--attach'   ,dest='attach', action='store_true', required=False, help='attach to first femtocrawl container found')
    arg_parser.add_argument('--clean'   ,dest='clean', action='store_true', required=False, help='cleans any data from previous crawls')
    arg_parser.add_argument('--crawl'   ,dest='crawl', action='store_true', required=False, help='runs docker on default input file')
    arg_parser.add_argument('--join'    ,dest='join', action='store_true'  , required=False, help='joins all warc into a single warc(prep for zim conversion)')
    arg_parser.add_argument('--validate',dest='validate', action='store_true', required=False, help='validates the warc against warc2zim')
    arg_parser.add_argument('--zim'     ,dest='zim', action='store_true', required=False, help='converts warc/big.warc into zim/big.zim')
    arg_parser.add_argument('--index'   ,dest='index', action='store_true', required=False, help='index warc')
    arg_parser.add_argument('--kiwix'   ,dest='kiwix', action='store_true', required=False, help='start kiwix server with zim/big.zim')

    TAG="0.3.1"

    args = arg_parser.parse_args()
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
            wsdookadr/femtocrawl:{0} bash
        '''.format(TAG)
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
        docker run --rm=true -ti               \\
            -v `pwd`/input:/home/user/input/:Z \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:{0} './femtocrawl.sh input/list_urls.txt'
        '''.format(TAG)
        )
    if args.join:
        os.system('''
        rm -f warc/big.warc 2>/dev/null
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcio ./v_warcio/bin/python ./warc_join.py --indir warc/ --out warc/big.warc'
        '''.format(TAG)
        )
    if args.validate:
        os.system('''
        rm -f log/* 2>/dev/null
        mkdir log/ 2>/dev/null
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/log:/home/user/log/:Z     \\
            wsdookadr/femtocrawl:{0} './validate.sh'
        '''.format(TAG)
        )
    if args.index:
        os.system('''
        rm -f db/big.db
        docker run --rm=true -ti               \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/db:/home/user/db/:Z       \\
            wsdookadr/femtocrawl:{0} 'env VIRTUAL_ENV=v_warcindex ./v_warcindex/bin/python ./warc_index.py --infile warc/big.warc --out db/big.db'
        '''.format(TAG)
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
        '''.format(TAG)
        )
    if args.kiwix:
        os.system('''
        mkdir log/ 2>/dev/null
        echo "Access the ZIM archive at http://localhost:8083/"
        docker run --rm=true -ti             \\
            -p 8083:8083                     \\
            -v `pwd`/zim:/home/user/zim/:Z   \\
            wsdookadr/femtocrawl:{0} '/usr/bin/kiwix-serve -i 0.0.0.0 --threads 30 --port 8083 /home/user/zim/big.zim'
        '''.format(TAG)
        )



