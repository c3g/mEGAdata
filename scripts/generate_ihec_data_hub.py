# Hub Dataset

import json
import peewee
from models import PublicTrack, Dataset, Sample, ExperimentType, ExperimentMetadata, ExperimentProperty
from playhouse.shortcuts import model_to_dict


class Hub:
    def __init__(self):
        self.data = {
            "datasets": {},
            # "hub_description": {"0":0},
            # "samples": {"0":0},
            }

    def jsonify(self):
        # Legible and pretty representation
        return json.dumps(self.data, indent=4)

class Analysis_Attributes:
    # All values taken from previous 2016 and 2017 McGill submissions.
    # et_name is experiment_type.name.
    def __init__(self, et_name=""):
        if not et_name:
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

def main():
    h = Hub()

    # query for one dataset, to start with.
    ds_query = (Dataset.select(Dataset, ExperimentType, Sample)\
        .join(ExperimentType)\
        .switch(Dataset)\
        .join(Sample)\
        .where(Dataset.id == 4954))
    ds_results = ds_query.execute()
    for ds in ds_results:
        # Generate a unique dataset_id
        dataset_id = f"{ds.sample.public_name}.{ds.experiment_type.name}"
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
            # print(model_to_dict(em))
            # print(em.toJSON())
            # print(em, em.value)
    # em_query = (ExperimentMetadata.select(ExperimentMetadata.value, ExperimentProperty.property)\
    #     .where(ExperimentMetadata.dataset_id == ds.id))\
    #     .join(ExperimentProperty))

    # em_results = em_query.execute()
            # print(f"{em.experiment_property.property}: {em.value}")
        #     h.data["datasets"][dataset_id]["experiment_attributes"]f"{em.experiment_property.property}: {em.value}")


class HubDataset:
    pass



if __name__ == "__main__":
  main()
