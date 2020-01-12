import requests
import yaml

from google.cloud import firestore
import google.cloud.exceptions

# hardcoded values
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

    return result.to_dict()['username'], result.id

#-----------------------------------------------------------------------
def post_image(username, image):

    image_location = username + '/' + image + ".jpg"

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
