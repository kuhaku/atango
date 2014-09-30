#!/bin/bash
set -eu

# Install MeCab with bug-fix patch
cd ${HOME}
curl -O https://mecab.googlecode.com/files/mecab-0.996.tar.gz
tar -zxvf mecab-0.996.tar.gz
curl -O https://gist.githubusercontent.com/kuhaku/f75597af0a282c6fada9/raw/fcf2eae9dd056e881d9b626bab4fa94a4d54a9e6/request_type.patch
cd ~/mecab-0.996
patch -u src/tagger.cpp < ../request_type.patch
./configure --enable-utf8-only
make
sudo make install

# Install MeCab IPA dictionary
cd ${HOME}
curl -O https://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz
tar -zxvf mecab-ipadic-2.7.0-20070801.tar.gz
cd ~/mecab-ipadic-2.7.0-20070801
./configure --with-charset=utf8
make
sudo make install
sudo chmod -R 777 /usr/local/lib/mecab

# Clean
cd ${HOME}
rm -r mecab-0.996 mecab-0.996.tar.gz request_type.patch mecab-ipadic-2.7.0-20070801 mecab-ipadic-2.7.0-20070801.tar.gz
