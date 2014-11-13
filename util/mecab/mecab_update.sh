#!/bin/sh
set -e

ATANGO_DIR=/work/atango
SCRIPT_DIR=${ATANGO_DIR}/util/mecab

# Activate Atango ENV
. /work/venv/atango/bin/activate

PYTHONPATH=${ATANGO_DIR}:${PYTHONPATH}

OLD_PWD=`pwd`

DICDIR=`mecab-config --dicdir`
ORIGINAL_DICDIR="${DICDIR}/original"
STORE_DICDIR="${DICDIR}/normalized"

MECAB_LIBEXEC_DIR=`mecab-config --libexecdir`

# Retrieve neologism from Syobocal, Wikipedia, Hatena Keyword and more
python ${SCRIPT_DIR}/web_neologism.py ${ORIGINAL_DICDIR}

rm ${STORE_DICDIR}/*
cp ${ORIGINAL_DICDIR}/*.def ${STORE_DICDIR}
cp ${ORIGINAL_DICDIR}/dicrc ${STORE_DICDIR}

cp ${ORIGINAL_DICDIR}/ipadic.csv ${STORE_DICDIR}
python ${SCRIPT_DIR}/split_csv_each_length.py ${ORIGINAL_DICDIR} ${STORE_DICDIR} "*.csv"
python ${SCRIPT_DIR}/normalize_cost.py ${ORIGINAL_DICDIR}/ipadic.csv ${STORE_DICDIR}/1.temp
${MECAB_LIBEXEC_DIR}/mecab-dict-index -d ${STORE_DICDIR} -o ${STORE_DICDIR} -f utf-8 -t utf-8 >> /dev/null
rm ${STORE_DICDIR}/1.temp

for i in {2..100}
do
  TMPFILE=${STORE_DICDIR}/${i}.temp
  if [ -e ${TMPFILE} ]; then
    python ${SCRIPT_DIR}/update_cost.py ${TMPFILE} ${STORE_DICDIR}
    ${MECAB_LIBEXEC_DIR}/mecab-dict-index -d ${STORE_DICDIR} -o ${STORE_DICDIR} -f utf-8 -t utf-8 >> /dev/null
    rm ${TMPFILE}
  fi
done
