#!/bin/bash
set -eu

QUIET=false

while getopts 'm:q:' OPTIONS
do
  case $OPTIONS in
  m) MESSAGE=${OPTARG};;
  q) QUIET=true;;
  esac
done

TMPWAVFILE=/tmp/out.wav
if [ -e ${TMPWAVFILE} ]; then
  rm ${TMPWAVFILE}
fi

echo "${MESSAGE}" | /usr/local/bin/nkf -w | /usr/local/bin/open_jtalk \
 -m /usr/local/share/openjtalk/nitech_jp_atr503_m001.htsvoice \
 -x /usr/local/lib/mecab/dic/ojt-naist-jdic \
 -ow ${TMPWAVFILE} \
 -r 0.93

if [ ${QUIET} != true ]; then
 afplay ${TMPWAVFILE}
fi
