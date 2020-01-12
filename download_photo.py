import csv
import subprocess
import time
import yaml

from random import randint
from time import sleep

# hardcoded values
config = yaml.safe_load(open("config.yaml"))


#-----------------------------------------------------------------------
def main():

    # CSV file containing Instagram usernames
    with open(config['csvfile']) as csvfile:
        reader = csv.DictReader(csvfile)

        # skip header
        # next(reader, None)
        for row in reader:
            # Instagram username
            username = row['username']
            print(username)

            download_images(username)


#-----------------------------------------------------------------------
def download_images(username):

    # https://github.com/rarcega/instagram-scraper
    # Scrapes an instagram user's photos and videos
    # pip install instagram-scraper
    p = subprocess.Popen(
        ["instagram-scraper", username, "--media-types", "image", "--latest"],
        stdout=subprocess.PIPE)

    output, err = p.communicate()
    if output != "":
        print(output)
    sleep(randint(10, 30))


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
