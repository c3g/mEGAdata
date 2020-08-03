import re
import os
import logging

# Runs only under python 2.7 (not python3) since mp2 uses python 2.7.

# Move RNA tracks and IHEC_metrics from original_data/ to their appropriate places in structured_data/, renaming as appropriate.
# Applies to EMC_Asthma, EMC_Blueprint and EMC_SARDs only.

# Make sure user umask is set to 007 before running. # TODO: write this into the script with os.umask()

# Beware _'s in sample.names. (to be confused with directory separators)

# Establish logging.
logging.basicConfig(
    filename="structureOriginal_data.log",
    filemode="w",
    format='%(levelname)s: %(message)s',
    level=logging.INFO) 
    # level=logging.DEBUG) 

# Basic parameters.
project = "EMC_Asthma"
originalRoot = "./original_data/rnaseq/" + project + "/tracks/"
structuredRoot = "./structured_data/" + project + "/"

# Link the track files
for track_file in os.listdir(originalRoot):
    # Skip an exceptional filename case
    match = re.match("MSC16_P3_OD_RNASeq_1", track_file)
    if match:
        continue

    # Parse filename into path and file, handling two cases differently.
    if re.match(r"\d", track_file):
        # File starts with a number
        tokens = re.split("_", track_file, maxsplit=2)
        # Confirm presence of raw_reads dir
        raw_reads_dir = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNA/raw_reads/"
        logging.debug(raw_reads_dir + " : " + str(os.path.isdir(raw_reads_dir)))

        new_track_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/tracks/"
        new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/ihec_metrics/"
    else:
        # File starts with a letter, except for MSC16_P3_OD_RNASeq_1* case
        tokens = re.split("_", track_file, maxsplit=1)
        # Confirm presence of raw_reads dir
        raw_reads_dir = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNA/raw_reads/"
        logging.debug(raw_reads_dir + " : " + str(os.path.isdir(raw_reads_dir)))
        
        new_track_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/tracks/"
        new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/ihec_metrics/"
        
    # Create the new RNASeq track and ihec_metrics directories, if they doesn't exist already
    if (not os.path.isdir(new_track_path)) and (not os.path.isdir(new_metrics_path)):
        try:
            os.makedirs(new_track_path, 0770)
            os.makedirs(new_metrics_path, 0770)
        except OSError as er:
            logging.error(track_file + " mkdirs OSError: " + er.message)
    
    # Link file, name unchanged.
    try:
        os.link(originalRoot + track_file, new_track_path + track_file)
    except OSError as er:
        logging.error(track_file + " link OSError: " + er.message)

# Link the ihec_metrics files
originalRoot = "./original_data/rnaseq/" + project + "/ihec_metrics/"
for metrics_file in os.listdir(originalRoot):
    # Skip that exceptional filename case
    match = re.search("MSC16_P3_OD_RNASeq_1", metrics_file)
    if match:
        continue

    # Gotta do something with the All.txt ihec_metrics files.  Retain them somewhere.  Spot-check their validity.
    match = re.search(r"_All\.txt", metrics_file)
    if match:
        logging.debug("Found the file " + metrics_file)
        continue

    new_metrics_file = re.sub("IHEC_metrics_rnaseq_", "", metrics_file)
    new_metrics_file = re.sub(r"\.txt", ".read_stats.txt", new_metrics_file)
    logging.debug(metrics_file + ": " + new_metrics_file)
    
    # Parse the new_metrics_file in two different ways, depending on whether it starts with a number or a letter.
    if re.match(r"\d", new_metrics_file):
        # File starts with a number
        tokens = re.split("_", new_metrics_file, maxsplit=2)
        new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/ihec_metrics/"
    else:
        # File starts with a letter, such as all those C00M cases (except for MSC16_P3_OD_RNASeq_1*)
        tokens = re.split("_", new_metrics_file, maxsplit=1)
        new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/ihec_metrics/"

    # Link file, using the new name.
    try:
        os.link(originalRoot + metrics_file, new_metrics_path + new_metrics_file)
    except OSError as er:
        logging.error(metrics_file + " link OS Error: " + er.message)
        logging.debug("Can't link: " + new_metrics_path + new_metrics_file)

'''
IHEC_metrics_rnaseq_600-2000_CD4_RNASeq_1.txt

610_0004
    Eos
        BS
            ihec_metrics
                610_0004_Eos_BS_1.read_stats.txt
'''
'''
IHEC_metrics_rnaseq_C00MS182a01v02_RNASeq_1.txt

 C00MS182a01v02
     C00MS182a01v02
        RNA
            raw_reads
        RNASeq
            tracks
            ihec_metrics

'''


'''
600-0002_CD4_RNASeq_1.forward.bw

 600-0002
     CD4
        RNA
            raw_reads
        RNASeq
            tracks
            ihec_metrics

OR

C00MS182a01v02_RNASeq_1.forward.bw

C00MS182a01v02
    C00MS182a01v02
        RNA
            raw_reads
        RNASeq
            tracks
            ihec_metrics
'''

