#!/usr/bin/python
from __future__ import print_function
import os
# import csv
from numpy import loadtxt, str

class TrackFile:
    #Class variable
    md5sumDict = [] # csv list of fullLines and md5sums (for .bigWig and .BigBeds only)

    # Need to find:
    # dataset_id - pair it to the hg19 db entry
    # assembly - always hg38
    # track_type (signal_forward, etc...)
    # url - should be something like path...

    """
    # trackFile Class properties
    fullLine - full line of text from the 'find' file.  Beware, this includes the trailing \n.
    path - path to file (no trailing /)
    fileName - full name of the file
    fileRoot - fileName, less the extension
    fileExtension - file extension
    fileType - BigWig, BigBed, etc.
    assembly - hg38
    track_type - signal_forward, signal_reverse, etc.
    md5sum - md5sum of the file.
    """

    # Constructor
    def __init__(self, fullLine):
        self.fullLine = fullLine
        #Path
        self.path = os.path.dirname(fullLine.lstrip('./'))
        #FileName
        self.fileName = os.path.basename(fullLine.strip()) # Remove trailing \n
        # Call class methods to assign additional attributes
        self.findFileType()
        self.findTrackType()
        self.findMd5sum(fullLine.strip())
        self.assembly = "hg38" # All datasets in this directory are hg38.

    def findFileType(self):
        myRoot = os.path.splitext(self.fileName)
        self.fileRoot = myRoot[0]
        myExtension = os.path.splitext(self.fileName)
        self.fileExtension = myExtension[1]
        # Define file type
        if self.fileExtension == ".bw":
            self.fileType = "BigWig"
        elif self.fileExtension == ".bb":
            self.fileType = "BigBed"
        elif self.fileExtension == ".txt":
            self.fileType = "Text"
        elif self.fileExtension == ".gz":
            self.fileType = "GZip"
        elif self.fileExtension == ".bam":
            self.fileType = "Bam"
        elif self.fileExtension == '.bai':
            self.fileType = "Bai"
        else:
            self.fileType = "Unknown" # This category should never be used.


# These will need to map to edcc.track_metadata key: EXPERIMENT_TYPE or edcc.assay.

# Define the track, as one of:
# peak_calls - in a peak_call dir, and fileName contains _peaks.
# signal_unstranded - All the histone stuff.
# signal_forward - fileName contains .forward.
# signal_reverse - fileName contains .reverse.
# methylation_profile - fileName contains `methylation`

# What about 'coverage'?  (Seems to go along with methylation)
# What about 'Input'? - signal_unstranded.
# Also have the ATAC-Seq files.

    def findTrackType(self):
        if ".forward." in self.fileName:
            self.track_type = "signal_forward"
        elif ".reverse." in self.fileName:
            self.track_type = "signal_reverse"
        elif "_peaks" in self.fileName:
            self.track_type = "peak_calls"
        elif "ChIP" in self.fileName:
            self.track_type = "signal_unstranded"
        elif "methylation" in self.fileName:
            self.track_type = "methylation_profile"
        ## Unknown file types - ALL BELOW MUST BE FURTHER CATEGORIZED
        elif "coverage" in self.fileName:
            self.track_type = "coverage" # always alongside methylation files.
        elif "ATAC" in self.fileName:
            self.track_type = "ATAC"
        elif "smRNASeq" in self.fileName:
            self.track_type = "smRNASeq"
        elif "chipmentation" in self.fileName:
            self.track_type = "chipmentation"
        elif "_BS_" in self.fileName and "BS" in self.path:
            self.track_type = "_BS_" # Bisulfite sequencing determines methylation.
        else:
            self.track_type = "Unknown" # Category should be unused.


    # fullLine must not contain any \n 
    def findMd5sum(self, fullLine):
        if self.md5sumDict:
            # Class var dictionary of all md5sums already populated.
            pass
        else:
            # Class var dictionary of all md5sums is empty and must be populated.
            self.loadMd5sum()
        if self.fileType in ['BigWig', 'BigBed']: #md5sum list should only contain .bw and .bb files.
            self.md5sum = self.md5sumDict[fullLine]


    @classmethod
    def loadMd5sum(cls):
        try:
            key_value = loadtxt("md5sumBwBb.csv", delimiter=",", dtype=str) # numpy.loadtxt and numpy.str
        except OSError:
            print("Cannot open file")
        else:
            cls.md5sumDict = {k:v for k,v in key_value}


    # Better displayed as a string
    def __str__(self):
        # fullLine = self.fullLine
        # 
        # fileName = self.fileRoot + ": " + self.fileExtension
        # fileType = self.fileType
        # return fullLine + path + "\n" + fileName + "\n" + fileType + "\n"
        # return fullLine + path + fileName + " " + fileType + " " + self.track_type
        # return self.fullLine + ": " + self.md5sum
        return self.path + "/"+ self.fileName + ": " + self.md5sum

    # Portray the base line we are dealing with
    def __repr__(self):
        return self.fullLine

