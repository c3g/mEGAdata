import requests
import json
import os
import sys
# from abc import ABC, abstractmethod
from configparser import ExtendedInterpolation, RawConfigParser
import logging

import globals
import utils

# class EgaObj(ABC):
class EgaObj():
    def __init__(self):
        self.data = {} # "Empty"
        self.path_to_template = ""
        self.registration_status = "INSTANTIATED"

    # Pretty print
    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def send(self):
        # Define request
        path = globals.BASE_URL + globals.config["session"]["submission_path"] + "/" + _type_to_api(self)
        payload = json.dumps(self.data)
        r = requests.post(path, headers=json.loads(globals.config["global"]["headers"]), data=payload)
        # Ensure successful response
        if r.status_code != 200:
            raise Exception(f"Failed to send {_type_to_api(self).capitalize()} {self.data['alias']}")
        else:
            logging.debug(f"SENT {_type_to_api(self).capitalize()} {self.data['alias']}")
        json_response = r.json()
        # Update with server-assigned id
        self.data["id"] = json_response["response"]["result"][0]["id"]

    # It is best *NOT* to VALIDATE EGA Objects individually - only VALIDATE entire Submission at once.
    def validate(self):
        json_response = self._validate_or_submit("VALIDATE").json()
        # Take registration status from response.
        self.registration_status = json_response["response"]["result"][0]["status"]
        logging.debug(f"{_type_to_api(self).capitalize()} {self.data['alias']} has registration status: {self.registration_status}")

    # It is best *NOT* to SUBMIT EGA Objects individually - SUBMIT entire Submission at once.
    def submit(self):
        json_response = self._validate_or_submit("SUBMIT").json()
        # Take registration status from response.
        self.registration_status = json_response["response"]["result"][0]["status"]
        logging.debug(f"{_type_to_api(self).capitalize()} {self.data['alias']} has registration status: {self.registration_status}")
        # Update with EGA Accession id from response.
        egaAccessionId = json_response["response"]["result"][0]["egaAccessionId"]
        if egaAccessionId:
            self.data["egaAccessionId"] = egaAccessionId
        # For Experiments, rather than egaAccessionId, egaAccessionIds[0] must be used.
        elif json_response["response"]["result"][0]["egaAccessionIds"]:
            self.data["egaAccessionId"] = json_response["response"]["result"][0]["egaAccessionIds"][0]
        logging.debug(f"{_type_to_api(self).capitalize()} {self.data['alias']} has egaAccessionId: {self.data['egaAccessionId']}.")

    # Internal class function.
    def _validate_or_submit(self, action="VALIDATE"):
        if action not in ("VALIDATE", "SUBMIT"):
            raise Exception(f"For {_type_to_api(self).capitalize()} {self.data['alias']}, only VALIDATE or SUBMIT actions are permitted.")
        path = globals.BASE_URL + "/" + _type_to_api(self) + "/" + self.data["id"] + "?action=" + action
        r = requests.put(path, headers=json.loads(globals.config["global"]["headers"]))
        if r.status_code != 200:
            raise Exception(f"Failed to {action} {_type_to_api(self).capitalize()} {self.data['alias']}")
        else:
            logging.debug(f"{action}D {_type_to_api(self).capitalize()} {self.data['alias']}")
        return r

    # Is the Object already registered in the internal obj_registry of INSTANTIATED Objects?
    def _is_in_registry(self):
        for obj in globals.obj_registry[f"{_type_to_api(self)}"]:
            if self.data["alias"] == obj.data["alias"]:
                logging.debug(f"{_type_to_api(self).capitalize()} {self.data['alias']} is already present in the obj_registry.")
                return True
            else:
                continue
            # Once all the list members have been checked...
            logging.debug(f"{_type_to_api(self).capitalize()} {self.data['alias']} not in the obj_registry .")
            return False

    # Return Object by alias and type from internal obj_registry lists.
    @classmethod
    def _get_by_alias(cls, alias, obj_type):
        # Select which list to use
        for obj in globals.obj_registry[obj_type]:
            logging.debug(f"Searching through {obj_type} for alias: {utils.alias_raw(obj.data['alias'])}...")
            if utils.alias_raw(obj.data['alias']) == alias:
                logging.debug(f"Found {alias} in globals.obj_registry {obj_type}.")
                return obj
        # Nothing found.
        raise Exception(f"Lookup of alias {alias} failed.")


# Corresponds to and EGA Submission object.
class Submission(EgaObj):
    def __init__(self):
        f = open(globals.config["directories"]["json_dir"] + globals.config["session"]["submission_json"])
        self.data = f.read() # Want json - this might be a string.

    # Should write this.
    def __str__(self):
        pass

    # Initial send to EGA server.
    def send(self):
        path = "/submissions"
        url = globals.BASE_URL + path
        r = requests.post(url, headers=json.loads(globals.config["global"]["headers"]), data=self.data)
        if r.status_code != 200:
            raise Exception("Could not send Submission json.")
        json_response = r.json()
        globals.config["session"]["submissionId"] = json_response["response"]["result"][0]["id"]
        globals.write_config()
        logging.debug(f"Submission SENT with submissionId {globals.config['session']['submissionId']}")
        
    def validate(self):
        self._validate_or_submit(action="VALIDATE")
            
    def submit(self):
        self._validate_or_submit(action="SUBMIT")

    # Internal class function.
    def _validate_or_submit(self, action="VALIDATE"):
        if action not in ("VALIDATE", "SUBMIT"):
            raise Exception(f"For Submissions, only VALIDATE or SUBMIT actions are permitted.")
        path = f"/submissions/{globals.config['session']['submissionId']}?action={action}"
        url = globals.BASE_URL + path
        r = requests.put(url, headers=json.loads(globals.config["global"]["headers"]))
        if r.status_code != 200:
            logging.debug(r.text)
            raise Exception(f"Could not complete Submission {action}ION.")
        logging.debug(f"Submission {action} accepted.")

    # All of this Submissions EGA Objects, by type.
    # Returns an EGA response result JSON (list)
    def _all_of(self, obj_type):
        path = f"/submissions/{globals.config['session']['submissionId']}/{obj_type}"
        url = globals.BASE_URL + path
        resp = requests.get(url, headers=json.loads(globals.config["global"]["headers"]))
        if resp.status_code != 200:
            logging.debug(f"Failed to retrieve this Submission's {obj_type}. \n {resp.text}")
            raise Exception(f"Could not retrieve Submission {obj_type}.")
        logging.debug(f"Retrieved this Submission's {obj_type}.")
        return resp.json()["response"]["result"]

    # Returns a list containing all Ids associated with this Submissions, for a particular EGA Object type.
    def all_ids(self, obj_type):
        if obj_type not in ["samples", "studies", "experiments", "runs", "dacs", "policies", "datasets", "analyses"]:
            raise Exception("Unknown EGA object type.")
        resp = self._all_of(obj_type)
        # Parse EGA response results JSON for list of Ids.
        objIds_list = []
        for obj in resp:
            objIds_list.append(obj["id"])
        return objIds_list

    # Deletes one Object, given its Id and type.
    def _delete_one_by_id(self, Id, obj_type):
        if not Id:
            raise Exception(f"Please specify the Id of the {obj_type} to delete.")
        path = f"/{obj_type}/{Id}"
        url = globals.BASE_URL + path
        resp = requests.delete(url, headers=json.loads(globals.config["global"]["headers"]))
        # Not currently verifying that an object was deleted.  Even a failed delete request can returns status_code == 200.
        if resp.status_code != 200:
            logging.debug(f"Failed to DELETE {obj_type} with Id: {Id} \n {resp.text}")
            raise Exception(f"Could not DELETE {obj_type} with Id: {Id}.")
        logging.debug(f"DELETED {obj_type} with Id: {Id}.")

    # Deletes all this Submission's EGA Objects, of a given type.
    # obj_type: EGA Object type, as a string.
    def delete_all_of(self, obj_type):
        if obj_type not in ["samples", "studies", "experiments", "runs", "dacs", "policies", "datasets", "analyses"]:
            raise Exception("Unknown EGA object type to delete.")
        del_list = self.all_ids(obj_type)
        for Id in del_list:
            self._delete_one_by_id(Id, obj_type)
        logging.debug(f"All {obj_type} DELETED for this Submission.")

    # Deletes all of this Submission's EGA Objects, for all types.
    # Might need to code to verfiy that truly nothing remains (http errors can cause deletion failures.)
    def delete_all_objects(self):
        for obj_type in ["samples", "studies", "experiments", "runs", "dacs", "policies", "datasets", "analyses"]:
            self.delete_all_of(obj_type)
        logging.debug(f"All EGA Objects DELETED for this Submission.")


# Corresponds to EGA Sample object.
class Sample(EgaObj):
    def __init__(self, alias):
        self.path_to_template = globals.config["directories"]["json_dir"] + _type_to_api(self) + "/" + utils.alias_raw(alias) + ".json"
        self.registration_status = "INSTANTIATED"
        try:
            f = open(self.path_to_template)
        except:
            logging.error("Couldn't open Sample file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        # Append an autoincrement to the alias to ensure unique aliases submitted to EGA during testing.
        self.data["alias"] = utils.alias_testing(alias)
        logging.debug(f"Instantiated Sample: {self.data['alias']}")
        # if not already in globals.obj_registry, append, send, validate and submit (all at once).
        if not self._is_in_registry():
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Sample {self.data['alias']} added to global list.")
            self.send()

    # Find EgaObj in globals.obj_registry by alias
    @classmethod
    def get_by_alias(cls, alias):
        return cls._get_by_alias(alias, "samples")

    # Needs work...
    # Should be made unambiguous
    def __repr__(self):
        return self.data["alias"]

# Rather than lookup up in the obj_registry, could I query EGA directly?  Well, have to query *by* something (alias or id)...

# Corresponds to EGA Experiment object.
# Despite the EGA documentation regarding the new JSON format (Green Arrow), for Experiments, we need to submit each assay type for each sample.
# We can use a template to generate the EgaObj, but we need somewhere to store the Samples * Assays = 8 * 8 = 64 EGA ids.
# Options: the relationMapping.ods Spreadsheet.  An internal data structure.  Generate all 64 jsons.
# Should "design name" be a link to "See http://epigenomesportal.ca/edcc/doc/"?
class Experiment(EgaObj):
    def __init__(self, sample_alias, exp_alias):
        self.path_to_template = globals.config["directories"]["json_dir"] + _type_to_api(self) + "/" + utils.alias_raw(exp_alias) + ".json"
        try:
            f = open(self.path_to_template)
        except:
            logging.error("Couldn't open Experiment file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        # Append an autoincrement to the alias to ensure unique aliases submitted to EGA during testing.
        self.data["alias"] = utils.alias_testing(f"{sample_alias}_{exp_alias}")
        # Include Study and Sample in the Experiment.
        self.data["studyId"] = globals.config["submission"]["studyId"]
        # Lookup sample_alias in globals.obj_registry
        # self.data["sampleId"] = Sample.get_by_alias(sample_alias).data["alias"]
        self.data["sampleId"] = Sample.get_by_alias(sample_alias).data["id"]
        logging.debug(f"Instantiated Experiment: {self.data['alias']}")
        # if not already in globals.experiments, append, send, validate and submit (all at once).
        if not self._is_in_registry():
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Experiment {self.data['alias']} added to global list.")
            self.send()

    # Find EgaObj in globals.obj_registry by alias
    @classmethod
    def get_by_alias(cls, alias):
        return cls._get_by_alias(alias, "experiments")


class Study(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

class Run(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

class Dac(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

class Policy(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

class Dataset(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

# Not implemented.
class Analysis(EgaObj):
    def __init__(self):
        pass

    def send(self):
        pass

# Maybe rename to better reflect usage.
def _type_to_api(EgaObj):
    if isinstance(EgaObj, Sample):
        return "samples"
    elif isinstance(EgaObj, Study):
        return "studies"
    elif isinstance(EgaObj, Experiment):
        return "experiments"
    elif isinstance(EgaObj, Run):
        return "runs"
    elif isinstance(EgaObj, Dac):
        return "dacs"
    elif isinstance(EgaObj, Policy):
        return "policies"
    elif isinstance(EgaObj, Dataset):
        return "datasets"
    elif isinstance(EgaObj, Analysis):
        logging.error("Not implemented")
    else:
        raise Exception("Unknown EGA Object.")
    

#### JUNK ####
'''
    def send(self):
        # Send EgaObj only once.  Once sent, it has an id.
        # if "id" not in self.data:
        # Remove ids from template for sending to EGA, if present.
        # if "id" in self.data:
        #     self.data.pop("id")
        # if "egaAccessionId" in self.data:
        #     self.data.pop("egaAccessionId")

    # Saves object data to template file.
    # def save_to_template(self):
    #     try:
    #         f = open(self.path_to_template, "w")
    #     except:
    #         logging.error("Couldn't open Sample file to write.")
    #     f.write(json.dumps(self.data, indent=4))
    #     f.close()

\"title\" : \"\",\
	                \"description\" : \"\",\


# SUBMISSION
def validate_subset(self):
    self._validate_or_submit_subset(action="VALIDATE")

def submit_subset(self):
    self._validate_or_submit_subset(action="SUBMIT")

# So far, only hard-coded for first row of data.
def _validate_or_submit_subset(self, action="VALIDATE"):
    if action not in ("VALIDATE", "SUBMIT"):
        raise Exception(f"For subset Submissions, only VALIDATE or SUBMIT actions are permitted.")
    path = f"/submissions/{globals.config['session']['submissionId']}?action={action}"
    url = globals.BASE_URL + path
    sample = Sample.get_by_alias("MS048901")
    sampleId = sample.data["id"]
    experiment = Experiment.get_by_alias("MS048901_" + "Chipmentation_H3K27ac")
    experimentId = experiment.data["id"]
    # print("Using: " + sample.data["id"])
    # print("Using: " + sample.data["id"])
    payload = "{\"submissionSubset\" : {\
                    \"sampleIds\" : [\"" + sampleId + "\"],\
                    \"analysisIds\" : [],\
                    \"dacIds\" : [],\
                    \"datasetIds\" : [],\
                    \"experimentIds\" : [\"" + experimentId + "\"],\
                    \"policyIds\" : [],\
                    \"runIds\" : [],\
                    \"studyIds\" : []\
        } }"
    print(payload)
    r = requests.put(url, headers=json.loads(globals.config["global"]["headers"]), data=payload)
    if r.status_code != 200:
        print(r.text)
        raise Exception(f"Could not {action} partial Submission.")
    logging.debug(f"Partial Submission {action}ION accepted.")

Default is reuse Submission. Just use config's.
Reuse recorded Submission - retrieve from config
Send initial Submission - store submissionId - same as new Submission. - Needs to be primed.
New Submission - Send new and overwrite config submissionId

        # Restore later
        # f"registration_status: {self.registration_status}\n" + \
        # return f"path_to_template: {self.path_to_template}\n" + \
        #     json.dumps(self.data, indent=4) + "\n\n"

# self.validate()
# self.submit()

'''