dupinator
=========

The original dupinator.py script was created by Bill Bumgarner, and later improved by Andrew Shearer.

The "best" version will be simple called dupinator.py, the others are there for historical reference.

The script is used to find duplicate files, taking care to use as little CPU as possible, thus only comparing files of the same size, then checking the first kb for differences, and after that creating a checksum of the whole file.
