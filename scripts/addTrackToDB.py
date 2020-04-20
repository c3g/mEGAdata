#!/usr/bin/python
from __future__ import print_function
import peewee
# For relative imports, modify sys.path
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__)))) # parent directory of pwd
from app import db
from models import PublicTrack
from trackFile import TrackFile # already in pwd

# Inputs:
# 1. A listing of the directory containing all the files, generated through: `find . -type f` 
# 2. A csv mapping of file names to md5sums in the format:
# filePath/fileName,md5sum
# This may be generated from the directoy containing all the files with:
# find . -type f | egrep "(\.bw|\.bb)" | xargs -n 1 md5sum >> md5sumBwBbInitial.txt
# awk '{print $2","$1}' md5sumBwBbInitial.txt | sort > md5sumBwBb.csv

def main():
    db.set_autocommit(True)

    #Open and read list of files
    try:
        f = open("structured_data_ls_bwBb.txt", "r") # Could add this filename as a comand line param.
        # f = open("structured_data_ls_bwBb_short.txt", "r") # Could add this filename as a comand line param.
    except OSError:
        print("Cannot open file")
    else:
        fl = f.readlines()
        for l in fl:
            myTrackFile = TrackFile(l)
            # Convert to a peewee PublicTrack model
            public_track = PublicTrack()
            public_track.assembly = myTrackFile.assembly
            public_track.track_type = myTrackFile.track_type
            public_track.md5sum = myTrackFile.md5sum
            public_track.path = myTrackFile.path
            public_track.file_name = myTrackFile.fileName
            public_track.file_type = myTrackFile.fileType
            public_track.save()
            # print(str(myTrackFile))
    finally:
        f.close()
# end of main

if __name__ == "__main__":
  main()
