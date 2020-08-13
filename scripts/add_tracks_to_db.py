#!/usr/bin/python3
import peewee
from models import PublicTrack
from trackFile import TrackFile # already in pwd

# Reads a directory listing containing data files and inserts them into the database as public_tracks.

# Inputs [in the `lists` sub-dir]:
# 1. A listing of only the .bigwig and .bigbed files from the root directory containing all the files, generated through: `find . -type f | egrep "(\.bw$)|(\.bb$)" > lists/ls_bwBb.txt` 

def main():

    #Open and read list of files
    try:
        f = open("lists/ls_bwBb.txt", "r") # Could add this filename as a command line param.
        # f = open("lists/structured_data_ls_bwBb.txt", "r") # Could add this filename as a command line param.
        # f = open("lists/structured_data_ls_bwBb_short.txt", "r") # Could add this filename as a comand line param.
    except OSError:
        print("Cannot open file")
    else:
        fl = f.readlines()
        for l in fl:
            # Convert a file line into a TrackFile object
            my_track_file = TrackFile(l)

            # Exclude _Input files that aren't exlicitly in ChIP_Input directories.
            # These are from the EMC_Mitochondrial_Disease and EMC_Temporal_Change projects.  Many *_Input* files are repeated and listed needlessly.
            if ("_ChIP_Input_" in my_track_file.file_name or "_ChIP2_Input_" in my_track_file.file_name)\
                and "/ChIP_Input/" not in my_track_file.path:
                # print(my_track_file.path)
                continue

            # Convert TrackFile object to a peewee PublicTrack model, using only the relevant fields from TrackFile # TODO better written as a TrackFile function, named something like TrackFile.to_public_track()
            public_track = PublicTrack.create()
            public_track.assembly = my_track_file.assembly
            public_track.track_type = my_track_file.track_type
            public_track.md5sum = my_track_file.md5sum
            public_track.path = my_track_file.path
            public_track.file_name = my_track_file.file_name
            public_track.file_type = my_track_file.file_type
            public_track.save()

    finally:
        f.close()

if __name__ == "__main__":
  main()
