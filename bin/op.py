#!/usr/bin/env python3
import os
import re
import argparse

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='operator script for femtocrawl')
    arg_parser.add_argument('--shell'   ,dest='shell', action='store_true', required=False, help='starts the container and provides a shell')
    arg_parser.add_argument('--clean'   ,dest='clean', action='store_true', required=False, help='cleans any data from previous crawls')
    arg_parser.add_argument('--crawl'   ,dest='crawl', action='store_true', required=False, help='runs docker on default input file')
    arg_parser.add_argument('--join'    ,dest='join', action='store_true'  , required=False, help='joins all warc into a single warc(prep for zim conversion)')
    arg_parser.add_argument('--validate',dest='validate', action='store_true', required=False, help='validates the warc against warc2zim')
    arg_parser.add_argument('--zim'     ,dest='zim', action='store_true', required=False, help='converts warc/big.warc into zim/big.zim')
    arg_parser.add_argument('--index'   ,dest='index', action='store_true', required=False, help='index warc')
    arg_parser.add_argument('--kiwix'   ,dest='kiwix', action='store_true', required=False, help='start kiwix server with zim/big.zim')

    args = arg_parser.parse_args()

    if args.shell:
        os.system('''
        mkdir log/ warc/ input/ 2>/dev/null
        docker run -ti                         \\
            -v `pwd`/log:/home/user/log/:Z \\
            -v `pwd`/input:/home/user/input/:Z \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:0.2 bash
        '''
        )
    if args.clean:
        os.system('''
        rm -rf warc/*
        rm -rf zim/*
        '''
        )
    if args.crawl:
        os.system('''
        docker run -ti                         \\
            -v `pwd`/input:/home/user/input/:Z \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:0.2 './femtocrawl.sh input/list_urls.txt'
        '''
        )
    if args.join:
        os.system('''
        docker run -ti                         \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            wsdookadr/femtocrawl:0.2 'env VIRTUAL_ENV=v_warcio ./v_warcio/bin/python ./warc_join.py --indir warc/ --out warc/big.warc'
        '''
        )
    if args.validate:
        os.system('''
        mkdir log/ 2>/dev/null
        docker run -ti                         \\
            -v `pwd`/warc:/home/user/warc/:Z   \\
            -v `pwd`/log:/home/user/log/:Z     \\
            wsdookadr/femtocrawl:0.2 './validate.sh'
        '''
        )
    if args.zim:
        os.system('''
        set -x
        mkdir zim/ warc/ 2>/dev/null
        docker run -ti                                          \\
            -v `pwd`/warc:/home/user/warc/:Z                    \\
            -v `pwd`/zim:/home/user/zim/:Z                      \\
            wsdookadr/femtocrawl:0.2                            \\
            'env VIRTUAL_ENV=v_warc2zim ./v_warc2zim/bin/warc2zim --verbose --lang eng --output zim/ --zim-file big.zim --name "big" warc/big.warc'
        '''
        )
    if args.kiwix:
        os.system('''
        mkdir log/ 2>/dev/null
        echo "Access the ZIM archive at http://localhost:8083/"
        docker run -ti                       \\
            -p 8083:8083             \\
            -v `pwd`/zim:/home/user/zim/:Z   \\
            wsdookadr/femtocrawl:0.2 '/usr/bin/kiwix-serve -i 0.0.0.0 --threads 30 --port 8083 /home/user/zim/big.zim'
        '''
        )



