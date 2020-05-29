#!/usr/bin/python3
import peewee

# from models import Dataset, Sample, ExperimentType, PublicTrack, Donor, SampleMetadata, SampleProperty
from models import PublicTrack, Dataset, ExperimentType

from trackFile import TrackFile

def main():
    project_names = [
        # "EMC_Asthma", # Coded.
        # "EMC_BluePrint", # Coded, but very little linked.
        # "EMC_Bone", # No datasets - never implemented.
        # "EMC_BrainBank", # Coded, but #TODO: Some of the unmapped NCHiP's are in this project.
        # "EMC_CageKid", # Coded.
        # # "EMC_COPD", # Almost nothing here.  Never implemented.
        # "EMC_Drouin", # Only two samples.  Never implemented.
        # "EMC_iPSC", # Coded, but handled exceptionally in its own method.
        # "EMC_Leukemia", # Coded.
        "EMC_Mature_Adipocytes", # Coded.
        # "EMC_Mitochondrial_Disease", # Coded.
        # "EMC_MSCs", # Coded only enough to generate logs.  Will have to be done seriously, at some point.
        # # "EMC_Primate", # Should this be implemented?
        # # "EMC_Rodent_Brain", # Should this be implemented?
        # "EMC_SARDs", # Coded enough for logs.  Many orphans and unmatched.
        # "EMC_Temporal_Change", #  Coded. 
    ]
    for project_name in project_names:
        # Tracks with dataset match
        print(f"{project_name} tracks with dataset match")
        pt_query = (PublicTrack.select(PublicTrack, Dataset.id, ExperimentType.name)\
            .join(Dataset)\
            .switch(Dataset)\
            .join(ExperimentType)\
            .where((PublicTrack.path.startswith(project_name)) & (PublicTrack.dataset_id.is_null(False))))\
            .order_by(ExperimentType.name, Dataset.id)

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
                        print(f"experiment_type.name: {pt.dataset.experiment_type.name}\t{headers}", end="") # readline already contains a \n
                        col_headers_printed = True
                    # Always print data cols
                    print(f"{pt.file_name}\t{im.readline()}", end="")
                    # print(f"{im.readline()}", end="")
                finally:
                    im.close()
                    previous_experiment_type = pt.dataset.experiment_type.name
            else: # Untested!!!
                print(f"{pt.file_name}\tNo ihec_metrics/.txt available")


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
#         By experiment_type : # [Count of experiment_type (only applicable types)]
#             experiment_type \t ihec_metrics/.txt column headers
#             public_track.file_name \t ihec_metrics/.txt (data cols, iff available)
#     Tracks without dataset match
#         By experiment_type : # [Count of experiment_type (only applicable types)]
#             public_track.file_name \t experiment_type ihec_metrics/.txt column headers
#             \t ihec_metrics/.txt (content only, iff available)
#     Orphan datasets
#         By experiment_type : [Count only of experiment_type (only applicable types)]
