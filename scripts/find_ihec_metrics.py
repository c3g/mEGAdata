#!/usr/bin/python3
# import peewee
# from models import PublicTrack
from trackFile import TrackFile # already in pwd
import re, os

# Reads a directory listing of public_track data files and matches them to an ihec_metric/.txt (or read_stats.txt) file.

# Inputs [inside the `./lists` sub-dir]:
# 1. A listing of only the .bigwig and .bigbed files from the root directory containing all the files, generated through: `find . -type f | egrep "(\.bw$)|(\.bb$)" > lists/ls_bwbb.txt` 
# 2. Recreate the structured_data hierarchy in ./lists/ihec_metrics/ containing only full paths and the ihec_metrics/.txt and ihec_metrics/read_stats.txt files (the raw data files and the .bw & .bb files are not neccessary).
# This can be accomplished with:
# find . -type f | egrep "\.txt$" | grep "ihec_metrics" > ls_ihec_metrics.txt
# tar -cvzf ihec_metrics.tgz --files-from=ls_ihec_metrics.txt

# All the significant code from this file got refactored into TrackFile.get_ihec_metrics().
# This script is really just a testing wrapper of TrackFile.get_ihec_metrics(), but the description of Inputs is still useful.

def main():
    try:
        f = open("lists/structured_data_ls_bwBb.txt", "r") # Could add this filename as a command line param.
    except OSError:
        print("Cannot open file")
    else:
        fl = f.readlines()
        for l in fl:
            # Convert a dir listing line into a TrackFile object
            my_track_file = TrackFile(l)
            # Find the ihec_metrics file
            if my_track_file.get_ihec_metrics():
                print(repr(my_track_file) + ": Match")
            else:
                print(repr(my_track_file) + ": No match")

    finally:
        f.close()

if __name__ == "__main__":
  main()


#--------------------------
# Notes
#--------------------------
# 
# .peak files can be problematic.  Sometimes, /peak_call/ .bb files don't have their own, unique corresponding /ihec_metrics/ directory.  The closest one is used by the /tracks/ directory _Input file.  For example:
# │       ├── H3K36me3
# │       │   ├── ihec_metrics
# │       │   │   └── BF761_TC_ChIP_Input_1.read_stats.txt
# │       │   ├── peak_call
# │       │   │   └── BF761_TC_peaks.broadPeak.bb
# │       │   └── tracks
# │       │       └── BF761_TC_ChIP_Input_1.bw
#
# So there are read_stats.txt for the _Input file, but no corresponding read_stats.txt for the peaks file.
#
# _Input files can also be problematic on their own (simply missing an accompanying read_stats.txt file).
#
#
# Overall, of the 3512 files in EMC, the following types were missing accompanying ihec_metrics/.txt files:
# Total without ihec_metrics/.txt:
# 339
# These are further sub-classified as...
# .peak files without ihec_metrics/.txt:
# 226
# _Input files without ihec_metrics/.txt:
# 81
# Other files without ihec_metrics/.txt
# 32 
# 
# Considering that this is not an exhaustive and essential report, no further effort was made to find ihec_metrics/.txt files for the last 32 files.  99% is good enough.
