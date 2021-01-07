# -*- coding: future_fstrings -*-
import re
import peewee

from models import PublicTrack, ExperimentType

from trackFile import TrackFile

# Generates a report of all tracks with their respective ihec_metrics/.txt stats.
#
# Merge separate .tsv files as worksheets into one common workbook spreadsheet with:
# ssconvert --merge-to=./reports/ihec_metrics_report.ods ./reports/*.tsv
#
# (Don't worry about any generated errors.)
#
# TODO: This needs more doc.  What/where are the inputs?
#
# Note: Histone files have two separate formats (col definitions) which cannot be munged together.  They are presented in separate worksheets.

def main():
    # Process most (but not all) mEGAdata.experiment_type.names.  Ignore Chipmentation.  mRNA-seq doesn't have any track files.
    et_query = (ExperimentType.select(ExperimentType.name)\
        .where(~ExperimentType.name.startswith("Chipmentation") & ~ExperimentType.name.startswith("mRNA-seq"))\
        .order_by(ExperimentType.name))
    et_results = et_query.execute()
    for et in et_results:
        # Get all the hg38 aligned public tracks.
        # Histones for EMC_Temporal_Change and EMC_Mitochondrial_Disease have a different format, so don't treat them here.
        if re.match("H3K", et.name):
            pt_query = (PublicTrack.select(PublicTrack).where(PublicTrack.path.is_null(False))\
                .where(~PublicTrack.path.startswith("EMC_Mitochondrial_Disease") & ~PublicTrack.path.startswith("EMC_Temporal_Change"))\
                .order_by(PublicTrack.path, PublicTrack.file_name))
            # Write headers and data to a file 
            write_ihec_metrics(pt_query, et.name, et.name)

            # Handle the special case of EMC_Mitochondrial_Disease & EMC_Temporal_Change histones, with their alternate format.
            pt_query = (PublicTrack.select(PublicTrack).where(PublicTrack.path.is_null(False))\
                .where(PublicTrack.path.startswith("EMC_Mitochondrial_Disease") | PublicTrack.path.startswith("EMC_Temporal_Change"))\
                .order_by(PublicTrack.path, PublicTrack.file_name))
            write_ihec_metrics(pt_query, et.name, et.name+"_alternate_metrics")
        else:
            pt_query = (PublicTrack.select(PublicTrack).where(PublicTrack.path.is_null(False))\
                .order_by(PublicTrack.path, PublicTrack.file_name))
            write_ihec_metrics(pt_query, et.name, et.name)

# pt_query: Query yeilding public tracks.
# et_name: mEGAdata.experiment_type.name.
# out_file_name: handle for the tsv.
def write_ihec_metrics(pt_query, et_name, out_file_name):
    pt_results = pt_query.execute()
    # Transform to PublicTrack objects.
    all_track_files = []
    for pt in pt_results:
        track_file = TrackFile.from_PublicTrack(pt)
        if track_file.experiment_type_name == et_name:
            all_track_files.append(track_file)
    
    f = open(f"reports/{out_file_name}.tsv", "wt")
    # Write headers line of the first PublicTrack that has an ihec_metrics/.txt file.
    for tf in all_track_files:
        if tf.ihec_metrics:
            im_file = open(all_track_files[0].ihec_metrics)
            f.write("Project\tPath & File\t" + im_file.readline())
            im_file.close()
            break # Just write headers once.
        else:
            pass

    # For all track files, write data cols.
    for tf in all_track_files:
        # Write the project name, taken from the first token of the TrackFile.path
        match = re.match(r"[\w]+/", tf.path)
        f.write(match.group().rstrip("/", ) + "\t") # Project name
        if tf.ihec_metrics:
            im_file = open(tf.ihec_metrics)
            im_file.readline() # read and discard header line
            f.write(f"{tf.path}/{tf.file_name}\t")
            f.write(im_file.readline()) # write data cols
            im_file.close()
        else:
            f.write(f"{tf.path}/{tf.file_name}\tNo metrics available\n")

    f.close()

if __name__ == "__main__":
  main()
