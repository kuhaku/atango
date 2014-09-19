#!/bin/bash

sudo mkdir /work
sudo chmod 777 /work

# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install pip
sudo easy_install pip

# Install virtualenv
sudo pip install virtualenv
virtualenv /work/venv/atango
. /work/venv/atango/bin/activate

# Install Python libs
curl -O https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
sudo pip install --upgrade --timeout 30 -r requirements.txt
rm requirements.txt

# Install MeCab
brew install mecab mecab-ipadic
MECAB_VERSION=`mecab-config --version`
pip install https://mecab.googlecode.com/files/mecab-python-${MECAB_VERSION}.tar.gz

# Clone Atango repository
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib:${PYTHONPATH} >> /work/venv/atango/bin/activate
