#!/usr/bin/python3
# import peewee
# from models import PublicTrack
from trackFile import TrackFile # already in pwd
import re, os

# Reads a directory listing containing data files and matches them to an ihec_metric read_stats.txt file.

# Inputs [in the `lists` sub-dir]:
# 1. A listing of only the .bigwig and .bigbed files from the root directory containing all the files, generated through: `find . -type f | egrep "(\.bw$)|(\.bb$)" > lists/ls_bwbb.txt` 
# 2. Recreated the structured_data hierarchy in ./lists/ihec_metrics/ containing only full paths and the read_stats (.txt) files.

def main():

    #Open and read list of files
    try:
        f = open("lists/structured_data_ls_bwBb.txt", "r") # Could add this filename as a command line param.
        # f = open("lists/structured_data_ls_bwBb_short.txt", "r") # Could add this filename as a comand line param.
    except OSError:
        print("Cannot open file")
    else:
        fl = f.readlines()
        for l in fl:
            # Convert a file line into a TrackFile object
            my_track_file = TrackFile(l)
            
            # Attempt to match to a read_stats .txt file.
            # Define the path    
            metric_path = re.sub(r"(/tracks)|(/peak_call)", r"/ihec_metrics", my_track_file.path)
            # metric_path = my_track_file.path.replace(r"/tracks", r"/ihec_metrics") # Working, sort of.
            metric_rel_path = r"./lists/ihec_metrics/" + metric_path + r"/"
            # Define the file name
            metric_base_file_name = my_track_file.file_name.replace(r"_peaks", r"")
            metric_basic_file_name = re.sub(r"(\..*)", r".txt", metric_base_file_name)
            metric_read_stats_file_name = re.sub(r"(\..*)", r".read_stats.txt", metric_base_file_name)
            # Test for a match.
            if os.path.isfile(metric_rel_path + metric_basic_file_name) or os.path.isfile(metric_rel_path + metric_read_stats_file_name):
                pass
                print(repr(my_track_file) + ": Match")
            else:
                print(repr(my_track_file) + ": No match")
                # print(f"Basic: {metric_rel_path + metric_basic_file_name}")
                # print(f"Read_stats: {metric_rel_path + metric_read_stats_file_name}")
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
# Overall, of the 3512 files in EMC, the following types were missing accompanying read_stats.txt files:
# Total without read_stats.txt:
# 339
# These are further classified as...
# .peak files without read_stats.txt:
# 226
# _Input files without read_stats.txt:
# 81
# Other files without read_stats.txt
# 32 
# 
# Considering that this is not an exhaustive and essential report, no further effort was made to find _read_stats.txt files for the last 32 files.  99% is good enough.
