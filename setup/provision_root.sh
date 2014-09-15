#!/bin/sh
apt-get update

apt-get install -y build-essential python-dev python-pip
apt-get install -y gfortran liblapack-dev libblas-dev
apt-get install -y libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

wget --no-check-certificate https://raw.githubusercontent.com/kuhaku/atango/master/requirements.txt
pip install --upgrade -r requirements.txt
rm requirements.txt

apt-get install -y mecab-ipadic-utf8 python-mecab
apt-get install -y mecab

apt-get install -y git
mkdir -p /work
chmod 777 /work

ln -sf /usr/share/zoneinfo/Japan /etc/localtime

# Install substitute fonts to use in WordMap job
apt-get install fonts-migmix
