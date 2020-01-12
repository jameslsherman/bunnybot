import requests
import yaml

from google.cloud import firestore
import google.cloud.exceptions

config = yaml.safe_load(open("config.yaml"))
slack = yaml.safe_load(open("slack.yaml"))

#-----------------------------------------------------------------------
def get_bunny_image():
    db = firestore.Client()

    images_ref = db.collection(u'images')
    query = images_ref.order_by('rabbit_cuteness',
                                direction=firestore.Query.DESCENDING).limit(10) #debug
    results = query.stream()

    for result in results:
        print(u'{} => {}'.format(result.id, result.to_dict()))
        print('\n')

    return result.to_dict()['username'], result.id


#-----------------------------------------------------------------------
def post_bunny_image(image_url):

    url = slack['webhook_url']
    headers = {"Content-type": "application/json"}
    json = (
        "{"
        "'blocks': "
        "[{"
        "'type': 'image', "
        "'title': {'type': 'plain_text','text': 'bunnybot','emoji': true}, "
        "'image_url': '" + image_url + "', "
        "'alt_text': 'bunnybot'"
        "}]"
        "}")

    print(url)
    print(json)

    r = requests.post(url, headers=headers, data=json)

    if r.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s' %
            (r.status_code, r.text))
    else:
        print('No errors')

    print(r.text)

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
username, image = get_bunny_image()
print(username)
print(image)

# image_url = "https://api.slack.com/img/blocks/bkb_template_images/beagle.png"
# image_url =  config['image_url'] + username + "/" + image + ".jpg"
image_url =  config['image_url'] + image + ".jpg"
# debug
# post_bunny_image(image_url)
