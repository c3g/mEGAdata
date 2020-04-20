#!/usr/bin/python
from __future__ import print_function
import peewee
import re
# For relative imports, modify sys.path
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__)))) # parent directory of pwd
from app import db
from models import Dataset, Sample, ExperimentType, PublicTrack
from models import User

# Defines the logic to link public_tracks (files) to their existant datasets (metadata).
# Handled on a per projects basis.

def main():
    db.set_autocommit(True)

    # user = User.get(User.id==3)
    # print(user.name)
    # user.name = 'Tony Kwan'
    # print(user.save())

    link_EMC_Mature_Adipocytes()

def link_EMC_Mature_Adipocytes():
# Find all EMC_M_A public_tracks
    query = PublicTrack.select().where(PublicTrack.path.startswith('EMC_Mature_adipocytes'))
    for pt in query:
        # substring up until third '_'.
        all_ = [m.start() for m in re.finditer(r"_", pt.file_name)]
        prefix = pt.file_name[0: all_[2]]
        # Foreach, attempt to pair with a existant dataset, based on sample.private_name in file name.
        try:
            ds = Dataset.select(Dataset, Sample).join(Sample, on=(Dataset.sample_id == Sample.id)).where(Sample.private_name == prefix).get()
        except Exception:
            pass # No match found.  Must deal with this case, eventually.
            # print(Exception)
        else:
            pt.dataset = ds # Assign a dataset foreign key.  Can alse be written as pt.dataset = ds.id
            print(pt.save())
            # pt.dataset_id = ds.id # Assign a dataset foreign key.  Can alse be written as pt.dataset = ds.id
            # print(pt.save())

    # Manual pairing:

    # EG006_IA_mADPs two cases of 
    # Compensating for a type (`Stoma`, not `Stroma`)
    ds = (Dataset
            .select(Dataset, Sample)
            .join(Sample)
            .where(Sample.private_name == 'EG006_SC_Stroma')).get()
    pt = PublicTrack.get(PublicTrack.file_name == 'EG006_SC_Stoma_RNASeq_1.forward.bw')
    pt.dataset = ds
    pt.save()

    pt = PublicTrack.get(PublicTrack.file_name == 'EG006_SC_Stoma_RNASeq_1.reverse.bw')
    pt.dataset = ds
    pt.save()

    # Unique case for sample.private_name = EG010_SC_mADPs_1 (first of the ATAC-Seq with two tracks)
    ds = (Dataset
            .select(Dataset, Sample)
            .join(Sample)
            .where(Sample.private_name == 'EG010_SC_mADPs_1')).get()
    pt = PublicTrack.get(PublicTrack.file_name == 'EG010_SC_mADPs_ATACSeqCP_1_peaks.narrowPeak.bb')
    pt.dataset = ds
    pt.save()

    pt = PublicTrack.get(PublicTrack.file_name == 'EG010_SC_mADPs_ATACSeqCP_1.bw')
    pt.dataset = ds
    pt.save()


# Log results
# List linked public_tracks
# List unlinked public_tracks
# List unlinked datasets


if __name__ == "__main__":
  main()
