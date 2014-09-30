#!/bin/bash

# Create virtualenv
virtualenv /work/venv/atango
. /work/venv/atango/bin/activate

# Install python libs from PyPI
wget --no-check-certificate https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
pip install --upgrade -r requirements.txt
rm requirements.txt

# Clone Atango repository
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib:${PYTHONPATH} >> /work/venv/atango/bin/activate
