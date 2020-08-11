#!/usr/bin/python
import os
import re

import peewee
from numpy import loadtxt, str

from models import PublicTrack

# Object describing one track file.

# Inputs [in the `lists` sub-dir]:
# 1. A csv mapping of file names to md5sums in the format:
# file_path/file_name,md5sum
# This may be generated from the directory containing all the files with:
# find . -type f | egrep "(\.bw|\.bb)" | xargs -n 1 md5sum >> md5sumBwBbInitial.txt
# awk '{print $2","$1}' md5sumBwBbInitial.txt | sort > md5sumBwBb.csv

class TrackFile:
    #csv mapping of file_path/file_names to md5sums
    md5sum_dict = []  # csv list of full_lines and md5sums (for .bigwig and .bigbed only)

    """
    # TrackFile Class properties
    full_line - full line of text from the 'find' file.  Beware, this includes the trailing \n.
    path - path to file (no trailing /)
    file_name - full name of the file
    file_root - file_name, less the extension
    file_extension - file extension
    file_type - BigWig, BigBed, etc.
    assembly - hg38  #TODO: verify this - it might not be the case (for non-human primates & mice)
    track_type - signal_forward, signal_reverse, etc.  Defaults to signal_unstranded.
    raw_experiment_type - Unrefined experiment_type.
    experiment_type_name - Corresponds to a mEGAdata.experiment_type.name
    md5sum - md5sum of the file.
    ihec_metrics - relative path and filename of ihec_metrics/.txt file (iff exists) 
    """

    # Constructor
    def __init__(self, full_line):
        self.full_line = full_line
        #Path
        self.path = os.path.dirname(full_line.lstrip('./'))
        #file_name
        self.file_name = os.path.basename(full_line.strip())  # Remove trailing \n
        # Call class methods to assign additional attributes
        self.find_file_type()
        self.find_track_type()
        self.find_md5sum(full_line.strip())
        self.find_raw_experiment_type()  # TODO combine with map_raw_experiment...() in to one function?
        self.map_raw_experiment_type_to_experiment_type_name()
        self.get_ihec_metrics() # requires recreated ihec_metrics/.txt dir structure.
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
            self.file_type = "Unknown"  # This category should never be used.

    # TrackType ought to be one of: signal_forward|signal_reverse|signal_unstranded|peak_calls|methylation_profile|contigs
    # All peak-type files are included in the peak_calls category...
    #TODO This will eventually be needed for IHEC DH browser definitions
    def find_track_type(self):
        if ".forward." in self.file_name: # This one is fine.
            self.track_type = "signal_forward"
        elif ".reverse." in self.file_name: # This one is fine.
            self.track_type = "signal_reverse"
        elif "_peaks" in self.file_name: # This one is fine.
            self.track_type = "peak_calls"
        elif "methylation" in self.file_name: # This one is fine.
            self.track_type = "methylation_profile"
        else: # All ChIP, non-peak ATACSeq, smRNA, coverage and chipmentation files are included here.
            # According to edcc/....../migration/1.3.4_to_1.3.5.sql, dataset_track.view='coverage' files were reassigned to the 'signal' category.
            self.track_type = "signal_unstranded"

    # Don't save this messy value as a DB field - keep it as a private TrackFile property.
    # raw_experiment_type is still messy and intended to map to mEGAdata.experiment_type.name through map_raw_experiment_type_to_experiment_type_name()
    # These will ultimately need to map to (edcc.track_metadata key: EXPERIMENT_TYPE)(maybe) or edcc.assay (probably).
    def find_raw_experiment_type(self):
        # The path is "mostly" structured as such: Project/Donor/(third_path_token)/Experiment_type/(tracks|peak_call)/
        match = re.search(r"[\w-]*/(tracks|peak_call)", self.path)
        self.raw_experiment_type = re.sub(r"/(tracks|peak_call)", "", match.group())

        # Manual intervention for some wacky-named file exceptions.
        if "MSC_Tagmentation-ChIP_100K" in self.path:
            self.raw_experiment_type = "Tagmentation-ChIP_100K_H3K4ME1"


    # Maps public_track.raw_experiment_type to mEGAdata.experiment_type.name, in a slightly fuzzy manner, when possible.
    # mEGAdata.experiment_type.name is used (rather than .internal_assay_short_name or .ihec_name).
    def map_raw_experiment_type_to_experiment_type_name(self):
        if re.search(r"ATAC", self.raw_experiment_type):
            self.experiment_type_name = "ATAC-seq"
        elif re.search(r"^BS", self.raw_experiment_type):
            self.experiment_type_name = "Bisulfite-seq"
        elif re.search(r"^CM", self.raw_experiment_type):
            self.experiment_type_name = "Capture Methylome"
        elif re.search(r"ChIP_Input", self.raw_experiment_type):
            self.experiment_type_name = "ChIP-Seq Input"
        elif re.search(r"^chipmentation_", self.raw_experiment_type):
            res = re.search(r"H3K[\w]*", self.raw_experiment_type)
            self.experiment_type_name = "Chipmentation_" + res.group()
        elif re.search(r"H3K\d{1,2}(me\d|ac)", self.raw_experiment_type) and re.search(r"NChIP", self.raw_experiment_type) is None:
            res = re.search(r"H3K\d{1,2}(me\d|ac)", self.raw_experiment_type)
            self.experiment_type_name = res.group()
        elif re.search(r"^RNASeq", self.raw_experiment_type): # TODO: What about the case of RNA?  Though there shouldn't be any .bw, .bb in RNA directories (they were stored in RNASeq directories). 
            self.experiment_type_name = "RNA-seq"
        elif re.search(r"^smRNASeq", self.raw_experiment_type):
            self.experiment_type_name = "smRNA-seq"
        # TODO: Now need to handle mRNA-seq case (since there are now data files of this type in EMC_BluePrint).
        elif re.search(r"^mRNASeq", self.raw_experiment_type): # TODO: UNTESTED!!!
            self.experiment_type_name = "mRNA-seq"
        # TODO - Still must handle NChIP and Tagmentation cases.
        else:
            self.experiment_type_name = "Indeterminate"


    # full_line must not contain any \n 
    def find_md5sum(self, full_line):
        if self.md5sum_dict:
            # Class var dictionary of all md5sums already populated.
            pass
        else:
            # Class var dictionary of all md5sums is empty and must be populated.
            self.load_md5sum()
        if self.file_type in ['BigWig', 'BigBed']:  # md5sum list should only contain the .bw and .bb files.
            if full_line in self.md5sum_dict:
                self.md5sum = self.md5sum_dict[full_line]
            else:
                self.md5sum = "Uncalculated" 

    @classmethod
    def load_md5sum(cls):
        try:
            key_value = loadtxt("lists/md5sumBwBb.csv", delimiter=",", dtype=str)  # numpy.loadtxt and numpy.str
        except OSError:
            print("Cannot open file")
        else:
            cls.md5sum_dict = {k:v for k,v in key_value}


    # Attempt to find a corresponding ihec_metrics/.txt file.
    # Must have the structured_data hierarchy recreated in ./lists/ihec_metrics/ containing full paths and the ihec_metrics/.txt and ihec_metrics/read_stats.txt files (the raw data files, .bw & .bb files are not neccessary (and besides, way too large)).
    def get_ihec_metrics(self):
        # Define the path    
        metric_path = re.sub(r"(/tracks)|(/peak_call)", r"/ihec_metrics", self.path)
        metric_rel_path = r"./lists/ihec_metrics/" + metric_path + r"/" # Relative location of recreated structured_data hierarchy.
        # Define the file name
        metric_base_file_name = self.file_name.replace(r"_peaks", r"")
        metric_basic_file_name = re.sub(r"(\..*)", r".txt", metric_base_file_name)
        metric_read_stats_file_name = re.sub(r"(\..*)", r".read_stats.txt", metric_base_file_name)
        # Test for a match.
        if os.path.isfile(metric_rel_path + metric_basic_file_name):
            self.ihec_metrics = metric_rel_path + metric_basic_file_name
        elif os.path.isfile(metric_rel_path + metric_read_stats_file_name):
            self.ihec_metrics = metric_rel_path + metric_read_stats_file_name
        else:
            self.ihec_metrics = None


    # Construct and return a TrackFile from a Peewee PublicTrack
    @classmethod
    def from_PublicTrack(cls, PublicTrack):
        pt = cls(f"./{PublicTrack.path}/{PublicTrack.file_name}") # Recreate as a full_line to reuse the __init__ constructor.
        return pt


    # Better displayed as a string
    def __str__(self):
        # full_line = self.full_line
        # 
        # file_name = self.file_root + ": " + self.file_extension
        # file_type = self.file_type
        # return full_line + path + "\n" + file_name + "\n" + file_type + "\n"
        # return self.full_line + ": " + self.md5sum
        # return self.path + "/"+ self.file_name + ": " + self.md5sum
        # return self.path + "/" + self.file_name + "," + self.raw_experiment_type
        return str(self.path.split("/"))

    # Portray the base line we are dealing with
    def __repr__(self):
        # return self.full_line
        return self.path + " " + self.file_name

