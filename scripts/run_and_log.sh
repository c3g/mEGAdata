#!/bin/bash

# Run and log one EMC project at a time (or everything all at once).

# Specify project name in the following files:
# Here, in this file.
# In the main() method list of link_public_tracks_to_datasets.py
# In the two .sql query files referenced below.

# Generate full log
python link_public_tracks_to_datasets.py 2> log.log

# Variables
project="All_EMC"
# project="EMC_Asthma"
# project="EMC_BluePrint"
# project="EMC_BrainBank"
# project="EMC_CageKid"
# project="EMC_iPSC"
# project="EMC_Leukemia"
# project="EMC_Mature_Adipocytes"
# project="EMC_Mitochondrial_Disease"
# project="EMC_MSCs"
# project="EMC_SARDs"
# project="EMC_Temporal_Change"

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
echo "Orphan datasets" >> ${counts_file}
mysql mEGAdata --skip-column-names < findOrphanDatasets.sql | wc -l >> ${counts_file}
mysql mEGAdata < findOrphanDatasets.sql > ${dir}orphanDatasets.tsv


# Refresh DB, ready for next time!
# Turn off if you want to see the results of the run script. 
mysql mEGAdata < "/home/assez/sql/megadata-with-addTrackToDB.sql"


#---------------------------------------------
# Logs may be generated for one project, or all projects (but not some projects).
# Log files are saved to a subdir called $PWD/logs/${project}/
# 
# Log file explanations:
#
# counts.log : Summary counts.  Quite useful.
# full.log : Full output.
# multipleMatches.log : When more than one dataset was matched unexpectedly.
# noMatch.log : Data files that could not be paired.
# orphanDatasets.tsv : Existant datasets that could not be linked to data files.  Best opened in OpenOffice Calc.
# rawExperimentTypeMappingProblem.log : Indicates a problem in map_raw_exp_name_to_exp_type_name()
# unlinkedPublicTracks.tsv : Data files that could not be paired (essentially a repeat of noMatch.log, but more descriptive).
# withMatch.log : Data files successfully linked to mEGAdata dataset metadata.
#
# Note that since these are logs, not pure reports, some tracks (and counts) can be repeated in the logs (such as for link_manual interventions).
