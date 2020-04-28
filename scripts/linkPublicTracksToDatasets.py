#!/usr/bin/python3
import peewee
import re

from models import Dataset, Sample, ExperimentType, PublicTrack
from models import User
from logger_settings import logger

# Defines the logic to link public_tracks (files) to their existant datasets (metadata).

def main():
    # Handle each project separately

    link_EMC_Mature_Adipocytes()

def link_EMC_Mature_Adipocytes():
    # Find all EMC_Mature_Adipocytes public_tracks
    query = PublicTrack.select().where(PublicTrack.path.startswith('EMC_Mature_adipocytes'))
    # Attempt to pair with a existant dataset, based on (1) sample.private_name within public_track.file_name and (2) raw_experiment_type similar to a known experiment_type.
    for pt in query:
        # (1) sample.private_name within public_track.file_name
        # substring up until third '_'.  #TODO: This regex could probably be refactored.
        all_ = [m.start() for m in re.finditer(r"_", pt.file_name)]
        prefix = pt.file_name[0: all_[2]]
        # (2) public_track.raw_experiment_type "similar" to a known experiment_type.name.
        exp_t_name = map_raw_exp_name_to_exp_type_name(pt.raw_experiment_type)

        # Match to (hopefully) a single dataset
        query = Dataset.select(Dataset, Sample.private_name, ExperimentType.name).join(Sample).where(Sample.private_name == prefix).switch(Dataset).join(ExperimentType).where(ExperimentType.name == exp_t_name)
        if query.count() > 1:
            logger.warning("Multiple corresponding datasets found for %s.", pt.file_name)
        elif query.count() < 1: # == -1: # Error
            logger.warning('No corresponding dataset found for %s.', pt.file_name)
        else:
            result = query.execute()
            for dataset in result:
                pt.dataset = dataset.id # Can also be written as pt.dataset_id = ds.id
                logger.info('Dataset linked for public_track %s: %s.', pt.file_name, pt.save())

        # # Match to a single dataset
        # try:
        #     # Working # ds = Dataset.select(Dataset, Sample).join(Sample, on=(Dataset.sample_id == Sample.id)).where(Sample.private_name == prefix).get()
        #     query = Dataset.select(Dataset, Sample.private_name, ExperimentType.name).join(Sample).where(Sample.private_name == prefix).switch(Dataset).join(ExperimentType).where(ExperimentType.name = exp_t_name)
        #     results = query.execute()
        # except Exception:
        #     pass # No match found.  Does the metadata exist somewhere outside the database?  Probably not.
        #     logger.warning('No corresponding dataset found for %s.', pt.file_name)
        # else:
        #     pt.dataset = ds # Works best # Assign a dataset foreign key.  Can also be written as pt.dataset = ds.id OR pt.dataset_id = ds.id
        #     logger.info('Dataset linked for public_track %s: %s.', pt.file_name, pt.save())


    # Manual pairing:
    # EG006_IA_mADPs two cases.  Compensating for a typo (`Stoma`, not `Stroma`)
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


def map_raw_exp_name_to_exp_type_name(raw_experiment_type):
    if re.search(r"ATAC", raw_experiment_type) is not None:
        return "ATAC-seq"
    elif re.search(r"^BS", raw_experiment_type) is not None:
        return "Bisulfite-seq"
    elif re.search(r"^CM", raw_experiment_type) is not None:
        return "capture Methylome"
    elif re.search(r"ChIP_Input", raw_experiment_type) is not None:
        return "ChIP-Seq Input"
    elif re.search(r"^chipmentation_", raw_experiment_type) is not None:
        res = re.search(r"H3K[\w]*", raw_experiment_type)
        return "Chipmentation_" + res.group()
    elif re.search(r"NChIP", raw_experiment_type) is None and re.search(r"H3K\d{1,2}(me\d|ac)", raw_experiment_type) is not None:
        res = re.search(r"H3K\d{1,2}(me\d|ac)", raw_experiment_type)
        return res.group()
    elif re.search(r"^RNASeq", raw_experiment_type) is not None:
        return "RNA-seq"
    elif re.search(r"^smRNASeq", raw_experiment_type) is not None:
        return "smRNA-seq"
    # TODO - Still must handle NChIP and Tagmentation cases.
    else:
        logger.warning("No mapping for " + raw_experiment_type)
        return "unmatched"

# List unlinked datasets - I don't think this is possible.  Requires completeness.  Maybe do it in SQL at the end.


if __name__ == "__main__":
  main()
