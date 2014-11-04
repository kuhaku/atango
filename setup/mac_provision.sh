#!/bin/bash

sudo mkdir /work
sudo chmod 777 /work

# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install 3
brew install python3

# Install virtualenv
sudo pip3 install virtualenv
virtualenv -p python3 /work/venv/atango
. /work/venv/atango/bin/activate

# Install MeCab
curl -O https://raw.githubusercontent.com/kuhaku/atango/master/setup/mecab_install.sh
bash mecab_install.sh
rm mecab_install.sh

# Install Python libs
curl -O https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
pip install --upgrade --timeout 30 -r requirements.txt
rm requirements.txt

# Install iStats for CPU temperature monitor
gem install iStats

# Clone Atango repository
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib:${PYTHONPATH} >> /work/venv/atango/bin/activate
