# -*- coding: future_fstrings -*-
import peewee
# from peewee import fn, JOIN
from settings import db

from models import PublicTrack, Dataset, ExperimentType

from trackFile import TrackFile

# Generates a report of all tracks with their respective ihec_metrics/.txt stats.
#
# See prerequisites in find_ihec_metrics.py
#
# See bottom of this file for report formatting.
#
# This script is deprecated in favour of ihec_metrics_report.py

def main():
    project_names = [
        "EMC_Asthma", # Coded.
        "EMC_BluePrint", # Coded, but very little linked.
        # "EMC_Bone", # No datasets - never implemented.
        "EMC_BrainBank", # Coded, but #TODO: Some of the unmapped NCHiP's are in this project.
        "EMC_CageKid", # Coded.
        # "EMC_COPD", # Almost nothing here.  Never implemented.
        # "EMC_Drouin", # Only two samples.  Never implemented.
        "EMC_iPSC", # Coded, but handled exceptionally in its own method.
        "EMC_Leukemia", # Coded.
        "EMC_Mature_Adipocytes", # Coded.
        "EMC_Mitochondrial_Disease", # Coded.
        "EMC_MSCs", # Coded only enough to generate logs.  Will have to be done seriously, at some point.
        # "EMC_Primate", # Should this be implemented?
        # "EMC_Rodent_Brain", # Should this be implemented?
        "EMC_SARDs", # Coded enough for logs.  Many orphans and unmatched.
        "EMC_Temporal_Change", #  Coded. 
    ]
    print(f"EMC ihec_metrics")
    print(f"Use this file with AutoFilter to filter by 1) project_name and 2) experiment_type.name (though always display row when experiment_type.name is empty so as to include WITH / WITHOUT / UNMATCHED title info.)")
    for project_name in project_names:
        # Tracks with dataset match
        print(f"\n{project_name}\t\tTracks WITH dataset match")
        pt_query = (PublicTrack.select(PublicTrack, Dataset.id, ExperimentType.name)\
            .join(Dataset)\
            .switch(Dataset)\
            .join(ExperimentType)\
            .where((PublicTrack.path.startswith(project_name)) & (PublicTrack.dataset_id.is_null(False))))\
            .order_by(ExperimentType.name, PublicTrack.file_name)

        pt_results = pt_query.execute()
        col_headers_printed = False
        previous_experiment_type = None
        for pt in pt_results:
            my_track_file = TrackFile.from_PublicTrack(pt)
            current_experiment_type = pt.dataset.experiment_type.name # Current experiment_type.name, used to determine if col headers need to be printed again.
            if my_track_file.ihec_metrics:
                try:
                    im = open(my_track_file.ihec_metrics, "r")
                except OSError:
                    print("Cannot open ihec_metrics/ .txt file")
                else:
                    headers = im.readline()
                    # Only print col headers once.
                    if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                        print(f"{project_name}\t{pt.dataset.experiment_type.name}\t\t{headers}", end="") # im.readline already contains a \n
                        col_headers_printed = True
                    # Always print data cols
                    print(f"{project_name}\t{pt.dataset.experiment_type.name}\t{pt.file_name}\t{im.readline()}", end="")
                finally:
                    im.close()
                    previous_experiment_type = pt.dataset.experiment_type.name
            else:
                # if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                #     # print(f"{project_name}\t{pt.dataset.experiment_type.name}\t", end="")
                #     col_headers_printed = False
                #     previous_experiment_type = pt.dataset.experiment_type.name
                print(f"{project_name}\t{pt.dataset.experiment_type.name}\t{pt.file_name}\tNo ihec_metrics/.txt available")

        # Tracks without dataset match.
        # Kinda an ugly copy & paste of the "Tracks WITH dataset match" bit, but there are enough necessary differences.
        print(f"\n{project_name}\t\tTracks WITHOUT dataset match")
        pt_query = (PublicTrack.select(PublicTrack)
            .where((PublicTrack.path.startswith(project_name)) & (PublicTrack.dataset_id.is_null(True)))\
            .order_by(PublicTrack.file_name))

        pt_results = pt_query.execute()
        col_headers_printed = False
        previous_experiment_type = None

        # Need a list of results, sorted by TrackFile.experiment_type_name
        my_track_files = []
        for pt in pt_results:
            my_track_files.append(TrackFile.from_PublicTrack(pt))
        my_track_files.sort(key=lambda x: x.experiment_type_name)
        # ut.sort(key=lambda x: x.count, reverse=True)
        for my_track_file in my_track_files:
            current_experiment_type = my_track_file.experiment_type_name # Current experiment_type_name, used to determine if col headers need to be printed again.
            if my_track_file.ihec_metrics:
                try:
                    im = open(my_track_file.ihec_metrics, "r")
                except OSError:
                    print("Cannot open ihec_metrics/ .txt file")
                else:
                    headers = im.readline()
                    # Only print col headers once.
                    if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                        print(f"{project_name}\t{my_track_file.experiment_type_name}\t\t{headers}", end="") # im.readline already contains a \n
                        col_headers_printed = True
                    # Always print data cols
                    print(f"{project_name}\t{my_track_file.experiment_type_name}\t{my_track_file.file_name}\t{im.readline()}", end="")
                finally:
                    im.close()
                    previous_experiment_type = my_track_file.experiment_type_name
            else:
                # if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                #     # print(f"{project_name}\t{my_track_file.experiment_type_name}\t", end="")
                #     col_headers_printed = False
                #     previous_experiment_type = my_track_file.experiment_type_name
                print(f"{project_name}\t{my_track_file.experiment_type_name}\t{my_track_file.file_name}\tNo ihec_metrics/.txt available")

        # Orphan datasets, grouped by experiment_type.  Counts only.
        # Based on ./findOrphanDatasets.sql
        # Kinda ugly to drop down into raw SQL, but Peewee didn't like the complexity required.
        print(f"\n{project_name}\t\tDatasets unmatched to tracks")
        cursor = db.execute_sql(f"select et.name, count(*) "\
            f"FROM donor d, donor_metadata dm, donor_property dp, sample s, experiment_type et, dataset ds "\
            f"LEFT OUTER JOIN public_track pt on (ds.id = pt.dataset_id AND pt.assembly = 'hg38' AND pt.id >= 2859) "\
            f"WHERE dm.donor_id = d.id and dm.donor_property_id = dp.id and s.donor_id = d.id and ds.sample_id = s.id "\
            f"and et.id = ds.experiment_type_id and dp.property = 'project_name' and dm.value = '{project_name}' "\
            # pt.id is null identifies only the orphaned datasets
            f"and pt.id is null "\
            f"group by et.name")
        for row in cursor.fetchall():
            print(f"{project_name}\t{row[0]}\t{row[1]}")


if __name__ == "__main__":
  main()

# ------------------------------
# ihec_metrics_one_page_report format
# ------------------------------
#
# Creates a .tsv file, suitable to opening as a spreadsheet.
# The intention is to use the AutoFilter to filter by 1) project_name and 2) experiment_type.name (though always display row when experiment_type.name is empty for WITH / WITHOUT / UNMATCHED info.)
#
# Column def's
# project_name, experiment_type.name, file_name, headers/data/no_metrics
# 
# By project
#     Tracks WITH dataset match
#         By experiment_type.name
#             project_name, experiment_type.name, \t, ihec_metrics/.txt column headers
#             project_name, experiment_type.name, public_track.file_name, ihec_metrics/.txt (data cols, iff available)
#     Tracks WITHOUT dataset match
#         By experiment_type_name
#             project_name, TrackFile.experiment_type_name, \t, ihec_metrics/.txt column headers
#             project_name, TrackFile.experiment_type_name, TrackFile.file_name, ihec_metrics/.txt (data cols, iff available)
#     Datasets unmatched to tracks
#         By experiment_type:
#             project_name, experiment_type.name, count(of experiment_type) (only applicable types) 
