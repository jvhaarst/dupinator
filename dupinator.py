#!/usr/bin/env python3


# Dupinator
# Original script by Bill Bumgarner: see
# http://www.pycs.net/bbum/2004/12/29/
#
# Updated by Andrew Shearer on 2004-12-31: see
# http://www.shearersoftware.com/personal/weblog/2005/01/14/dupinator-ii

import os
import sys
import stat
from hashlib import md5
from os.path import join, getsize
import shlex

minsize = 0
# For easier testing
maxsize = 0

FIRST_SCAN_BYTES = 1024

filesBySize = {}
requireEqualNames = False
remove = False


def fmt3(num):
    for x in ['', 'Kb', 'Mb', 'Gb', 'Tb']:
        if num < 1024:
            return "%3.1f%s" % (num, x)
        num /= 1024

for directory in sys.argv[1:]:
    sys.stderr.write('Scanning directory "%s".' % directory + "\n")
    # Fill dict with files of same size
    for root, dirs, files in os.walk(directory):
        if 'Thumbs' in dirs:
            dirs.remove('Thumbs')  # Do not go into 'Thumbs' folder
        if '.DS_Store' in dirs:
            dirs.remove('.DS_Store')  # Do not go into '.DS_Store' folder
        for f in files:
            size = getsize(join(root, f))
            if size < minsize:
                continue
            if size > maxsize and maxsize != 0:
                continue
            # Get list of names of this size if it exists, create otherwise
            if size in filesBySize:
                list_of_names = filesBySize[size]
            else:
                list_of_names = []
                filesBySize[size] = list_of_names
            list_of_names.append(join(root, f))


sys.stderr.write('Finding potential dupes.' + "\n")
dupes = []
potentialDupes = []
potentialCount = 0
sizes = list(filesBySize.keys())
sizes.sort()
for k in sizes:
    inFiles = filesBySize[k]
    hashes = {}
    if len(inFiles) == 1:
        continue
    sys.stderr.write('Testing %d files of size %d.' % (len(inFiles), k) + "\n")
    if requireEqualNames:
        for fileName in inFiles:
            hashes.setdefault(os.path.basename(fileName), []).append(fileName)
        inFiles = []
        for nameGroup in list(hashes.values()):
            if len(nameGroup) > 1:
                inFiles.extend(nameGroup)
        hashes = {}
    for fileName in inFiles:
        aFile = open(fileName, 'rb')
        hasher = md5()
        hasher.update(aFile.read(FIRST_SCAN_BYTES))
        hashValue = hasher.digest()
        if hashValue in hashes:
            hashes[hashValue].append(fileName)
        else:
            hashes[hashValue] = [fileName]
        aFile.close()
    outFileGroups = [fileGroup for fileGroup in list(hashes.values()) if len(fileGroup) > 1]
    if k <= FIRST_SCAN_BYTES:   # we already scanned to whole file; put into definite dups list (ashearer)
        dupes.extend(outFileGroups)
    else:
        potentialDupes.extend(outFileGroups)
    potentialCount = potentialCount + len(outFileGroups)
del filesBySize

sys.stderr.write('Found %d sets of potential dupes.' % potentialCount + "\n")
sys.stderr.write('Scanning for real dupes.' + "\n")

for aSet in potentialDupes:
    hashes = {}
    for fileName in aSet:
        sys.stderr.write('Scanning file "%s".' % fileName + "\n")
        aFile = open(fileName, 'rb')
        hasher = md5()
        while True:
            r = aFile.read(4096)
            if not len(r):
                break
            hasher.update(r)
        aFile.close()
        hashValue = hasher.digest()
        if hashValue in hashes:
            hashes[hashValue].append(fileName)
        else:
            hashes[hashValue] = [fileName]  # ashearer
    outFileGroups = [fileGroup for fileGroup in list(hashes.values()) if len(fileGroup) > 1]
    dupes.extend(outFileGroups)

i = 0
counter = 0
bytesSaved = 0
for d in dupes:
    counter = counter + 1
    # Sort on length, as usually less interesting duplicates have longer names
    d.sort(key = len)
    print ('Original is\t{}\t{}\t({})'.format(d[0], fmt3(os.path.getsize(d[0])), counter))
    for f in d[1:]:
        i = i + 1
        bytesSaved += os.path.getsize(f)
        if remove:
            print("Removing\t{}".format(f))
            os.remove(f)
        else:
            print ('rm {}'.format(shlex.quote(f)))
    print()
if remove:
    print ("Have removed {}; {} file(s) duplicated.".format(fmt3(bytesSaved), len(dupes)))
else:
    print ("Would have saved {}; {} file(s) duplicated.".format(fmt3(bytesSaved), len(dupes)))
