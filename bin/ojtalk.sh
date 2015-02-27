#!/bin/bash
set -eu

# parse argument
QUIET=false

while getopts 'm:q:' OPTIONS
do
  case $OPTIONS in
  m) MESSAGE=${OPTARG};;
  q) QUIET=true;;
  esac
done

# initialize output file
TMPWAVFILE=/tmp/out.wav
if [ -e ${TMPWAVFILE} ]; then
  rm ${TMPWAVFILE}
fi

# speech synthesis
counter=0
for sentence in `echo ${MESSAGE} | tr -s '' ' '`; do
  tmpwavfile="/tmp/tmp${counter}.wav"
  echo "${sentence}" | /usr/local/bin/nkf -w | /usr/local/bin/open_jtalk \
   -m /usr/local/share/openjtalk/nitech_jp_atr503_m001.htsvoice \
   -x /usr/local/lib/mecab/dic/ojt-naist-jdic \
   -ow ${tmpwavfile} \
   -r 0.93
  counter=$(($counter + 1))
done

# concat wavs
if [ $counter -gt 1 ];then
  /usr/local/bin/ffmpeg -f concat \
                        -i <(for f in /tmp/tmp*.wav; do echo "file '$f'"; done)\
                        -c copy ${TMPWAVFILE} >& /dev/null
else
  cp ${tmpwavfile} ${TMPWAVFILE}
fi

rm /tmp/tmp*.wav

# if not quiet, play
if [ ${QUIET} != true ]; then
 afplay ${TMPWAVFILE}
fi
