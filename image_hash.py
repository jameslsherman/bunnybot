# https://stackoverflow.com/questions/52736154/python-how-to-check-similarity-of-two-images-that-have-different-pixelization
# https://github.com/JohannesBuchner/imagehash
from PIL import Image
import imagehash
import os
import yaml

from google.cloud import firestore
from google.cloud import storage
import google.cloud.exceptions

config = yaml.safe_load(open("config.yaml"))


#-----------------------------------------------------------------------
def main():

    unique_files = scan_directory_for_images()

    prev_file = ''
    for key in sorted(unique_files):
        # print('key value: {} {}'.format(key,unique_files[key]))
        if prev_file:
            hash1 = imagehash.phash(Image.open('louisaandbenny\\' + prev_file))
            hash2 = imagehash.phash(
                Image.open('louisaandbenny\\' + unique_files[key]))
            # print('hash2 - hash1: {}'.format(hash2 - hash1))
            # delete near matches
            if (hash2 - hash1) < 5:
                delete_document(unique_files[key])
                delete_from_storage(unique_files[key])

        prev_file = unique_files[key]


#-----------------------------------------------------------------------
def scan_directory_for_images():

    # only check one username/directory
    files = os.listdir('louisaandbenny\\')
    files.sort()

    unique_files = {}
    for file in files:
        if file.endswith('.jpg'):
            # hash = imagehash.average_hash(Image.open('louisaandbenny\\' + file))
            hash = imagehash.phash(Image.open('louisaandbenny\\' + file))
            # delete exact matches
            if str(hash) in unique_files:
                print('delete: {}'.format(file))
                delete_document(file)
                delete_from_storage(file)
            else:
                print('unique: {}'.format(file))
                unique_files[str(hash)] = file

    return unique_files


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

    # hardcoded subdirectory, since all dups are from same user - louisaandbenny
    blob = bucket.blob('louisaandbenny/' + file)
    try:
        blob.delete()
    except:
        print('File not found')

    print("Blob {} deleted.".format(file))


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
