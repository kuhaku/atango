#!/bin/bash

# Lauch agents
plists=/work/atango/settings/*.plist
for plist in ${plists}
do
  ln -sf ${plist} ~/Library/LaunchAgents/
  filename=`basename ${plist}`
  launchctl load ~/Library/LaunchAgents/${filename}
  labelname=`echo ${filename} | sed -e "s/\./ /g" | awk '{$NF="";print $0}'`
  launchctl start ${labelname}
done


echo "export PYTHONPATH=/work/atango/lib:${PYTHONPATH}" >> /work/venv/atango/bin/activate
echo "source /work/venv/atango/bin/activate" >> ~/.profile
