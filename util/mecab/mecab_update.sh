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
TMP_DICDIR="/tmp/tempdic"
STORE_DICDIR="${DICDIR}/normalized"

MECAB_LIBEXEC_DIR=`mecab-config --libexecdir`

# Retrieve neologism from Syobocal, Wikipedia, Hatena Keyword and more
#python ${SCRIPT_DIR}/web_neologism.py ${ORIGINAL_DICDIR}

rm -rf ${TMP_DICDIR}
mkdir ${TMP_DICDIR}
cp ${ORIGINAL_DICDIR}/*.def ${TMP_DICDIR}
cp ${ORIGINAL_DICDIR}/dicrc ${TMP_DICDIR}

cp ${ORIGINAL_DICDIR}/ipadic.csv ${TMP_DICDIR}
python ${SCRIPT_DIR}/split_csv_each_length.py ${ORIGINAL_DICDIR} ${TMP_DICDIR} "*.csv"
python ${SCRIPT_DIR}/normalize_cost.py ${ORIGINAL_DICDIR}/ipadic.csv ${TMP_DICDIR}/1.temp
${MECAB_LIBEXEC_DIR}/mecab-dict-index -d ${TMP_DICDIR} -o ${TMP_DICDIR} -f utf-8 -t utf-8 >> /dev/null
rm ${TMP_DICDIR}/1.temp

for i in {2..20}
do
  TMPFILE=${TMP_DICDIR}/${i}.temp
  if [ -e ${TMPFILE} ]; then
    python ${SCRIPT_DIR}/update_cost.py ${TMPFILE} ${TMP_DICDIR}
    ${MECAB_LIBEXEC_DIR}/mecab-dict-index -d ${TMP_DICDIR} -o ${TMP_DICDIR} -f utf-8 -t utf-8 >> /dev/null
    rm ${TMPFILE}
  fi
done

if [ -e ${STORE_DICDIR} ];
then
    rm -r ${STORE_DICDIR}
fi

mv ${TMP_DICDIR} ${STORE_DICDIR}
rm ${STORE_DICDIR}/*.csv ${STORE_DICDIR}/*.temp ${TMP_DICDIR}/*.temp
