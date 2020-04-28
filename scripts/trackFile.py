#!/usr/bin/python
import os
import re
import peewee
from models import PublicTrack
from numpy import loadtxt, str

# Object describing one track file.

# Inputs [in the `lists` sub-dir]:
# 1. A csv mapping of file names to md5sums in the format:
# file_path/file_name,md5sum
# This may be generated from the directory containing all the files with:
# find . -type f | egrep "(\.bw|\.bb)" | xargs -n 1 md5sum >> md5sumBwBbInitial.txt
# awk '{print $2","$1}' md5sumBwBbInitial.txt | sort > md5sumBwBb.csv


class TrackFile:
    #csv mapping of file_path/file_names to md5sums
    md5sum_dict = [] # csv list of full_lines and md5sums (for .bigwig and .bigbed only)

    """
    # TrackFile Class properties
    full_line - full line of text from the 'find' file.  Beware, this includes the trailing \n.
    path - path to file (no trailing /)
    file_name - full name of the file
    file_root - file_name, less the extension
    file_extension - file extension
    file_type - BigWig, BigBed, etc.
    assembly - hg38
    track_type - signal_forward, signal_reverse, etc. - NEEDS REWORKING
    raw_experiment_type - Unrefined experiment_type.
    md5sum - md5sum of the file.
    """

    # Constructor
    def __init__(self, full_line):
        self.full_line = full_line
        #Path
        self.path = os.path.dirname(full_line.lstrip('./'))
        #file_name
        self.file_name = os.path.basename(full_line.strip()) # Remove trailing \n
        # Call class methods to assign additional attributes
        self.find_file_type()
        self.find_track_type()
        self.find_raw_experiment_type()
        self.find_md5sum(full_line.strip())
        self.assembly = "hg38" # All datasets in this directory are hg38.

    def find_file_type(self):
        my_root = os.path.splitext(self.file_name)
        self.file_root = my_root[0]
        my_extension = os.path.splitext(self.file_name)
        self.file_extension = my_extension[1]
        # Define file type
        if self.file_extension == ".bw":
            self.file_type = "BigWig"
        elif self.file_extension == ".bb":
            self.file_type = "BigBed"
        elif self.file_extension == ".txt":
            self.file_type = "Text"
        elif self.file_extension == ".gz":
            self.file_type = "GZip"
        elif self.file_extension == ".bam":
            self.file_type = "Bam"
        elif self.file_extension == '.bai':
            self.file_type = "Bai"
        else:
            self.file_type = "Unknown" # This category should never be used.


    # TrackType ought to basically be (signal_forward|signal_reverse|signal_unstranded|peak_calls|methylation_profile|narrowPeak|broadPeak|coverage)
    # #TODO This is still very incomplete and will eventually be needed for IHEC DP browser definitions
    def find_track_type(self):
        if ".forward." in self.file_name:
            self.track_type = "signal_forward"
        elif ".reverse." in self.file_name:
            self.track_type = "signal_reverse"
        elif "_peaks" in self.file_name:
            self.track_type = "peak_calls"
        elif "ChIP" in self.file_name:  # I don't trust this part yet.
            self.track_type = "signal_unstranded"
        elif "methylation" in self.file_name:
            self.track_type = "methylation_profile"
        ## Unknown file types - ALL BELOW MUST STILL BE FURTHER CATEGORIZED
        ## These are not always mutually exclusive.  Argh!
        elif "coverage" in self.file_name:
            self.track_type = "coverage" # always alongside methylation files.
        else:
            self.track_type = "Unknown" # Category should be unused.

    # raw_experiment_type is still messy and intended to map to experiment_type.name.
    # These will ultimately need to map to (edcc.track_metadata key: EXPERIMENT_TYPE)(maybe) or edcc.assay (probably).
    def find_raw_experiment_type(self):
        # The path is "mostly" structured as such: Project/Donor/(third_path_token)/Experiment_type/(tracks|peak_call)/
        match = re.search(r"[\w-]*/(tracks|peak_call)", self.path)
        self.raw_experiment_type = re.sub(r"/(tracks|peak_call)", "", match.group())

        # Manual intervention for some wacky-named file exceptions.
        if "MSC_Tagmentation-ChIP_100K" in self.path:
            self.raw_experiment_type = "Tagmentation-ChIP_100K_H3K4ME1"

        # elif "ATAC" in self.file_name:
        #     self.track_type = "ATAC"
        # elif "smRNASeq" in self.file_name:
        #     self.track_type = "smRNASeq"
        # elif "chipmentation" in self.file_name:
        #     self.track_type = "chipmentation"
        # elif "_BS_" in self.file_name and "BS" in self.path:
        #     self.track_type = "_BS_" # Bisulfite sequencing determines methylation.


    # full_line must not contain any \n 
    def find_md5sum(self, full_line):
        if self.md5sum_dict:
            # Class var dictionary of all md5sums already populated.
            pass
        else:
            # Class var dictionary of all md5sums is empty and must be populated.
            self.load_md5sum()
        if self.file_type in ['BigWig', 'BigBed']: #md5sum list should only contain .bw and .bb files.
            self.md5sum = self.md5sum_dict[full_line]


    @classmethod
    def load_md5sum(cls):
        try:
            key_value = loadtxt("lists/md5sumBwBb.csv", delimiter=",", dtype=str) # numpy.loadtxt and numpy.str
        except OSError:
            print("Cannot open file")
        else:
            cls.md5sum_dict = {k:v for k,v in key_value}


    # Better displayed as a string
    def __str__(self):
        # full_line = self.full_line
        # 
        # file_name = self.file_root + ": " + self.file_extension
        # file_type = self.file_type
        # return full_line + path + "\n" + file_name + "\n" + file_type + "\n"
        # return self.track_type
        # return self.full_line + ": " + self.md5sum
        # return self.path + "/"+ self.file_name + ": " + self.md5sum
        # return self.path + "/" + self.file_name + "," + self.raw_experiment_type
        return str(self.path.split("/"))

    # Portray the base line we are dealing with
    def __repr__(self):
        return self.full_line

