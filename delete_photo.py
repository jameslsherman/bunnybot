import yaml

from google.cloud import storage
from google.cloud import firestore
import google.cloud.exceptions

config = yaml.safe_load(open("config.yaml"))

#-----------------------------------------------------------------------
def delete_photo(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))

#-----------------------------------------------------------------------
def get_bunny_image():
    db = firestore.Client()

    images_ref = db.collection(u'images')
    query = images_ref.where('rabbit_cuteness','<=',0)
    results = query.stream()

    for result in results:
        print(u'{} => {}'.format(result.id, result.to_dict()))
        print('\n')

    return result.to_dict()['username'], result.id

#-----------------------------------------------------------------------
# delete_photo(config['bucket_name'],'')
username, image = get_bunny_image()
print(username)
print(image)
