import csv
import datetime
import imagehash
import io
import ntpath
import os
import yaml

from PIL import Image
from time import sleep

# Imports the Google Cloud client library
from google.cloud import firestore
import google.cloud.exceptions

from google.cloud import storage

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

    load_image_into_memory(username, absolute_path)


#-----------------------------------------------------------------------
def load_image_into_memory(username, absolute_path):

    # Loads the image into memory
    with io.open(absolute_path, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)

        perform_label_detection(username, absolute_path, image)


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
        insert_annotations(username, absolute_path, image, annotations)

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

    data['hash'] = format(imagehash.phash(Image.open(absolute_path)))
    print('hash: {}'.format(data['hash']))
    is_identical = find_identical_hash(data['hash'])

    if sum_rabbit_cuteness > 0 and not (is_identical):
        data['rabbit_cuteness'] = sum_rabbit_cuteness
        doc_ref.set(data)
        upload_to_storage(config['bucket_name'], absolute_path,
                          username + '/' + document_name + '.jpg')
    # else:
    #     delete_from_db(document_name)
    #     delete_from_storage(config['bucket_name'], username + '/' + document_name + '.jpg')
    #     delete_local(absolute_path)

    # firestore: can only update a single document once per second
    # sleep(1)


#-----------------------------------------------------------------------
def find_identical_hash(hash):

    db = firestore.Client()
    docs = db.collection(u'images').where(u'hash', u'==',
                                          hash).limit(1).stream()

    is_identical = False
    for doc in docs:
        print('Identical hash {} => {}'.format(doc.id, doc.to_dict()['hash']))
        is_identical = True

    return is_identical


#-----------------------------------------------------------------------
def upload_to_storage(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name,
                                           destination_blob_name))


#-----------------------------------------------------------------------
def delete_from_db(document_name):

    try:
        db = firestore.Client()
        db.collection(u'images').document(document_name).delete()
        print("Document {} deleted in DB.".format(document_name))
    except:
        print('Document {} not found in DB.'.format(document_name))


#-----------------------------------------------------------------------
def delete_from_storage(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(blob_name)
        blob.delete()
        print("Document {} deleted in storage.".format(blob_name))
    except:
        print('Document {} not found in storage.'.format(blob_name))


#-----------------------------------------------------------------------
def delete_local(absolute_path):

    try:
        if os.path.exists(absolute_path):
            # TODO: Do not delete if only one file in directory
            os.remove(absolute_path)
            print("Document {} deleted locally.".format(absolute_path))
        else:
            print('Document {} not found locally.'.format(absolute_path))
    except:
        print('Document {} not found locally.'.format(absolute_path))


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
