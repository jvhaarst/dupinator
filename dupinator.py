#!/usr/bin/python

# Dupinator
# Original script by Bill Bumgarner: see
# http://www.pycs.net/bbum/2004/12/29/
#
# Updated by Andrew Shearer on 2004-12-31: see
# http://www.shearersoftware.com/personal/weblog/2005/01/14/dupinator-ii

import os
import sys
import stat
import md5

filesBySize = {}
requireEqualNames = False

def walker(arg, dirname, fnames):
    d = os.getcwd()
    os.chdir(dirname)
    try:
        fnames.remove('Thumbs')
    except ValueError:
        pass        
    for f in fnames:
        if not os.path.isfile(f) or os.path.islink(f) or f == '.DS_Store':
            continue
        size = os.stat(f)[stat.ST_SIZE]
        if size < 100:
            continue
        if filesBySize.has_key(size):
            a = filesBySize[size]
        else:
            a = []
            filesBySize[size] = a
        a.append(os.path.join(dirname, f))
    os.chdir(d)

for x in sys.argv[1:]:
    sys.stderr.write('Scanning directory "%s"....' % x + "\n")
    os.path.walk(x, walker, filesBySize)    

FIRST_SCAN_BYTES = 1024
sys.stderr.write( 'Finding potential dupes...' + "\n")
dupes = [] # ashearer
potentialDupes = []
potentialCount = 0
sizes = filesBySize.keys()
sizes.sort()
for k in sizes:
    inFiles = filesBySize[k]
    hashes = {}
    if len(inFiles) is 1: continue
    sys.stderr.write( 'Testing %d files of size %d...' % (len(inFiles), k) + "\n")
    if requireEqualNames:
        for fileName in inFiles:
            hashes.setdefault(os.path.basename(fileName), []).append(fileName)
        inFiles = []
        for nameGroup in hashes.values():
            if len(nameGroup) > 1:
                inFiles.extend(nameGroup)
        hashes = {}
    for fileName in inFiles:
        #if not os.path.isfile(fileName):
        #    continue
        aFile = file(fileName, 'r')
        hasher = md5.new(aFile.read(FIRST_SCAN_BYTES))
        hashValue = hasher.digest()
        if hashes.has_key(hashValue):
            hashes[hashValue].append(fileName)
        else:
            hashes[hashValue] = [fileName]
        aFile.close()
    outFileGroups = [fileGroup for fileGroup in hashes.values() if len(fileGroup) > 1] # ashearer
    if k <= FIRST_SCAN_BYTES:   # we already scanned to whole file; put into definite dups list (ashearer)
        dupes.extend(outFileGroups)
    else:
        potentialDupes.extend(outFileGroups)
    potentialCount = potentialCount + len(outFileGroups)
del filesBySize

sys.stderr.write( 'Found %d sets of potential dupes...' % potentialCount  + "\n")
sys.stderr.write( 'Scanning for real dupes...'  + "\n")

#dupes = [] ashearer
for aSet in potentialDupes:
    #outFiles = []
    hashes = {}
    for fileName in aSet:
        sys.stderr.write( 'Scanning file "%s"...' % fileName   + "\n")
        aFile = file(fileName, 'r')
        hasher = md5.new()
        while True:
            r = aFile.read(4096)
            if not len(r):
                break
            hasher.update(r)
        aFile.close()
        hashValue = hasher.digest()
        if hashes.has_key(hashValue):
            hashes[hashValue].append(fileName)  # ashearer
        else:
            hashes[hashValue] = [fileName] #ashearer
    outFileGroups = [fileGroup for fileGroup in hashes.values() if len(fileGroup) > 1] # ashearer
    dupes.extend(outFileGroups)

i = 0
bytesSaved = 0
for d in dupes:
    print 'Original is %s' % d[0]
    # Sort on length, as usually less interesting duplicates have longer names
    d.sort( lambda x,y: cmp(len(x), len(y)) )
    for f in d[1:]:
        i = i + 1
        print 'rm %s' % f
        bytesSaved += os.path.getsize(f)
        #os.remove(f)
    print

print "Would have saved %.1fK; %d file(s) duplicated." % (bytesSaved/1024.0,len(dupes))
