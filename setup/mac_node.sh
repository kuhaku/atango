#!/bin/bash

# Lauch agents
plists=/work/atango/settings/*.plist
for plist in ${plists}
do
  ln -f ${plist} ~/Library/LaunchAgents/
  filename=`basename ${plist}`
  launchctl load ~/Library/LaunchAgents/${filename}
done


echo "export PYTHONPATH=/work/atango/lib:${PYTHONPATH}" >> /work/venv/atango/bin/activate
echo "source /work/venv/atango/bin/activate" >> ~/.profile
