#!/bin/bash
rm -f warc/*
find /home/nas/archivebox/batches/ -name "*.warc.gz" -maxdepth 4 | perl -ne 'chomp; $n++; $cmd="zcat $_ > ~/femtocrawl/warc/$n.warc"; print "$cmd\n"; `$cmd` ; '
