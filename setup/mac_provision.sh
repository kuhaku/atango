#!/bin/bash

# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install pip
sudo easy_install pip

# Install dependencies
curl -O https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
sudo pip install --upgrade --timeout 30 -r requirements.txt
rm requirements.txt

# Install MeCab
brew install mecab mecab-ipadic
sudo easy_install https://mecab.googlecode.com/files/mecab-python-0.996.tar.gz

# Clone Atango repository
sudo mkdir -p /work
sudo chmod 777 /work
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib >> ~/.bashrc
