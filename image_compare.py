# https://stackoverflow.com/questions/52736154/python-how-to-check-similarity-of-two-images-that-have-different-pixelization
# https://github.com/JohannesBuchner/imagehash
from PIL import Image
import imagehash
import os

hashdict = {}

hash1 = imagehash.average_hash(
    Image.open('bunny._lovers\\' +
               '67827520_513046826171714_3041859141216392522_n.jpg'))
hash2 = imagehash.average_hash(
    Image.open('bunny._lovers\\' +
               '68668200_1771975639614567_954201664778373999_n.jpg'))
print('hash1: {}'.format(hash1))
print('hash2: {}'.format(hash2))
print('hash2 - hash1: {}'.format(hash2 - hash1))

hashdict[str(hash1)] = hash1
print(hashdict)

hash1 = imagehash.phash(
    Image.open('bunny._lovers\\' +
               '67827520_513046826171714_3041859141216392522_n.jpg'))
hash2 = imagehash.phash(
    Image.open('bunny._lovers\\' +
               '68668200_1771975639614567_954201664778373999_n.jpg'))
print('hash1: {}'.format(hash1))
print('hash2: {}'.format(hash2))
print('hash2 - hash1: {}'.format(hash2 - hash1))

hashdict[str(hash1)] = hash1
print(hashdict)
exit()

hash1 = imagehash.dhash(
    Image.open('bunny._lovers\\' +
               '67827520_513046826171714_3041859141216392522_n.jpg'))
hash2 = imagehash.dhash(
    Image.open('bunny._lovers\\' +
               '68668200_1771975639614567_954201664778373999_n.jpg'))
print('hash1: {}'.format(hash1))
print('hash2: {}'.format(hash2))
print('hash2 - hash1: {}'.format(hash2 - hash1))

hash1 = imagehash.whash(
    Image.open('bunny._lovers\\' +
               '67827520_513046826171714_3041859141216392522_n.jpg'))
hash2 = imagehash.whash(
    Image.open('bunny._lovers\\' +
               '68668200_1771975639614567_954201664778373999_n.jpg'))
print('hash1: {}'.format(hash1))
print('hash2: {}'.format(hash2))
print('hash2 - hash1: {}'.format(hash2 - hash1))
