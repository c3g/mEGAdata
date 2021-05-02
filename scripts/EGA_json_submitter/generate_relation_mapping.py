# -*- coding: future_fstrings -*-
import os
import sys

# Make models.py accessible in parent dir.
SCRIPTS_ROOT_DIR = os.path.dirname(os.getcwd())
sys.path.append(SCRIPTS_ROOT_DIR)

import peewee
from models import Dataset, Sample, ExperimentType, Run, RunFile, DatasetToReleaseSet, ReleaseSet

# Generate a relationMapping.ods from the mEGAdata DB, for a given dataset.release_status (R1, R2, R3, etc.)
# This relationMapping.ods is an unnormalizion of the dataset, sample, experiment, run and run_files tables and serves as an input for submissions to EGA.

def main():
    # Write all that header info.
    f = open("relationMapping.csv", "w")
    # Spreadsheet Title
    f.write("EMC Community - Unnormalized\n")
    f.write("Template columns must be manually filled in with the name of the JSON file.\n")
    # EGA Object headers
    f.write("Dataset,,,Sample,,,Experiment,,,Run,,Files\n")
    # Column headers
    f.write("Dataset_alias,Dataset_template,EGAD,Sample_alias,Sample_template,EGAN,Experiment_alias,Experiment_template,EGAX,Run_alias,EGAR,File1_fileName,File1_checksum,File1_encrypted_checksum,File1_EGAF,File2_fileName,File2_checksum,File2_encrypted_checksum,File2_EGAF\n")

    # Query Dataset, Sample and ExperimentType and Run info
    query = Dataset.select(Dataset, Sample, ExperimentType, Run)\
        .join(Sample)\
        .switch(Dataset).join(ExperimentType)\
        .switch(Dataset).join(Run)\
        .where((Dataset.release_status == "R7") ) # & (Dataset.id == 5072))
    # TODO: Really need to make R7 a CLA!!!
    results = query.execute()
    for ds in results:
        # Query and write the release_set (aka, the EGA Dataset)
        dtrs_query = DatasetToReleaseSet.select(DatasetToReleaseSet, ReleaseSet, Dataset)\
            .join(ReleaseSet)\
            .switch(DatasetToReleaseSet)\
            .join(Dataset).where(Dataset.id == ds.id)
        dtrs_results = dtrs_query.execute()
        for dtrs in dtrs_results:
            f.write(f"{dtrs.release_set.name},,,")

        # Write Sample, ExperimentType and Run info
        f.write(f"{ds.sample.public_name},,,{ds.sample.public_name}.{ds.experiment_type.internal_assay_short_name},,,{ds.sample.public_name}.{ds.experiment_type.internal_assay_short_name}.{ds.run.run}.{ds.run.lane},,")

        # Query and write the two run_files, to be written on the same line.
        run_file_query = RunFile.select(RunFile).where(RunFile.run_id == ds.run.id)
        run_file_results = run_file_query.execute()
        for rf in run_file_results:
            f.write(f"{rf.name},{rf.md5},{rf.encrypted_md5},,")
        f.write("\n")
    f.close()


if __name__ == "__main__":
  main()
