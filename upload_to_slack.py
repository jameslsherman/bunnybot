import datetime
import os.path
import requests
import yaml

from google.cloud import firestore
import google.cloud.exceptions

from google.cloud import storage

# hardcoded values
config = yaml.safe_load(open("config.yaml"))
slack = yaml.safe_load(open("slack.yaml"))


#-----------------------------------------------------------------------
def main():

    username, image = get_image()
    print(username)
    print(image)

    post_image(username, image)


#-----------------------------------------------------------------------
def get_image():

    db = firestore.Client()

    images_ref = db.collection(u'images')
    # get highest ranking value
    query = images_ref.order_by('rabbit_cuteness',
                                direction=firestore.Query.DESCENDING).limit(1)
    results = query.stream()

    for result in results:
        print(u'{} => {}'.format(result.id, result.to_dict()))
        print('\n')
        # begin add api
        source_blob_name = result.to_dict()['username'] + '/' + result.id + '.jpg'
        destination_file_name = source_blob_name
        copy_to_local(config['bucket_name'], source_blob_name, destination_file_name)
        # end add api

    return result.to_dict()['username'], result.id


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

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


#-----------------------------------------------------------------------
def post_image(username, image):

    image_location = username + '/' + image + '.jpg'

    url = slack['api_url'] + 'files.upload'
    headers = {'Authorization': 'Bearer ' + slack['oauth_access_token']}
    files = {
        'file': (image_location, open(image_location, 'rb')),
        'initial_comment': (None, 'From bunnybot'),
        'channels': (None, slack['channels']),
    }

    r = requests.post(url, headers=headers, files=files)

    if r.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s' %
            (r.status_code, r.text))
    else:
        print('No errors')
        update_rabbit_cuteness(image)

    print(r.text)


#-----------------------------------------------------------------------
def update_rabbit_cuteness(image):

    db = firestore.Client()
    doc_ref = db.collection(u'images').document(image)

    # add new field with timestamp
    data = {u'posted_dttm': datetime.datetime.now()}
    # update value to keep from getting reselected
    data['rabbit_cuteness'] = 0

    # merge=true to add to existing document and not overwrite
    doc_ref.set(data, merge=True)


#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
