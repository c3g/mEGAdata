#!/usr/bin/python3
import peewee

# from models import Dataset, Sample, ExperimentType, PublicTrack, Donor, SampleMetadata, SampleProperty
from models import PublicTrack, Dataset, ExperimentType

from trackFile import TrackFile

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
    for project_name in project_names:
        # Tracks with dataset match
        print(f"{project_name} tracks WITH dataset match")
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
                        print(f"experiment_type.name: {pt.dataset.experiment_type.name}\t{headers}", end="") # im.readline already contains a \n
                        col_headers_printed = True
                    # Always print data cols
                    print(f"{pt.file_name}\t{im.readline()}", end="")
                finally:
                    im.close()
                    previous_experiment_type = pt.dataset.experiment_type.name
            else:
                if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                    print(f"experiment_type.name: {pt.dataset.experiment_type.name}")
                    col_headers_printed = False
                    previous_experiment_type = pt.dataset.experiment_type.name
                print(f"{pt.file_name}\tNo ihec_metrics/.txt available")

        # Tracks without dataset match.
        # Kinda an ugly copy & paste of the "Tracks WITH dataset match" bit, but there are enough necessary differences.
        print(f"{project_name} tracks WITHOUT dataset match")
        pt_query = (PublicTrack.select(PublicTrack)
            .where((PublicTrack.path.startswith(project_name)) & (PublicTrack.dataset_id.is_null(True)))\
            .order_by(PublicTrack.file_name))

        pt_results = pt_query.execute()
        col_headers_printed = False
        previous_experiment_type = None

        #  Need a list of results, sorted by TrackFile.experiment_type_name
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
                        print(f"experiment_type_name: {my_track_file.experiment_type_name}\t{headers}", end="") # im.readline already contains a \n
                        col_headers_printed = True
                    # Always print data cols
                    print(f"{my_track_file.file_name}\t{im.readline()}", end="")
                finally:
                    im.close()
                    previous_experiment_type = my_track_file.experiment_type_name
            else:
                if col_headers_printed is False or current_experiment_type != previous_experiment_type:
                    print(f"experiment_type_name: {my_track_file.experiment_type_name}")
                    col_headers_printed = False
                    previous_experiment_type = my_track_file.experiment_type_name
                print(f"{my_track_file.file_name}\tNo ihec_metrics/.txt available")


if __name__ == "__main__":
  main()

# ------------------------------
# ihec_metrics_report format
# ------------------------------
#
# Creates a .tsv file, suitable to opening as a spreadsheet.
#
# By project
#     Tracks with dataset match
#         By experiment_type.name
#             experiment_type \t ihec_metrics/.txt column headers
#             public_track.file_name \t ihec_metrics/.txt (data cols, iff available)
#     Tracks without dataset match
#         By experiment_type_name
#             experiment_type \t ihec_metrics/.txt column headers
#             public_track.file_name \t ihec_metrics/.txt (data cols, iff available)
#     Orphan datasets
#         By experiment_type : [Count only of experiment_type (only applicable types)]
