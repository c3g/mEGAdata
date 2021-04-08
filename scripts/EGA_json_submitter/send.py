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
from egaobj import Submission, Sample, Experiment

# Process CLA
parser = argparse.ArgumentParser()
parser.add_argument("operation", action="store", nargs="?", choices=["send", "delete-all-objects", "record-EGA-objects", "all-file-info", "pass"], default="", help="Operation to perform.  `pass` to send nothing new.")
parser.add_argument("--new-submission", "--ns", action="store_true", help="Initiate a new Submission rather than working on the previous one.")
parser.add_argument("--validate", action="store_true", help="Attempt to VALIDATE all EGA Objects.")
parser.add_argument("--submit", action="store_true", help="Attempt to SUBMIT all EGA Objects.")
# Could add a --delete-all-of option (choices=["samples", "experiments", ...])
args = parser.parse_args()

# Make sure NOT TO DELETE all studies, dacs, policies, etc, when deleting the Submission's everything else.  If they are status=SUBMITTED, they should resist, but can't be sure...

# Need a better name for this script: EGAtransact, talktoEGA...  EGAzap!

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
    # Get info about all uploaded files.  Inclde as CLA or not?
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
    rows = pe.get_records(file_name=globals.config["directories"]["relation_mapping_dir"] + globals.config["directories"]["relation_mapping_file"],
    start_row=2,\
    name_columns_by_row=0,\
    # 24, # Will need to define this elsewhere.
    row_limit=6,\
    start_column=3,\
    column_limit=4 #4 to include Experiment.
    )
    logging.debug(f"Found {len(rows)} rows in the relation mapping spreadsheet.")
    for row in rows:
        # loggin.debug(f"Working on ")
        Sample(row["SampleAlias"])
        Experiment(row["SampleAlias"], row["ExperimentAlias"])

# Dump globals.obj_registry in quasi-json formatting, to record final state of Submission.
def record_obj_registry():
    for obj_type in globals.obj_registry:
        try:
            f = open(globals.config["directories"]["json_dir"] + "/sentEgaObj/" + str(obj_type) + ".json", "w")
        except:
            logging.error(f"Couldn't open file to write {str(obj_type)}s from object registry.")
        f.write("[\n")
        for obj in globals.obj_registry[obj_type]:
            f.write(str(obj) + ",\n")
            # Leaves a trailing `,` after last object.  Not sytactically correcty JSON, but acceptable to Python.
        f.write("]")
        f.close()

# Save a JSON of all fastq.gz files recognized by the server.
def all_ftp_uploaded_files_info():
    path = "/files?sourceType=EBI_INBOX&skip=0&limit=0"
    url = globals.BASE_URL + path
    r = requests.get(url, headers=json.loads(globals.config["global"]["headers"]))
    if r.status_code != 200:
        raise Exception("Could not retrieve file info.")
    f = open(globals.config["directories"]["json_dir"] + "all_files_ega_inbox.json", "w")
    f.write(r.text + "\n")
    logging.debug(f"All file information retrieved.")


if __name__ == "__main__":
  main()


#### JUNK ####
'''
        # if not mySample._is_present(mySample):
        # mySample.send()
            # mySample.validate()
            # mySample.submit()
    # Eventually get the id / EGAid back into mEGAdata.

# SAMPLES
def find_all_samples():
    # Define section of relation mapping spreadsheet that contains Sample information
    records = pe.get_records(file_name=globals.config["directories"]["relation_mapping_dir"] + globals.config["directories"]["relation_mapping_file"],
    start_row=2,\
    name_columns_by_row=0,\
    row_limit=16, # Will need to define this elsewhere.
    start_column=3,\
    column_limit=3
    )

    # Find unique Samples in spreadsheet
    for record in records:
        mySamples = []
        if record["Alias"] not in mySamples:
            mySamples.append(record["Alias"])
    
    # Instatiate
    for sample in mySamples:
        mySample = Sample(sample)
        mySample.send()
        mySample.validate()
        mySample.submit()
    # Eventually get the id / EGAid back into mEGAdata.

# import argparse

# # EXPERIMENTS
# def find_all_experiments():
#     pass

    # Try a submission subset validation
    # validate_subset_submission()
    # submit_subset_submission()

# def validate_subset_submission():
#     mySub.validate_subset()

# def submit_subset_submission():
#     mySub.submit_subset()

# SUBMISSIONS
# def send_submission():
#     # mySub = Submission()
#     globals.mySub.send()

def validate_submission():
    globals.mySub.validate()

def submit_submission():
    globals.mySub.submit()


    Future CLA's (better as args, not options.)
    --delete-all-objects
    --process-rows.
    --validate
    --submit

    # print(f"Operation: {args.operation}")
    # if args.operation and args.operation[0] == "send":

# print(globals.mySub.all_ids("experiments"))
# print(globals.mySub.all_ids("samples"))
# globals.mySub.delete_all_of("experiments")

'''
