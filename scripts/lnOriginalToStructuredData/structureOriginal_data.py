import re
import os
import logging

# Runs only under python 2.7 (not python3) since mp2 uses python 2.7.

# Move RNA tracks and IHEC_metrics from original_data/ to their appropriate places in structured_data/, renaming as appropriate.
# Applies to EMC_Asthma, EMC_BluePrint and EMC_SARDs only.

# Make sure user umask is set to 007 before running. # TODO: write this into the script with os.umask()

# Beware _'s in sample.names. (to be confused with directory separators)

def main():
    # Establish logging.
    logging.basicConfig(
        filename="structureOriginal_data.log",
        filemode="w",
        format='%(levelname)s: %(message)s',
        level=logging.INFO)
        # level=logging.DEBUG)

    # Basic parameters.
    # project = "EMC_Asthma"
    project = "EMC_BluePrint"
    originalRoot = "./original_data/rnaseq/" + project + "/tracks/"
    structuredRoot = "./structured_data/" + project + "/"

    # Link the track files
    for track_file in os.listdir(originalRoot):
        if project == "EMC_Asthma":
            # EMC_Asthma - Skip an exceptional filename case
            match = re.match("MSC16_P3_OD_RNASeq_1", track_file)
            if match:
                continue

            # Parse filename into path and file, handling two cases differently.
            if re.match(r"\d", track_file):
                # EMC_Asthma - File starts with a number
                tokens = re.split("_", track_file, maxsplit=2)
                # Confirm presence of raw_reads dir
                raw_reads_dir = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNA/raw_reads/"
                logging.debug(raw_reads_dir + " : " + str(os.path.isdir(raw_reads_dir)))

                new_track_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/tracks/"
                new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/ihec_metrics/"
            else:
                # EMC_Asthma - File starts with a letter, except for MSC16_P3_OD_RNASeq_1* case
                tokens = re.split("_", track_file, maxsplit=1)
                # Confirm presence of raw_reads dir
                raw_reads_dir = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNA/raw_reads/"
                logging.debug(raw_reads_dir + " : " + str(os.path.isdir(raw_reads_dir)))
                
                new_track_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/tracks/"
                new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/ihec_metrics/"
        elif project == "EMC_BluePrint":
            # Skip exceptional filenames.  Aren't any.
            # Parse filename.  Allow for both RNASeq and mRNASeq separately.
            parsed_filename = parse_BluePrint_filename(track_file)
            logging.debug(track_file + ": " + parsed_filename["donor"] + " " + parsed_filename["sample"] + " " + parsed_filename["experiment"])

            # Confirm presence of raw_reads dir
            raw_reads_dir1 = structuredRoot + parsed_filename["donor"] + "/" + parsed_filename["sample"] + "/" + "RNA/raw_reads/"
            raw_reads_dir2 = structuredRoot + parsed_filename["donor"] + "/" + parsed_filename["sample"] + "/" + "RNASeq/raw_reads/"
            logging.debug(raw_reads_dir1 + " or " + raw_reads_dir2 + ": " + str(os.path.isdir(raw_reads_dir1) or os.path.isdir(raw_reads_dir2)))

            new_track_path = structuredRoot + parsed_filename["donor"] + "/" + parsed_filename["sample"] + "/" + parsed_filename["experiment"] + "/tracks/"
            new_metrics_path = structuredRoot + parsed_filename["donor"] + "/" + parsed_filename["sample"] + "/" + parsed_filename["experiment"] + "/ihec_metrics/"

        # Create the new m?RNASeq track and ihec_metrics directories, if they don't exist already.
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
        # EMC_Asthma - Skip that exceptional filename case
        match = re.search("MSC16_P3_OD_RNASeq_1", metrics_file)
        if match:
            continue

        # TODO: do something with the All.txt ihec_metrics files.  Retain them somewhere.  Spot-check their validity.
        match = re.search(r"_All\.txt", metrics_file)
        if match:
            logging.debug("Found the file " + metrics_file)
            continue

        # Rename metrics file to match naming convention
        new_metrics_file = re.sub("IHEC_metrics_rnaseq_", "", metrics_file)
        new_metrics_file = re.sub(r"\.txt", ".read_stats.txt", new_metrics_file)
        logging.debug(metrics_file + " becomes: " + new_metrics_file)
        
        # Parse metrics_file to find directory
        if project == "EMC_Asthma":
            # Parse the new_metrics_file in two different ways, depending on whether it starts with a number or a letter.
            if re.match(r"\d", new_metrics_file):
                # EMC_Asthma - File starts with a number
                tokens = re.split("_", new_metrics_file, maxsplit=2)
                new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[1] + "/RNASeq/ihec_metrics/"
            else:
                # EMC_Asthma - File starts with a letter, such as all those C00M cases (except for MSC16_P3_OD_RNASeq_1*)
                tokens = re.split("_", new_metrics_file, maxsplit=1)
                new_metrics_path = structuredRoot + tokens[0] + "/" + tokens[0] + "/RNASeq/ihec_metrics/"
        elif project == "EMC_BluePrint":
            parsed_filename = parse_BluePrint_filename(new_metrics_file)
            new_metrics_path = structuredRoot + parsed_filename["donor"] + "/" + parsed_filename["sample"] + "/" + parsed_filename["experiment"] + "/ihec_metrics/"

        # Link metrics file, using the new name.
        try:
            os.link(originalRoot + metrics_file, new_metrics_path + new_metrics_file)
        except OSError as er:
            logging.error(new_metrics_path + new_metrics_file + " link OS Error: " + er.message)


def parse_BluePrint_filename(filename):
    m = re.match(r"[A-Z0-9]+", filename)
    donor = m.group(0)
    m = re.search(r"_(\w+)_m?RNASeq", filename)
    sample = m.group(1)
    m = re.search(r"m?RNASeq", filename)
    experiment = m.group(0)
    return {"donor": donor, "sample": sample, "experiment": experiment}

if __name__ == "__main__":
    main()
