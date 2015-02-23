#!/bin/bash
# For cron

ATANGO_DIR=/work/atango

# Activate Atango ENV
. /work/venv/atango/bin/activate

PYTHONPATH=${ATANGO_DIR}:${PYTHONPATH}
PATH=/usr/sbin:${PATH}
LANG="ja_JP.UTF-8"

# Execute Atango Job
python ${ATANGO_DIR}/atango.py $@
