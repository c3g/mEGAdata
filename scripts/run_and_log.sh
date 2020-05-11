#!/bin/bash

# Run and log one EMC project at a time.

# Specify project name in the following files:
# Here, in this file.
# In the main() method of link_public_tracks_to_datasets.py
# In the two .sql query files.

# Generate full log
python link_public_tracks_to_datasets.py 2> log.log

# Variables
# project="EMC_Mature_Adipocytes"
project="EMC_Asthma"
# project="EMC_BrainBank"
# project="EMC_CageKid"
# project="EMC_iPSC"
# project="EMC_Leukemia"
# project="EMC_Mitochondrial_Disease"

dir="logs/${project}/"

# Create the dir, if required.
mkdir -p "${dir}"

# Counts
counts_file="${dir}counts.log"
if [ -f ${counts_file} ] ; then
    rm ${counts_file}
fi
echo "None or multiple corresponding datasets" >> ${counts_file}
grep -c "None or multiple corresponding datasets" log.log >> ${counts_file}
echo "mapping to multiple datasets" >> ${counts_file}
grep -c "mapping to multiple datasets" log.log >> ${counts_file}
echo "Dataset linked" >> ${counts_file}
grep -c "Dataset linked" log.log >> ${counts_file}
echo "No mapping experiment_type.name for" >> ${counts_file}
grep -c "No mapping experiment_type.name for" log.log >> ${counts_file}

# Generate match logs
grep "None or multiple corresponding datasets" log.log > ${dir}noMatch.log
grep "mapping to multiple datasets" log.log > ${dir}multipleMatches.log
grep "Dataset linked" log.log > ${dir}withMatch.log
grep "No mapping experiment_type.name for" log.log > ${dir}rawExperimentTypeMappingProblem.log

# Clean-up
mv log.log ${dir}full.log

#SQL scripts
mysql mEGAdata < findUnlinkedPublicTracks.sql > ${dir}unlinkedPublicTracks.tsv
mysql mEGAdata < findOrphanDatasets.sql > ${dir}orphanDatasets.tsv

# Refresh DB, ready for next time!
# Turn off if you want to see the results of the run script. 
mysql mEGAdata < "/home/assez/sql/megadata-with-addTrackToDB.sql"


