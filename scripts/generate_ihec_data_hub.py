import json
import datetime
import peewee
import re

from models import PublicTrack, Dataset, Sample, ExperimentType, ExperimentMetadata, ExperimentProperty
from models import SampleMetadata, SampleProperty, Donor, DonorMetadata, DonorProperty

# Generates an IHEC data hub for all successfully linked public tracks.

class Hub:
    def __init__(self):
        self.data = {
            "datasets": {},
            "hub_description": {},
            "samples": {},
            }

    def jsonify(self):
        # Legible and pretty representation
        return json.dumps(self.data, indent=4, sort_keys=True)

class Analysis_Attributes:
    # Vales taken from GenPipes 3.1.0 base.ini files.
    # et_name is experiment_type.name.
    def __init__(self, et_name=""):
        if re.match("H3K", et_name) or re.search("Input", et_name):
            self.a_a = {"alignment_software": "BWA", 
                "alignment_software_version": "0.7.12", 
                "analysis_group": "McGill EMC", 
                "analysis_software": "GenPipes", 
                "analysis_software_version": "3.1.0",
                }
        else: # Default values for most experiment_type.names.
            self.a_a = {"alignment_software": "BWA", 
                "alignment_software_version": "0.7.15", 
                "analysis_group": "McGill EMC", 
                "analysis_software": "GenPipes", 
                "analysis_software_version": "3.1.0",
                }

class Hub_Description:
    def __init__(self):
        now = datetime.datetime.now()
        now_formatted = now.strftime("%Y-%m-%d")
        self.h_d = {
            "name": "McGill EMC Data Hub", # New field.
            "assembly": "hg38", 
            "date": now_formatted, 
            "description": "McGill EMC Data Hub", 
            "email": "info@epigenomesportal.ca", 
            "publishing_group": "CEEHRC", 
            "releasing_group": "McGill", 
            "taxon_id": 9606
        }
  

def main():
    h = Hub()

    # Find datasets with linked public_tracks; exclude any orphaned ones.
    LinkedDS = PublicTrack.alias()
    linked_ds = (LinkedDS.select(LinkedDS.dataset_id)\
        .where(LinkedDS.path.is_null(False))\
        .distinct()\
        .alias('linked_ds')\
        )

    # Select these Datasets with other needed info.
    ds_query = (Dataset.select(Dataset, ExperimentType, Sample)\
        .join(linked_ds, on=(Dataset.id == linked_ds.c.dataset_id))\
        .switch(Dataset)\
        .join(ExperimentType)\
        .switch(Dataset)\
        .join(Sample)\
        )

    ds_results = ds_query.execute()
    for ds in ds_results:
        # Dataset section
        # Generate a unique dataset_id
        dataset_id = f"{ds.sample.public_name}.{ds.experiment_type.name}" # Some experiment_types have spaces in the word (ie. ChIP-Seq Input, Capture Methylome, all the Chipmentations).  Does this cause problems?
        h.data["datasets"][dataset_id] = {}

        # analysis_attributes
        h.data["datasets"][dataset_id]["analysis_attributes"] = Analysis_Attributes(et_name=ds.experiment_type.name).a_a

        # sample_id
        h.data["datasets"][dataset_id]["sample_id"] = ds.sample.public_name

        # experiment_attributes

        # Looks like "experiment_ontology_curie" is now required and "experiment_ontology_uri" has disappeared.
        # There appear to be some entries from the properties section that are not defined yet.  Where do they come from?  
        ep_query = ExperimentProperty.select(ExperimentProperty.property, ExperimentMetadata.value)\
            .join(ExperimentMetadata)\
            .where(ExperimentMetadata.dataset_id == ds.id)
        ea = {}
        for ep in ep_query.dicts(): # Is there a better way of doing this?  toJSON() (ie. model_to_dict()) didn't really work.
            ea[ep["property"]] = ep["value"]
        h.data["datasets"][dataset_id]["experiment_attributes"] = ea

        # browser
        # Find tracks linked to this dataset.
        track_query = (PublicTrack.select(PublicTrack)\
            # Restrict to new, hg38 tracks (path not null)
            .where((PublicTrack.dataset_id == ds.id) & (PublicTrack.path.is_null(False)))\
            )
        track_results = track_query.execute()

        browser = {}
        for track in track_results:
            track_type = []
            browser_track = {}

            browser_track["big_data_url"] = track.path + track.file_name
            browser_track["md5sum"] = track.md5sum
            track_type.append(browser_track)
            # browser.track_type can have one or more list entries.  First entry taken as `primary` unless otherwise stated.
            if track.track_type in browser:
                browser[track.track_type].extend(track_type)
            else:
                browser[track.track_type] = track_type
        
        h.data["datasets"][dataset_id]["browser"] = browser 

        # download section never seems to be used... 

        # Lots of extraneous metadata here - should all fields really be included? #TODO: see if they get filtered during the ingestion step.
        # Samples
        sm_query = (SampleMetadata.select(SampleMetadata, SampleProperty)\
            .where(SampleMetadata.sample_id == ds.sample_id)\
            .join(SampleProperty)\
            )
        
        # Sample Attributes (Properties)
        sa = {}
        for sm in sm_query.dicts():
            sa[sm["property"]] = sm["value"]
        
        # Find the Donor
        d_query = (Donor.select(Donor, Sample)\
            .join(Sample)\
            .where(Sample.id == ds.sample_id)\
            )
        d_query.execute()
        for d in d_query:
            donorID = d.id # The Donor
            donor_public_name = d.public_name

        # Donor Attributes (Properties)
        dm_query = (DonorMetadata.select(DonorMetadata, DonorProperty)\
            .where(DonorMetadata.donor_id == donorID)\
            .join(DonorProperty)\
            )
        da = {} # Dict to hold the data
        da["donor_id"] = donor_public_name # required element.  Part of donor table (not donor_metadata).
        for dm in dm_query.dicts():
            da[dm["property"]] = dm["value"]
        
            # Convert donor_age into number value (not a string), if applicable.
            if dm["property"] == "donor_age" and dm["value"].isdigit():
                da["donor_age"] = int(dm["value"])

        # Combine the Sample and Donor metadata; place it into the data hub.
        samples_metadata = sa.copy()
        samples_metadata.update(da)
        h.data["samples"][ds.sample.public_name] = samples_metadata

    # Hub description
    h.data["hub_description"] = Hub_Description().h_d
    
    # Output to terminal
    print(h.jsonify())


if __name__ == "__main__":
  main()
