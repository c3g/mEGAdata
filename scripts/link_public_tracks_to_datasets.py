#!/usr/bin/python3
import peewee
import re

from models import Dataset, Sample, ExperimentType, PublicTrack, Donor
from models import User
from logger_settings import logger

# Link public_tracks (data files) to their existant datasets (metadata).

def main():
    # Due to variations, handle each project separately.

    # link_EMC_Mature_Adipocytes()
    # link_EMC_BrainBank()
    # link_EMC_CageKid()
    # link_EMC_iPSC()
    # link_EMC_Leukemia()
    link_EMC_Mitochondrial_Disease()

# Attempt to pair with an existant dataset.
def link_EMC_Mature_Adipocytes():
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_Mature_adipocytes"))

    for pt in pt_query:
        # sample.private_name within beginning of public_track.file_name
        # substring up until third "_".  #TODO: This regex could probably be refactored.
        all_ = [m.start() for m in re.finditer(r"_", pt.file_name)]
        prefix = pt.file_name[0: all_[2]]

        link_public_track(pt, prefix)

    # Handle the unlinked exceptional cases.
    link_manually_EMC_Mature_Adipocytes()


# Attempt to pair with an existant dataset.
# #TODO: Some of the unmapped NCHiP's are in this project.
def link_EMC_BrainBank():
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_BrainBank"))
    for pt in pt_query:
        # sample.private_name has is a highly variable number of _'s that have been lumped together with the remainder of the public_track.file_name.  It is impossible to know how much of the beginning of the public_track.file_name to use.
        # In EMC_BrainBank, there is a small number of unique third_path_tokens, *mostly* ending in Brain.  Use public_track.filename up until and including this third_path_token to match against the beginning of sample.private_name).
        # Applicable tokens: "BA11_Brain", "BA11", "BA44_Brain", "BA8_BA9", "CE_Brain", "LatAmy_Brain"
        
        match = re.search(r".*((BA11_Brain)|(BA11)|(BA44_Brain)|(BA8_BA9)|(CE_Brain)|(LatAmy_Brain))", pt.file_name)
        prefix = match.group()
        # logger.debug(f"prefix: {prefix}")

        link_public_track(pt, prefix)

    # Handle some unlinked exceptional cases.
    link_manually_EMC_BrainBank()


# Attempt to pair with an existant dataset.
def link_EMC_CageKid():
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_CageKid"))
    for pt in pt_query:
        # (1) This project's public_track.file_names often have an extra "_" in them, but the metadata sample.private_names don't.
        match = re.search(r".*Kidney", pt.file_name)
        init_prefix = match.group()
        prefix = re.sub(r"T_1_Kidney", r"T1_Kidney", init_prefix)
        prefix = re.sub(r"T_2_Kidney", r"T2_Kidney", prefix)
        prefix = re.sub(r"N_1_Kidney", r"N1_Kidney", prefix)
        prefix = re.sub(r"N_2_Kidney", r"N2_Kidney", prefix)
        
        link_public_track(pt, prefix)

    # No manually linkable cases found.
    # link_manually_EMC_CageKid()


# Attempt to pair with an existant dataset.
def link_EMC_iPSC():
    # Only include humans, not the non-human primates, for now.
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_iPSC"))
    for pt in pt_query:
        # match = re.search(r"Human_[^_]*", pt.file_name)
        match = re.search(r"Human_\w*_iPS", pt.file_name)
        if match is not None: # Skip the non-human public_tracks, for now.
            prefix = match.group()
            link_public_track(pt, prefix)


# Attempt to pair with an existant dataset.
def link_EMC_Leukemia():
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_Leukemia"))
    for pt in pt_query:
        match = re.search(r"\w+Pre{0,1}BC", pt.file_name)
        # if match is not None:
        prefix = match.group()
        link_public_track(pt, prefix)


# Attempt to pair with an existant dataset.
def link_EMC_Mitochondrial_Disease():
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_Mitochondrial_Disease"))
    for pt in pt_query:
        #Prefix definition: Track file_name sometimes contain `_Muscle`, sometimes not.  However, sample.private_name always contain `_Muscle`.
        match = re.match(r"\w{2,3}_", pt.file_name) #re.match() since we are looking from the beginning of the string, not within.  Probably the case for all other projects too.  #TODO - should change all re.search() to re.match().
        # prefix = match.group().strip("_")
        prefix = match.group() + r"Muscle"
        link_public_track(pt, prefix)


# Handle some tricky cases manually.
def link_manually_EMC_Mature_Adipocytes():
    # Manual pairing:
    # EG006_IA_mADPs two cases.  Compensating for a typo (`Stoma`, not `Stroma`)
    ds = (Dataset.select(Dataset, Sample)
        .join(Sample).where(Sample.private_name == "EG006_SC_Stroma")).get()
        # TODO: verify against experiment_type.name; ensure only one dataset returned.
    pt = PublicTrack.get(PublicTrack.file_name == "EG006_SC_Stoma_RNASeq_1.forward.bw")
    pt.dataset = ds
    logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}.  Saved: {pt.save()}")

    pt = PublicTrack.get(PublicTrack.file_name == "EG006_SC_Stoma_RNASeq_1.reverse.bw")
    pt.dataset = ds
    logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}.  Saved: {pt.save()}")

    # Unique case for sample.private_name = EG010_SC_mADPs_1 (first of the ATAC-Seq with two tracks).
    # There is only one dataset associated with this sample. (No need to check against experiment_type.name.)
    ds = (Dataset.select(Dataset, Sample)
        .join(Sample).where(Sample.private_name == "EG010_SC_mADPs_1")).get()
    pt = PublicTrack.get(PublicTrack.file_name == "EG010_SC_mADPs_ATACSeqCP_1_peaks.narrowPeak.bb")
    pt.dataset = ds
    logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}.  Saved: {pt.save()}")

    # Second track
    pt = PublicTrack.get(PublicTrack.file_name == "EG010_SC_mADPs_ATACSeqCP_1.bw")
    pt.dataset = ds
    logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}.  Saved: {pt.save()}")


# Treat exceptional cases manually.
def link_manually_EMC_BrainBank():
    # Manual pairing to compensate for an abbreviation ("Pl11" versus "Pool11") in 2 experiment_type.names.
    # Note: There is an experiment_type.name for ChIP, but not ChIP2, as in the file name.
    #TODO: Ask whether to use it?
    '''
    ds_query = (Dataset.select(Dataset, Sample, ExperimentType)
        .join(Sample).where(Sample.private_name == "134_171_225_227_Pool11_LatAmy_Brain")
        .switch(Dataset).join(ExperimentType).where(ExperimentType.internal_assay_short_name == "ChIP_H3K36me3")) # Need to use ExperimentType.internal_assay_short_name here.
    if ds_query.count() != 1:
        logger.warning(f"None or multiple corresponding datasets, {ds_query.count()}")
    else:
        result = ds_query.execute()
        pt_file_names = ["134_171_225_227_Pl11_LatAmy_Brain_ChIP2_H3K36me3_1.bw",
            "134_171_225_227_Pl11_LatAmy_Brain_ChIP2_H3K36me3_1_peaks.broadPeak.bb"]
        for ds in result:
            for pt_f_n in pt_file_names:
                pt = PublicTrack.get(PublicTrack.file_name == pt_f_n)
                pt.dataset = ds.id
                logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}. Saved: {pt.save()}")
    '''
    ds_query = (Dataset.select(Dataset, Sample, ExperimentType)
        .join(Sample).where(Sample.private_name == "134_171_225_227_Pool11_LatAmy_Brain")
        .switch(Dataset).join(ExperimentType).where(ExperimentType.internal_assay_short_name == "ChIP_H3K27me3")) # Need to use ExperimentType.internal_assay_short_name here.
    if ds_query.count() != 1:
        logger.warning(f"None or multiple corresponding datasets, {ds_query.count()}")
    else:
        result = ds_query.execute()
        pt_file_names = ["134_171_225_227_Pl11_LatAmy_Brain_ChIP_H3K27me3_1.bw",
            "134_171_225_227_Pl11_LatAmy_Brain_ChIP_H3K27me3_1_peaks.broadPeak.bb"]
        for ds in result:
            for pt_f_n in pt_file_names:
                pt = PublicTrack.get(PublicTrack.file_name == pt_f_n)
                pt.dataset = ds.id
                logger.info(f"Dataset linked manually for public_track {pt.file_name} to {ds.id}.  Saved: {pt.save()}")


# (1) sample.private_name within public_track.file_name, based on the project and public_track dependent prefix.
# (2) Links based on raw_experiment_type similar to a known experiment_type (.name, .internal_assay_name or ihec_name).
def link_public_track(pt, prefix):
    # Prefix definition is project dependant - Could pass the project name and put the prefix logic inside this method here.

    # public_track.raw_experiment_type "similar" to a known experiment_type.name.
    exp_t_name = map_raw_exp_name_to_exp_type_name(pt.raw_experiment_type)

    ds_query = Dataset.select(Dataset, Sample.private_name, ExperimentType.name)\
        .join(Sample).where(Sample.private_name == prefix)\
        .switch(Dataset).join(ExperimentType).where(ExperimentType.name == exp_t_name)

    # Match to (hopefully) a single dataset
    if ds_query.count() != 1:
        logger.warning(f"None or multiple corresponding datasets, {ds_query.count()}, found for {pt.file_name}")
        for dataset in ds_query.execute():
            logger.error(f"{pt.file_name} mapping to multiple datasets: {dataset.id}")
    else:  # One single dataset found
        result = ds_query.execute()
        for dataset in result:
            pt.dataset = dataset.id  # Can also be written as pt.dataset = ds OR pt.dataset_id = ds.id
            logger.info(f"Dataset linked for public_track {pt.file_name}. Saved: {pt.save()}")


# Maps public_track.raw_experiment_type to experiment_type.name, in a slightly fuzzy manner.
def map_raw_exp_name_to_exp_type_name(raw_experiment_type):
    if re.search(r"ATAC", raw_experiment_type) is not None:
        return "ATAC-seq"
    elif re.search(r"^BS", raw_experiment_type) is not None:
        return "Bisulfite-seq"
    elif re.search(r"^CM", raw_experiment_type) is not None:
        # return "capture Methylome"
        return "Capture Methylome"  # I think this was supposed to be capitalized.
    elif re.search(r"ChIP_Input", raw_experiment_type) is not None:
        return "ChIP-Seq Input"
    elif re.search(r"^chipmentation_", raw_experiment_type) is not None:
        res = re.search(r"H3K[\w]*", raw_experiment_type)
        return "Chipmentation_" + res.group()
    elif re.search(r"H3K\d{1,2}(me\d|ac)", raw_experiment_type) is not None and re.search(r"NChIP", raw_experiment_type) is None:
        res = re.search(r"H3K\d{1,2}(me\d|ac)", raw_experiment_type)
        return res.group()
    elif re.search(r"^RNASeq", raw_experiment_type) is not None:
        return "RNA-seq"
    elif re.search(r"^smRNASeq", raw_experiment_type) is not None:
        return "smRNA-seq"
    # TODO - Still must handle NChIP and Tagmentation cases.
    else:
        logger.warning(f"No mapping experiment_type.name for {raw_experiment_type}.")
        return "unmatched"


if __name__ == "__main__":
  main()


# Note that for link_manual interventions, logs will include tracks multiple times.

# Aviso and future improvement:
# sample.private_name often follows a format such as: CONCATENATE(donor.private_name, some-kind-of-cell-type)
# When joining on sample.private_name, there is the chance that:
# i) A Donor is shared between projects.
# A check could be made agaist project name.  Using (donor_metadata.value like 'EMC_[project name]%' where donor_property.property = 'project_name') would accomplish this since all donors have been assigned to a normalized project (except EMC_Rodent_Brain, a project which, for now, doesn't matter and has bigger problems.)
# 
# ii) A donor.private_name could be *repeated* between projects (since some donor.private_names are incredibly terse (ie. two digits.)

# No action has been taken since no donor is ever shared between projects and no donor.private_name is ever repeated between projects.  So far.

# However, there is probably no unique project, donor and sample naming constraints implemented so far.
