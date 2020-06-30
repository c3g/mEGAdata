# Hub Dataset

import json
import datetime
import peewee
from models import PublicTrack, Dataset, Sample, ExperimentType, ExperimentMetadata, ExperimentProperty


class Hub:
    def __init__(self):
        self.data = {
            "datasets": {},
            "hub_description": {},
            # "samples": {"0":0},
            }

    def jsonify(self):
        # Legible and pretty representation
        return json.dumps(self.data, indent=2, sort_keys=True)

class Analysis_Attributes:
    # All values taken from previous 2016 and 2017 McGill submissions.
    # v0.6.1 is from 2011, so probably not applicable to this hg38 alignment.
    # #TODO This is probably different for the hg38 alignment. (Alignment is different than sequencing.) 
    # et_name is experiment_type.name.
    def __init__(self, et_name=""):
        if not et_name: # Default values for most experiment_type.names.
            self.a_a = {"alignment_software": "BWA", 
            "alignment_software_version": "0.6.1", 
            "analysis_group": "McGill EMC", 
            "analysis_software": "NA", 
            "analysis_software_version": "NA",
            }
        elif et_name == "RNA-seq" or et_name == "mRNA-seq" or et_name == "smRNA-seq":
            self.a_a = {"alignment_software": "TopHat", 
                "alignment_software_version": "1.4.1", 
                "analysis_group": "McGill EMC", 
                "analysis_software": "NA", 
                "analysis_software_version": "NA",
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

    # Find datasets with linked public_tracks, not any orphaned ones.
    LinkedDS = PublicTrack.alias()
    linked_ds = (LinkedDS.select(LinkedDS.dataset_id)\
        .where(LinkedDS.path.is_null(False))\
        .alias('linked_ds')\
        )
    ds_query = (Dataset.select(Dataset, ExperimentType, Sample)\
        .join(linked_ds, on=(Dataset.id == linked_ds.c.dataset_id))\
        .switch(Dataset)\
        .join(ExperimentType)\
        .switch(Dataset)\
        .join(Sample)\
        # .where(Dataset.id == 4954)\  # Just one dataset, for testing.
        )
    ds_results = ds_query.execute()
    for ds in ds_results:
        # Dataset section
        # Generate a unique dataset_id
        dataset_id = f"{ds.sample.public_name}.{ds.experiment_type.name}" # Some experiment_types have spaces in the word (ie. ChIP-Seq Input, Capture Methylome, all the Chipmentations).  Does this cause problems?
        h.data["datasets"][dataset_id] = {}

        # analysis_attributes
        h.data["datasets"][dataset_id]["analysis_attributes"] = Analysis_Attributes().a_a # TODO: use actual experiment_type value.

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
        # TODO: Need track_type categorized first.

        # download section never seems to be used... 

    # Hub description
    h.data["hub_description"] = Hub_Description().h_d

    # Samples
    # Could just dump all the samples, regardless of whether we need them or not.
    # Need both sample and donor metadata
    

    print(h.jsonify())


def junk(self):
    pass
    # h.data = {
    #     "datasets": {"0":0},
    #     "hub_description": {"0":0},
    #     "samples": {"0":0},
    #     }

    # print(json.dumps(hd.__dict__, indent = 4))
    # print(json.dumps(hd__dict__, indent = 4))

            # print(em.id, em.dataset_id, em.value)
            # print(em.toJSON())
            # print(em, em.value)
    # em_query = (ExperimentMetadata.select(ExperimentMetadata.value, ExperimentProperty.property)\
    #     .where(ExperimentMetadata.dataset_id == ds.id))\
    #     .join(ExperimentProperty))

    # em_results = em_query.execute()
            # print(f"{em.experiment_property.property}: {em.value}")
        #     h.data["datasets"][dataset_id]["experiment_attributes"]f"{em.experiment_property.property}: {em.value}")


if __name__ == "__main__":
  main()
