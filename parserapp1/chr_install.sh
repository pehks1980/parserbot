#!/bin/sh
echo 'install chomedriver to local venv... '
PLATFORM=linux64
#change number at the end according to chromium version this is important!
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE_84)
wget http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip
unzip -d venv/bin chromedriver_$PLATFORM.zip
echo 'install complete please make sudo chmod a+x to that chromedriver'
