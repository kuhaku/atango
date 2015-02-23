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
curl -k -O https://raw.githubusercontent.com/kuhaku/atango/master/setup/mecab_install.sh
bash mecab_install.sh
rm mecab_install.sh

# Install Java7
brew tap phinze/homebrew-cask
brew install brew-cask
brew tap caskroom/versions
brew cask install java7

# Install Elasticsearch
brew install elasticsearch

# Install Redis
brew install redis

# Install Python libs
curl -k -O https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
pip install --upgrade --timeout 30 -r requirements.txt
rm requirements.txt

# Clone Atango repository
git clone https://github.com/kuhaku/atango.git /work/atango

# Install nginx
brew install nginx
cp /work/atango/settings/nginx.conf /usr/local/etc/nginx/nginx.conf

# Install open-jtalk
wget -O /usr/local/Library/Formula/open-jtalk.rb https://raw.githubusercontent.com/yawara/homebrew/open-jtalk/Library/Formula/open-jtalk.rb
brew install open-jtalk

# Install node.js for demo
brew install node

# Install iStats for CPU temperature monitor
gem install iStats
