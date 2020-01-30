import csv
import datetime
import io
import ntpath
import os
import yaml

from time import sleep

# Imports the Google Cloud client library
from google.cloud import firestore
import google.cloud.exceptions

from google.cloud import vision
from google.cloud.vision import types

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

            scan_directory_for_images(username)


#-----------------------------------------------------------------------
def scan_directory_for_images(username):

    files = os.listdir(username + '/')
    files.sort()

    for file in files:
        print('file: {}'.format(file))

        if file.endswith('.jpg'):
            get_images(username, file)


#-----------------------------------------------------------------------
def get_images(username, file):

    absolute_path = os.path.abspath(username + '/' + file)
    print('absolute_path: {}'.format(absolute_path))

    is_inserted = load_image_into_memory(username, absolute_path)

    if not is_inserted:
        # delete file, if not labeled as rabbit
        os.remove(absolute_path)
    else:
        # TODO: move to bucket storage
        print('move')
        # TODO: remove if not newest image


#-----------------------------------------------------------------------
def load_image_into_memory(username, absolute_path):

    # Loads the image into memory
    with io.open(absolute_path, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)

        return perform_label_detection(username, absolute_path, image)


#-----------------------------------------------------------------------
def perform_label_detection(username, absolute_path, image):

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations
    print_labels(labels)

    # Performs web detection on the image file
    response = client.web_detection(image=image)
    annotations = response.web_detection
    if annotations.web_entities:
        print_annotations(annotations)
        # What if no web_entities?
        return insert_annotations(username, absolute_path, image, annotations)

    # exit()  # debug


#-----------------------------------------------------------------------
def print_labels(labels):

    print('Labels:')
    for label in labels:
        print(label.description + ' ' + str(label.score))


#-----------------------------------------------------------------------
def print_annotations(annotations):

    print('\n{} Web entities found: '.format(len(annotations.web_entities)))

    for entity in annotations.web_entities:
        print('\n\tScore      : {}'.format(entity.score))
        print(u'\tDescription: {}'.format(entity.description))


#-----------------------------------------------------------------------
def insert_annotations(username, absolute_path, image, annotations):

    db = firestore.Client()
    # remove directory and '.jpg' from absolute_path
    document_name = ntpath.basename(absolute_path[:-4])
    doc_ref = db.collection(u'images').document(document_name)

    data = {u'username': username, u'entered_dttm': datetime.datetime.now()}

    sum_rabbit_cuteness = 0
    for entity in annotations.web_entities:
        if entity.description:
            data[entity.description] = entity.score
            # add score to sum
            if entity.description == 'Rabbit' or entity.description == 'Cuteness':
                sum_rabbit_cuteness += entity.score

    if sum_rabbit_cuteness > 0:
        data['rabbit_cuteness'] = sum_rabbit_cuteness
        data['hash'] = imagehash.phash(Image.open(absolute_path))   # add hash
        doc_ref.set(data)
        is_inserted = True
    else:
        try:
            # delete documents inserted during testing
            db.collection(u'images').document(document_name).delete()
        except:
            print('Document not found')
        is_inserted = False

    return is_inserted
    # firestore: can only update a single document once per second
    # sleep(1)


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
