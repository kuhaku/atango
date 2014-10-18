#!/bin/sh
# For cron

ATANGO_DIR=/work/atango

# Activate Atango ENV
. /work/venv/atango/bin/activate

PYTHONPATH=${ATANGO_DIR}:${PYTHONPATH}
LANG="ja_JP.UTF-8"

# Execute Atango Job
python ${ATANGO_DIR}/atango.py $@
