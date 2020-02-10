# https://stackoverflow.com/questions/52736154/python-how-to-check-similarity-of-two-images-that-have-different-pixelization
# https://github.com/JohannesBuchner/imagehash
from PIL import Image
import imagehash
import itertools
import os
import yaml

from google.cloud import firestore
from google.cloud import storage
import google.cloud.exceptions

config = yaml.safe_load(open("config.yaml"))


#-----------------------------------------------------------------------
def main():

    image_filenames = find_exact_images()
    find_similar_images(image_filenames)


#-----------------------------------------------------------------------
def find_exact_images():

    files = os.listdir(config['upload_directory'] + '/')
    files.sort()

    image_filenames = {}
    for file in files:
        if file.endswith('.jpg'):
            # hash = imagehash.average_hash(Image.open(config['upload_directory'] + '/' + file))
            hash = imagehash.phash(Image.open(config['upload_directory'] + '/' + file))

            # delete exact matches
            if str(hash) in image_filenames:
                print('delete: {}'.format(file))
                username = get_username(file)
                delete_document(file)
                delete_from_storage(config['bucket_name'], username + '/' + file)
            else:
                print('unique: {}'.format(file))
                image_filenames[str(hash)] = file

    return image_filenames


#-----------------------------------------------------------------------
def find_similar_images(image_filenames):

    debug = 0
    for k1, k2 in itertools.combinations(sorted(image_filenames), 2):
        img1 = image_filenames[k1]
        img2 = image_filenames[k2]
        hash1 = imagehash.phash(Image.open(config['upload_directory'] + '/' + img1))
        hash2 = imagehash.phash(Image.open(config['upload_directory'] + '/' + img2))

        debug += 1
        # delete similar matches
        print('{} => hash2 - hash1: {}'.format(debug, hash2 - hash1))
        if (hash2 - hash1) < 10:
            print('delete: {}'.format(img1))
            username = get_username(img1)
            delete_document(img1)
            delete_from_storage(config['bucket_name'], username + '/' + img1)


#-----------------------------------------------------------------------
def get_username(file):

    # remove trailing .jpg to change image name to firestore document name
    document = os.path.splitext(file)[0]
    print(document)

    db = firestore.Client()
    doc_ref = db.collection(u'images').document(document)

    try:
        doc = doc_ref.get()
        username = doc.to_dict()['username']
        print('username: {}'.format(username))
    except:
        username = ''
        print('Unable to get username')

    return username


#-----------------------------------------------------------------------
def delete_document(file):

    # remove trailing .jpg to change image name to firestore document name
    document = os.path.splitext(file)[0]
    print(document)

    try:
        # db.collection('images').document(document).delete()
        print('Document {} deleted from DB'.format(document))
    except:
        print('Document not found in DB'.format(document))


#-----------------------------------------------------------------------
def delete_from_storage(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(blob_name)
        # blob.delete()
        print("Document {} deleted in storage.".format(blob_name))
    except:
        print('Document {} not found in storage.'.format(blob_name))


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
