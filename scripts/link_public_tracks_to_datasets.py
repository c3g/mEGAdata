#!/usr/bin/python3
import peewee
import re

from models import Dataset, Sample, ExperimentType, PublicTrack, Donor
from models import User
from logger_settings import logger

# Link public_tracks (data files) to their existant datasets (mEGAdata DB metadata).
def main():
    # Due to variations, it is helpful to handle projects separately.
    project_names = [
        # "EMC_Asthma", # Coded.
        "EMC_BluePrint", # Coded, but very little linked.
        # "EMC_Bone", # No datasets - never implemented.
        # "EMC_BrainBank", # Coded, but #TODO: Some of the unmapped NCHiP's are in this project.
        # "EMC_CageKid", # Coded.
        # "EMC_COPD", # Almost nothing here.  Never implemented.
        # "EMC_Drouin", # Only two samples.  Never implemented.
        # "EMC_iPSC", # Coded, but handled exceptionally in its own method.
        # "EMC_Leukemia", # Coded.
        # "EMC_Mature_Adipocytes", # Coded.
        # "EMC_Mitochondrial_Disease", # Coded.
        # "EMC_MSCs", # Not yet implemented
        # "EMC_Primate", # Not yet implemented.  Should it be?
        # "EMC_Rodent_Brain", # Not yet implemented.  Should it be?
        # "EMC_SARDs", # Not yet implemented.
        # "EMC_Temporal_Change", # Not yet implemented.
    ]
    for project_name in project_names:
        link_project_tracks(project_name)


# project_name takes the form: "EMC_..."
def link_project_tracks(project_name):
    # Get the project's public_tracks
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith(project_name))
    for pt in pt_query:
        if project_name == "EMC_Asthma":
            match = re.match(r"[\w.]+((_Eos)|((ATAC)(Seq)?(CP)?))", pt.file_name) # Need to include the 0.5x case 
            prefix = match.group()
        elif project_name == "EMC_BrainBank":
            # sample.private_name has is a highly variable number of _'s that have been lumped together with the remainder of the public_track.file_name.  It is impossible to know how much of the beginning of the public_track.file_name to use.
            # In EMC_BrainBank, there is a small number of unique third_path_tokens, *mostly* ending in Brain.  Use public_track.filename up until and including this third_path_token to match against the beginning of sample.private_name).
            # Applicable tokens: "BA11_Brain", "BA11", "BA44_Brain", "BA8_BA9", "CE_Brain", "LatAmy_Brain"
            match = re.match(r".*((BA11_Brain)|(BA11)|(BA44_Brain)|(BA8_BA9)|(CE_Brain)|(LatAmy_Brain))", pt.file_name)
            prefix = match.group()
        elif project_name == "EMC_BluePrint": #
            # sample.private_names always end in "_nTC" or "_GR".  Nice!  "_Mono"s follow the pattern, but there are no corresponding sample.private_names.
            match = re.search(r".*_nTC|_GR|_Mono", pt.file_name)
            if match: # match found
                prefix = match.group()
            else: # file_name does not meet the criteria
                continue
        elif project_name == "EMC_CageKid":
            # (1) This project's public_track.file_names often have an extra "_" in them, but the metadata sample.private_names don't.
            match = re.match(r".*Kidney", pt.file_name)
            init_prefix = match.group()
            prefix = re.sub(r"T_1_Kidney", r"T1_Kidney", init_prefix)
            prefix = re.sub(r"T_2_Kidney", r"T2_Kidney", prefix)
            prefix = re.sub(r"N_1_Kidney", r"N1_Kidney", prefix)
            prefix = re.sub(r"N_2_Kidney", r"N2_Kidney", prefix)
        # elif project_name == "EMC_Bone": # No datasets - never implemented.
        # elif project_name == "EMC_COPD": # Almost nothing here.  Never implemented.
        # elif project_name == "EMC_Drouin": # Only two samples.  Never implemented.
        elif project_name == "EMC_iPSC": # Coded, but treat as an exceptional, separate case.
            continue
        elif project_name == "EMC_Leukemia":
            match = re.match(r"\w+Pre{0,1}BC", pt.file_name)
            # if match is not None:
            prefix = match.group()
        elif project_name == "EMC_Mature_Adipocytes":
            # sample.private_name within beginning of public_track.file_name
            # substring up until third "_".  #TODO: This regex could probably be refactored.
            all_ = [m.start() for m in re.finditer(r"_", pt.file_name)]
            prefix = pt.file_name[0: all_[2]]
        elif project_name == "EMC_Mitochondrial_Disease":
            #Prefix definition: Track file_name sometimes contain `_Muscle`, sometimes not.  However, sample.private_name always contains `_Muscle`.
            match = re.match(r"\w{2,3}_", pt.file_name)
            prefix = match.group() + r"Muscle"
        # elif project_name == "EMC_MSCs": # Not yet implemented
        # elif project_name == "EMC_Primate": # Not yet implemented.  Should it be?
        # elif project_name == "EMC_Rodent_Brain": # Not yet implemented.  Should it be?
        # elif project_name == "EMC_SARDs": # Not yet implemented.
        # elif project_name == "EMC_Temporal_Change": # Not yet implemented.
        else:
            logger.critical("Unknown EMC project.  Exiting script.")
            return None

        # Attempt to pair with an existant dataset.
        link_public_track(pt, prefix)

    # Handle manual cases
    if project_name == "EMC_BrainBank":
        link_manually_EMC_BrainBank()
    elif project_name == "EMC_Mature_Adipocytes":
        link_manually_EMC_Mature_Adipocytes()
    # Handle exceptional projects
    elif project_name == "EMC_iPSC":
        link_EMC_iPSC()


# Attempt to pair with an existant dataset.
# Keep this as an independent method to allow filtering of non-human primates.
def link_EMC_iPSC():
    # Only include humans, not the non-human primates, for now.
    pt_query = PublicTrack.select().where(PublicTrack.path.startswith("EMC_iPSC"))
    for pt in pt_query:
        # match = re.match(r"Human_[^_]*", pt.file_name)
        match = re.match(r"Human_\w*_iPS", pt.file_name)
        if match is not None: # Skip the non-human public_tracks, for now.
            prefix = match.group()
            link_public_track(pt, prefix)


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


# (1) sample.private_name within public_track.file_name, based on the project and public_track dependent prefix.
# (2) Links based on raw_experiment_type similar to a known experiment_type (.name, .internal_assay_name or ihec_name).
def link_public_track(pt, prefix):
    # (1) Prefix definition is project dependant - Could pass the project name and put the prefix logic inside this method here.

    # (2) public_track.raw_experiment_type "similar" to a known experiment_type.name.
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


# Note that for link_manual interventions, tracks will be repeated in the logs.

# Aviso and future improvement:
# sample.private_name often follows a format such as: CONCATENATE(donor.private_name, some-kind-of-cell-type)
# When joining on sample.private_name, there is the chance that:
# i) A Donor is shared between projects.
# A check could be made agaist project name.  Using (donor_metadata.value like 'EMC_[project name]%' where donor_property.property = 'project_name') would accomplish this since all donors have been assigned to a normalized project (except EMC_Rodent_Brain, a project which, for now, doesn't matter and has bigger problems.)
# 
# ii) A donor.private_name could be *repeated* between projects (since some donor.private_names are incredibly terse (ie. two digits.)

# No action has been taken since no donor is ever shared between projects and no donor.private_name is ever repeated between projects.  So far.

# However, there is probably no unique project, donor and sample naming constraints implemented so far.
