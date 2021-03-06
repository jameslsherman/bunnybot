import google.cloud.exceptions
import imagehash
import os
import pathlib
import yaml

from google.cloud import firestore
from google.cloud import storage
from PIL import Image
from time import sleep

config = yaml.safe_load(open("config.yaml"))


#-----------------------------------------------------------------------
def main():

    update_hash()


#-----------------------------------------------------------------------
def update_hash():

    debug = 0

    db = firestore.Client()
    docs = db.collection(u'images').stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))

        try:
            if doc.to_dict()['hash'] > '':
                print('do nothing')
        except:
            print('do something')

            doc_ref = db.collection(u'images').document(doc.id)
            destination_file_name = os.path.abspath(doc.to_dict()['username'] +
                                                    '/' + doc.id + '.jpg')
            if pathlib.Path(destination_file_name).exists():
                hash = format(
                    imagehash.phash(Image.open(destination_file_name)))
                doc_ref.set({'hash': hash}, merge=True)
                # firestore: can only update a single document once per second
                sleep(1)
            else:
                source_blob_name = doc.to_dict(
                )['username'] + '/' + doc.id + '.jpg'
                is_copied = copy_to_local(config['bucket_name'],
                                          source_blob_name,
                                          destination_file_name)
                if is_copied:
                    hash = format(
                        imagehash.phash(Image.open(destination_file_name)))
                    doc_ref.set({'hash': hash}, merge=True)
                    # firestore: can only update a single document once per second
                    sleep(1)

        # if debug == 2:
        #     break
        # else:
        #     debug += 1


#-----------------------------------------------------------------------
def copy_to_local(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    if blob.exists():
        blob.download_to_filename(destination_file_name)
        print("Blob {} downloaded to {}.".format(source_blob_name,
                                                 destination_file_name))
        return True
    else:
        print('Blob {} does not exist.'.format(source_blob_name))
        return False


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
