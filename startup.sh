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

while read b; do
  gsutil -m cp -r $b gs://bunnybot
done <bunnies.csv

while read b; do
  ls -td $b/* | tail -n +4 | xargs rm --;
done <bunnies.csv

# send to slack
# Upload latest slack.yaml file
gsutil cp gs://bunnybot_secret/*.yaml .
# python3 send_to_slack.py
python3 upload_to_slack.py
