#!/bin/sh
# For cron

ATANGO_DIR=/work/atango
LANG="ja_JP.UTF-8"

# Activate Atango ENV
. /work/venv/atango/bin/activate

# Execute Atango Job
python ${ATANGO_DIR}/atango.py $@
