#!/bin/bash

# Run and log one EMC project at a time.


# Refresh DB
mysql mEGAdata < "/home/assez/sql/megadata-with-addTrackToDB.sql"

# Generate full log
python link_public_tracks_to_datasets.py 2> log.log

# Variables
# project="EMC_BrainBank"
project="EMC_Mature_Adipocytes"
dir="logs/${project}/"

# Create the dir
mkdir -p "${dir}"

# Counts
counts_file="${dir}counts.log"
if [ -f ${counts_file} ] ; then
    rm ${counts_file}
fi
echo "None or multiple corresponding" >> ${counts_file}
grep -c "None or multiple corresponding" log.log >> ${counts_file}
echo "mapping to all of:" >> ${counts_file}
grep -c "mapping to all of:" log.log >> ${counts_file}
echo "Dataset linked" >> ${counts_file}
grep -c "Dataset linked" log.log >> ${counts_file}
echo "No mapping experiment_type.name for" >> ${counts_file}
grep -c "No mapping experiment_type.name for" log.log >> ${counts_file}

# Generate match logs
grep "None or multiple corresponding" log.log > ${dir}noMatch.log
grep "mapping to all of:" log.log > ${dir}multipleMatches.log
grep "Dataset linked" log.log > ${dir}withMatch.log
grep "No mapping experiment_type.name for" log.log > ${dir}rawExperimentTypeProblem.log

# Clean-up
mv log.log ${dir}full.log

#SQL scripts
mysql mEGAdata < findUnlinkedPublicTracks.sql > ${dir}unlinkedPublicTracks.tsv
mysql mEGAdata < findOrphanDatasets.sql > ${dir}orphanDatasets.tsv


