# import fnmatch
import os

from google.cloud import firestore
from google.cloud import storage
import google.cloud.exceptions

config = yaml.safe_load(open("config.yaml"))

#-----------------------------------------------------------------------
def scan_directory_for_images():

    # after moving duplicate images to own 'dups' directory
    files = os.listdir('dups\\')
    files.sort()

    for file in files:
        # if fnmatch.fnmatch(file, '*.jpg'):
        if file.endswith('.jpg'):
            # print('delete: {}'.format(file))
            delete_document(file)
            delete_from_storage(file)

#-----------------------------------------------------------------------
def delete_document(file):

    # remove trailing .jpg to change image name to firestore document name
    document = os.path.splitext(file)[0]
    print(document)

    db = firestore.Client()
    try:
        db.collection(u'images').document(document).delete()
        print('Document deleted')
    except:
        print('Document not found')

#-----------------------------------------------------------------------
def delete_from_storage(file):

    storage_client = storage.Client()

    bucket = storage_client.bucket(config['bucket_name'])

    # hardcoded subdirectory, since all dups are from same user - bunny._lovers
    blob = bucket.blob('bunny._lovers/' + file)
    try:
        blob.delete()
    except:
        print('File not found')

    print("Blob {} deleted.".format(file))

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
scan_directory_for_images()
