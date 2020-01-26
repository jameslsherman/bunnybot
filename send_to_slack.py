import datetime
import requests
import socket
import subprocess
import yaml

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from google.cloud import firestore
import google.cloud.exceptions

# hardcoded values
config = yaml.safe_load(open("config.yaml"))
slack = yaml.safe_load(open("slack.yaml"))


#-----------------------------------------------------------------------
def main():

    username, image = get_image()
    print(username)
    print(image)

    post_image(image)


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
        copy_to_webserver(result.to_dict()['username'], result.id)

    return result.to_dict()['username'], result.id


#-----------------------------------------------------------------------
def copy_to_webserver(username, image):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not s.connect((config['external_ip'], 80)):
        bash_command = 'sudo gsutil cp gs://' + config[
            'bucket_name'] + '/' + username + '/' + image + '.jpg /var/www/html/. '
        print(u'bash_command: {}'.format(bash_command))

        process = subprocess.Popen(bash_command.split(),
                                   stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(u'output: {}'.format(output))
        print(u'error: {}'.format(error))
    else:
        print("Could not connect to web server")


#-----------------------------------------------------------------------
def post_image(image):

    url = slack['webhook_url']
    headers = {"Content-type": "application/json"}
    json = (
        "{"
        "'blocks': "
        "[{"
        "'type': 'image', "
        "'title': {'type': 'plain_text','text': 'bunnybot','emoji': true}, "
        "'image_url': '" + config['image_url'] + image + ".jpg', "
        "'alt_text': 'bunnybot'"
        "}]"
        "}")

    print(url)
    print(json)

    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=1,
                    status_forcelist=[502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))

    # r = requests.post(url, headers=headers, data=json, timeout=5)
    r = s.post(url, headers=headers, data=json, timeout=5)

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
