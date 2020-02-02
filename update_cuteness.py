import datetime

from google.cloud import firestore
import google.cloud.exceptions

#-----------------------------------------------------------------------
def main():

    db = firestore.Client()

    docs = db.collection(u'images').where(u'rabbit_cuteness', u'==', 0).stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
        sum_rabbit_cuteness = 0
        for key, value in doc.to_dict().items():
            if key == 'Rabbit' or key == 'Cuteness':
                sum_rabbit_cuteness += value
                print('sum_rabbit_cuteness: {}'.format(sum_rabbit_cuteness))

        # update doc
        doc_ref = db.collection(u'images').document(doc.id)
        doc_ref.set({'rabbit_cuteness': sum_rabbit_cuteness}, merge=True)

    # Posted Dttm
    docs = db.collection(u'images').where(u'posted_dttm', u'>',
                                          datetime.datetime(2000, 1, 1)).stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
        doc_ref = db.collection(u'images').document(doc.id)
        doc_ref.update({u'posted_dttm': firestore.DELETE_FIELD})

#-----------------------------------------------------------------------
if __name__ == "__main__":
    main()
