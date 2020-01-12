# import fnmatch
import hashlib
import ntpath
import os
import subprocess
import sys

#-----------------------------------------------------------------------
def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


#-----------------------------------------------------------------------
def check_for_duplicates(paths, hash=hashlib.sha1):
    hashes = {}
    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                # if fnmatch.fnmatch(filename, '*.jpg'):
                if file.endswith('.jpg'):
                    full_path = os.path.join(dirpath, filename)
                    hashobj = hash()
                    for chunk in chunk_reader(open(full_path, 'rb')):
                        hashobj.update(chunk)
                    file_id = (hashobj.digest(), os.path.getsize(full_path))
                    duplicate = hashes.get(file_id, None)

                    if duplicate and full_path != duplicate:
                        print("Duplicate found: {} and {}".format(
                            full_path, duplicate))

                        # start rename duplicates
                        old_name = 'C:\\Temp\\www\\bunnybot\\bunnybot\\' + duplicate
                        new_name = old_name + '.dup'
                        os.rename(old_name, new_name)
                        # end rename duplicates
                    else:
                        hashes[file_id] = full_path


#-----------------------------------------------------------------------
if sys.argv[1:]:
    check_for_duplicates(sys.argv[1:])
else:
    print("Please pass the paths to check as parameters to the script")
