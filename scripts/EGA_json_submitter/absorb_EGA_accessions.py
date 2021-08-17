# -*- coding: future_fstrings -*-
import os
import sys
import json
import re

# Make models.py accessible in parent dir.
SCRIPTS_ROOT_DIR = os.path.dirname(os.getcwd())
sys.path.append(SCRIPTS_ROOT_DIR)

import peewee
from models import Dataset, Sample, ExperimentType, Run, ReleaseSet#, RunFile

import globals
import utils  # already includes importing globals

# Update DB with EGA accessions from response_jsons/record-EGA-SUBMITTED/ dir.
# Relies on all object aliases following the format in generate_relation_mapping.py.
# Best practice is to run `send.py record-EGA-submitted` immediately prior to this script.
# During alias_increment = True testing to the test Submitter Portal, response_jsons/record-EGA-SUBMITTED/ JSONs aliases must have the same alias_append value as in settings.ini.  During alias_increment = False submissions to the production SP, this is irrelevant.
def main():
    for obj_type in ["samples", "experiments", "runs", "datasets"]: # Maybe add files...
        # Locate & open response file
        try:
            f = open(globals.config["directories"]["response_dir"] + "record-EGA-SUBMITTED/" + f"{obj_type}.json", "r")
        except:
            raise Exception("Failed to open file.")
        # Parse for response result list
        all_response = json.loads(f.read())
        results = all_response["response"]["result"]
        for result in results:
            # Define query, based on obj_type.
            if obj_type == "samples":
                query = Sample.select(Sample).where(Sample.public_name == utils.alias_raw(result["alias"]))
            elif obj_type == "experiments":
                # Parse Experiment by . separator.
                alias_parsed = re.split("\.", result["alias"], 1)
                sample_public_name = alias_parsed[0]
                experiment_type_internal_assay_short_name = utils.alias_raw(alias_parsed[1])
                query = Dataset.select(Dataset).join(Sample).where(Dataset.sample.public_name == sample_public_name)\
                    .switch(Dataset).join(ExperimentType).where(Dataset.experiment_type.internal_assay_short_name == experiment_type_internal_assay_short_name)
            elif obj_type == "runs":
                # Parse Run alias by . separator
                alias_parsed = re.split("\.", utils.alias_raw(result["alias"]))
                sample_public_name = alias_parsed[0]
                experiment_type_internal_assay_short_name = alias_parsed[1]
                run_run = alias_parsed[2]
                run_lane = alias_parsed[3]
                query = Run.select(Run).join(Dataset).join(Sample).where(Run.dataset.sample.public_name == sample_public_name)\
                    .switch(Dataset).join(ExperimentType).where(Run.dataset.experiment_type.internal_assay_short_name == experiment_type_internal_assay_short_name)\
                    .where((Run.run == run_run) & (Run.lane == run_lane))
            elif obj_type == "datasets":
                query = ReleaseSet.select(ReleaseSet).where(ReleaseSet.name == utils.alias_raw(result["alias"]))
            # Ensure only a single DB result returned.  EGA response results are unique Objects with unique accessions; so too should be the DB rows. 
            if query.count() != 1:
                raise Exception(f"{obj_type} query returned more than one result: ({query.count()}) - unique constraint violated.")
            # update DB field with EGA accession
            for row in query.execute():
                if obj_type == "samples":
                    row.ega_egan = result["egaAccessionId"]
                elif obj_type == "experiments":
                    row.ega_egax = result["egaAccessionIds"][0]
                elif obj_type == "runs":
                    row.ega_egar = result["egaAccessionId"]
                elif obj_type == "datasets":
                    row.ega_egad = result["egaAccessionId"]
                if row.save() != 1:
                    raise Exception(f"Failed to save EGA accession to DB for {obj_type} {utils.alias_raw(result['alias'])}.")


if __name__ == "__main__":
    main()