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
    f = open("out.csv", "w")
    # Spreadsheet Title
    f.write("EMC Community - Unnormalized\n")
    # EGA Object headers
    f.write("Dataset,,,Sample,,,Experiment,,,Run,,,Files\n")
    # Column headers
    f.write("DatasetAlias,ID,EGAD,SampleAlias,ID,EGAN,ExperimentAlias,ID,EGAX,RunAlias,ID,EGAR,File1_Alias,File1_fileName,File1_Checksum,File1_Encrypted_Checksum,File1_ID,File1_EGAF,File2_Alias,File2_fileName,File2_Checksum,File2_Encrypted_Checksum,File2_ID,File2_EGAF\n")

    # Query Dataset, Sample and ExperimentType and Run info
    query = Dataset.select(Dataset, Sample, ExperimentType, Run)\
        .join(Sample)\
        .switch(Dataset).join(ExperimentType)\
        .switch(Dataset).join(Run)\
        .where((Dataset.release_status == "R7") ) # & (Dataset.id == 5072))
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

        # Write Dataset, Sample and ExperimentType and Run info
        f.write(f"{ds.sample.public_name},,,{ds.sample.public_name}.{ds.experiment_type.internal_assay_short_name},,,{ds.sample.public_name}.{ds.experiment_type.internal_assay_short_name}.{ds.run.run}.{ds.run.lane},,,")

        # Query and write the two run_files, to be written on the same line.
        run_file_query = RunFile.select(RunFile).where(RunFile.run_id == ds.run.id)
        run_file_results = run_file_query.execute()
        for rf in run_file_results:
            f.write(f"{rf.name},{rf.name},{rf.md5},{rf.encrypted_md5},,,")
        f.write("\n")
    f.close()


if __name__ == "__main__":
  main()
