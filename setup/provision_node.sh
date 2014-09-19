#!/bin/bash

# Create virtualenv
virtualenv /work/venv/atango
. /work/venv/atango/bin/activate

# Install python libs from PyPI
wget --no-check-certificate https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
pip install --upgrade -r requirements.txt
rm requirements.txt

# Install Python-MeCab
MECAB_VERSION=`mecab-config --version`
pip install https://mecab.googlecode.com/files/mecab-python-${MECAB_VERSION}.tar.gz

# Clone Atango repository
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib:${PYTHONPATH} >> /work/venv/atango/bin/activate

# Configure matplotlib 
mkdir -p ~/.config/matplotlib/
echo backend : agg > ~/.config/matplotlib/matplotlibrc
