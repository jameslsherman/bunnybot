import google.cloud.exceptions
import imagehash
import os
import yaml

from google.cloud import firestore
from google.cloud import storage
from PIL import Image

config = yaml.safe_load(open("config.yaml"))

#-----------------------------------------------------------------------
def main():

    update_hash()


#-----------------------------------------------------------------------
def update_hash():

    db = firestore.Client()
    # docs = db.collection(u'images').where(u'hash', u'>', '').stream()
    docs = db.collection(u'images').stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))

        try:
            if doc.to_dict()['hash'] > '':
                print('do nothing')
            else:
                print('do something 1')
        except:
            print('do something 2')

            doc_ref = db.collection(u'images').document(doc.id)
            destination_file_name = os.path.abspath(doc.to_dict()['username'] + '/' + doc.id + '.jpg')
            try:
                doc_ref.set({'hash': format(imagehash.phash(Image.open(destination_file_name)))}, merge=True)
            except:
                source_blob_name = doc.to_dict()['username'] + '/' + doc.id + '.jpg'
                copy_to_local(config['bucket_name'], source_blob_name, destination_file_name)
                doc_ref.set({'hash': format(imagehash.phash(Image.open(destination_file_name)))}, merge=True)

        break

        # update doc
        # doc_ref = db.collection(u'images').document(doc.id)
        # doc_ref.set({'hash': sum_rabbit_cuteness}, merge=True)


#-----------------------------------------------------------------------
def copy_to_local(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print("Blob {} downloaded to {}.".format(source_blob_name,
                                             destination_file_name))


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
