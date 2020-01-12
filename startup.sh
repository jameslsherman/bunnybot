#!/bin/bash
git clone https://github.com/jameslsherman/bunnybot temp
mv temp/* bunnybot/
rm -fr temp
cd bunnybot/
sudo apt -y update
sudo apt -y install python3-pip
pip3 install -r requirements.txt

# yapf <- yet another python formater
# yapf -i label_photo.py

# Download images
python3 download_photo.py  #sleeps every 10 to 30 seconds between usernames
find . -name '*.mp4' -type f -delete

# Windows:
# set GOOGLE_APPLICATION_CREDENTIALS=c:\Users\james_000\Downloads\ballet-sql-cf0326ef163c.json

# Label images
python3 label_photo.py

# while read b; do
#  gsutil -m cp -r $b gs://bunnybot
#  cd $b'/'
#  ls -t | tail -n +4 | xargs rm --
#  cd ..
# done <bunnies.csv

# repeat for all directories
gsutil -m cp -r louisaandbenny gs://bunnybot
cd louisaandbenny/
ls -t | tail -n +4 | xargs rm --
cd ..

gsutil -m cp -r cukipukii gs://bunnybot
cd cukipukii/
ls -t | tail -n +4 | xargs rm --
cd ..

gsutil -m cp -r bunny._lovers gs://bunnybot
cd bunny._lovers
ls -t | tail -n +4 | xargs rm --
cd ..

# send to slack
# Upload latest slack.yaml file
gsutil cp gs://bunnybot_secret/*.yaml .
python3 send_to_slack.py
