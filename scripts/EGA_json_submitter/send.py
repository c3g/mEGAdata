# Import Python packages
import requests
import os
import json
import sys
import logging
import pyexcel as pe
import argparse
from configparser import ExtendedInterpolation, RawConfigParser

# Import custom code, in pwd.
import utils
import connection
import globals # A few critical global vars, for use among multiple scripts, defined.
from egaobj import Submission, Sample, Experiment, Run, File, Dataset

# Process CLA
parser = argparse.ArgumentParser()
# TODO: Should this be ? nargs?  (one of, rights)
parser.add_argument("operation", action="store", nargs="?", choices=["send", "delete-all-objects", "record-EGA-objects", "all-file-info", "pass"], default="", help="Operation to perform.  `pass` to send nothing new.")
parser.add_argument("--new-submission", "--ns", action="store_true", help="Initiate a new Submission rather than working on the previous one.")
parser.add_argument("--validate", action="store_true", help="Attempt to VALIDATE all EGA Objects.")
parser.add_argument("--submit", action="store_true", help="Attempt to SUBMIT all EGA Objects.")
# Could add a --delete-all-of option (choices=["samples", "experiments", ...])
args = parser.parse_args()

# Make sure NOT TO DELETE all studies, dacs, policies, etc, when deleting the Submission's everything else.  If they are status=SUBMITTED, they should resist, but can't be sure...

def main():
    logging.debug(f"Running script with arguments: {str(sys.argv)}.")
    # Login and save the authorzation token.
    connection.login()

    # Continue working on previous Submission by default, unless new Submission is specified as CLA.
    if args.new_submission or not globals.config["session"]["submissionId"]: # No previous submissionId
        globals.mySub.send()

    ## SWITCH of CLA operation to perform
    if args.operation == "send":
        # Process the relationMapping spreadsheet, build EGA Objects and send them.
        process_rows()
    elif args.operation == "delete-all-objects":
        # Delete all EGA Objects in this submission
        globals.mySub.delete_all_objects()
    elif args.operation == "record-EGA-objects":
    # Get info about all Submission objects.
        globals.mySub.record_EGA_objects()
    elif args.operation == "all-file-info":
    # Get info about all uploaded files.
        all_ftp_uploaded_files_info()
    # Otherwise, pass.

    # POSSIBLE VALIDATION OR SUBMISSION
    # Error-check Submission in its entirety only.  VALIDATING / SUBMITTING partial Submissions (or object by object) is not recommended (and often, for reasons of referential integrity, won't work).
    if args.validate:
        globals.mySub.validate()
    if args.submit:
        globals.mySub.submit()

    # FINISHING UP...
    # Dump object_registry to disk.
    record_obj_registry()
    # connection.logout()
    logging.debug(f"SCRIPT TERMINATED WITH SUCCESS.")


# Get one spreadsheet row to work with.
def process_rows():
    # Define section of relation mapping spreadsheet that contains Sample information
    rows = pe.get_records(file_name=globals.config["relations"]["dir"] + globals.config["relations"]["file"],\
        start_row = globals.config.getint("relations", "start_row"),\
        name_columns_by_row=globals.config.getint("relations", "name_columns_by_row"),\
        row_limit=globals.config.getint("relations", "row_limit"))
    logging.debug(f"Found {len(rows)} rows in the relation mapping spreadsheet.")
    for row in rows:
        # logging.debug(f"Working on ")
        Sample(row["Sample_alias"], row["Sample_template"])
        Experiment(row["Sample_alias"], row["Experiment_alias"], row["Experiment_template"])
        file1 = File(row["File1_fileName"], row["File1_checksum"], row["File1_encrypted_checksum"])
        file2 = File(row["File2_fileName"], row["File2_checksum"], row["File2_encrypted_checksum"])
        Run(row["Sample_alias"], row["Experiment_alias"], row["Run_alias"], file1, file2)
        # Create the Datasets, but don't send until AFTER all Runs are sent, since their Ids are required.
        Dataset(row["Dataset_alias"], row["Dataset_template"])
    # Run through .ods again, for each dataset, append its Runs and update the obj_registry
    for row in rows:
        dataset = Dataset.get_by_alias(row["Dataset_alias"])
        dataset.add_run(Run.get_by_alias(row["Run_alias"]))
        dataset.update_obj_registry()
    # Now that datasets are updated, send() all Datasets in the Dataset obj_registry.  (Assumes there is at least one row being processed.)
    Dataset.send_all()


# Dump globals.obj_registry in quasi-json formatting, to record final state of Submission.
def record_obj_registry():
    for obj_type in globals.obj_registry:
        try:
            f = open(f"{globals.config['directories']['response_dir']}obj_registry/{str(obj_type)}.json", "w")
        except:
            logging.error(f"Couldn't open file to write {str(obj_type)}s from object registry.")
        f.write("[\n")
        for obj in globals.obj_registry[obj_type]:
            f.write(str(obj) + ",\n")
            # Leaves a trailing `,` after last object.  Not sytactically correcty JSON, but acceptable to Python.
        f.write("]")
        f.close()

# Save a JSON of all data files recognized by the EGA server.
def all_ftp_uploaded_files_info():
    path = "/files?sourceType=EBI_INBOX&skip=0&limit=0"
    url = globals.BASE_URL + path
    r = requests.get(url, headers=json.loads(globals.config["global"]["headers"]))
    if r.status_code != 200:
        raise Exception("Could not retrieve file info.")
    f = open(globals.config["directories"]["response_dir"] + "all_files_ega_inbox.json", "w")
    f.write(r.text + "\n")
    logging.debug(f"All file information retrieved.")


if __name__ == "__main__":
  main()
