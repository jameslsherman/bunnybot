import ntpath
import yaml

from google.cloud import firestore
from google.cloud import storage

# hardcoded values
config = yaml.safe_load(open("config.yaml"))

#-----------------------------------------------------------------------
def main():

    list_docs()
    # list_blobs(config['bucket_name'])

#-----------------------------------------------------------------------
def list_docs():

    db = firestore.Client()

    docs = db.collection('images').where(u'hash', u'>', '').stream()  # 1100
    # docs = db.collection('images').where(u'rabbit_cuteness', u'>', 0).stream()  # 1082
    # docs = db.collection('images').where(u'rabbit_cuteness', u'==', 0).stream()  # 18
    # docs = db.collection('images').where(u'username', u'>', '').stream()  # 1100

    # db.collection(u'images').document(u'32824402_1034460390047593_7552867768618450944_n').delete()
    # db.collection(u'images').document(u'36981782_1981859065459485_5165202591579111424_n').delete()

    debug = 1
    for doc in docs:
        print(u'{} => {}'.format(debug, doc.id))
        debug += 1


#-----------------------------------------------------------------------
def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    debug = 1
    for blob in blobs:
        print(u'{} => {}'.format(debug, blob.name))
        doc_id = ntpath.basename(blob.name[:-4])
        is_exists = get_check_exists(doc_id, blob.name)
        if not is_exists:
            break
        debug += 1


#-----------------------------------------------------------------------
def get_check_exists(doc_id, blob_name):

    db = firestore.Client()
    doc_ref = db.collection(u'images').document(doc_id)

    try:
        doc = doc_ref.get()
        try:
            print(u'True: {}'.format(doc.to_dict()['hash']))
        except:
            copy_to_local(config['bucket_name'], blob_name, blob_name)
        # 66357651_175000876869605_8884614957564441290_n.jpg
        return True
    except google.cloud.exceptions.NotFound:
        print(u'False: {}'.format(doc_id))
        return False


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
