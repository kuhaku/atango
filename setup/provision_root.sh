#!/bin/bash

apt-get update

# Install things for building
apt-get install -y build-essential python3.4-dev python-pip

# Install virtualenv
pip install virtualenv

# Install scipy dependencies
apt-get install -y gfortran liblapack-dev libblas-dev

# Install matplotlib dependencies
apt-get install -y libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev

# Install git
apt-get install -y git

# Set Japan timezone
ln -sf /usr/share/zoneinfo/Japan /etc/localtime

# Install substitute fonts to use in WordMap job
apt-get install -y fonts-migmix

# Create work directory
mkdir /work
chmod 777 /work
