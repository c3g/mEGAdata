# -*- coding: future_fstrings -*-
import os
import sys
import json

# Make models.py accessible in parent dir.
SCRIPTS_ROOT_DIR = os.path.dirname(os.getcwd())
sys.path.append(SCRIPTS_ROOT_DIR)

import peewee
from models import Dataset, Sample, ExperimentType, Run, RunFile, DatasetToReleaseSet, ReleaseSet

import globals
import utils  # already includes importing globals

# parse record-EGA-objects (once SUBMITTED)
# How tightly should this be integrated with other scripts?

# Check uniqueness indexes on individual DB tables too.
def main():
    '''
    foreach objType
        foreach obj
            get Object from DB (based on unique alias criteria and joins.)
            common:
            Ensure it is only 1, since there is only one EGA obj.
            update DB with accession.
    '''

    # samples
    for obj_type in ["samples", "experiments", "runs", "datasets"]:  # Maybe add files...
        # Locate & open response file
        f = open(globals.config["directories"]["response_dir"] + "record-EGA-SUBMITTED/" + f"{obj_type}.json", "r")
        # Parse for accessions
        all_response = json.loads(f.read())
        results = all_response["response"]["result"]
        for result in results:
            # if obj_type != "experiments":
            #     print(f"{obj_type} - Alias: {result['alias']} => Accession: {result['egaAccessionId']}")  # GOOD!
            # else: # For experiments, use egaAccessionIds[0], not egaAccessionId.
            #     print(f"{obj_type} - Alias: {result['alias']} => Accession: {result['egaAccessionIds'][0]}")  # GOOD!
            # Switch on obj_type to define query.
            if obj_type == "samples":
                query = Sample.select(Sample).where(Sample.public_name == utils.alias_raw(result["alias"]))
            if obj_type == "experiments"
                # {ds.sample.public_name}.{ds.experiment_type.internal_assay_short_name}
                # Need to reliably parse Experiment according to a separator.
                query = Dataset.select(Dataset).join(Sample).where(Dataset.Sample.public_name.concat(Dataset.)== utils.alias_raw(result["alias"]))
            # if obj_type == "runs"
            #     query = Run.select()
            # if obj_type == "datasets"
            #     query = Datasets.select()
            print(utils.alias_raw(result["alias"]))
            print(query.count())
    # experiments

    # datasets

    # runs

    # files?

    # Might be able to generalize this into methods.
    # Do something about the auto_increment

# This is going to be a problem if the settings.ini has been autoincremented already, in a previous submission.
# Note that is only works for the current Submission, or on prod?  Ugly.
# Strip the alias of any autoincrement.  Used for lookup in the obj_registries.
# def alias_raw(alias):
#     if globals.config.getboolean("global", "alias_increment"):
#         return alias.replace("_" + globals.config["global"]["alias_append"], "")
#     else:
#         return alias


if __name__ == "__main__":
    main()