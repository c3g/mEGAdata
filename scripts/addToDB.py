#!/usr/bin/python
from __future__ import print_function
from trackFile import TrackFile # in pwd

# Inputs:
# 1. A listing of the directory containing all the files, generated through: `find . -type f` 
# 2. A csv mapping of file names to md5sums in the format:
# filePath/fileName,md5sum
# This may be generated from the directoy containing all the files with:
# find . -type f | egrep "(\.bw|\.bb)" | xargs -n 1 md5sum >> md5sumBwBbInitial.txt
# awk '{print $2","$1}' md5sumBwBbInitial.txt | sort > md5sumBwBb.csv

def main():
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
            print(str(myTrackFile))
    finally:
        f.close()
# end of main

if __name__ == "__main__":
  main()
