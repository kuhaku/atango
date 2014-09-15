#!/bin/sh
git clone https://github.com/kuhaku/atango.git /work/atango
echo export PYTHONPATH=/work/atango/lib >> ~/.bashrc

mkdir -p ~/.config/matplotlib/
echo backend : agg > ~/.config/matplotlib/matplotlibrc
