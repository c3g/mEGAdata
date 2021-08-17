import requests
import json
import os
import sys
from configparser import ExtendedInterpolation, RawConfigParser
import logging

import globals
import utils

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
            # logging.debug(f"Searching through {obj_type} for alias: {utils.alias_raw(obj.data['alias'])}...")
            if utils.alias_raw(obj.data['alias']) == alias:
                logging.debug(f"Found {alias} in globals.obj_registry {obj_type}.")
                return obj
        # Nothing found.
        raise Exception(f"Lookup of alias {alias} failed for type {obj_type}.")


# Corresponds to an EGA Submission object.
class Submission(EgaObj):
    def __init__(self):
        try:
            f = open(globals.config["directories"]["template_dir"] + _type_to_api(self) + "/" + globals.config["submission"]["submission_json"])
        except:
            logging.error("Couldn't open Submission template file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        logging.debug(f"Instantiated Submission.")

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    # Initial send to EGA server.
    def send(self):
        path = "/submissions"
        url = globals.BASE_URL + path
        payload = json.dumps(self.data)
        r = requests.post(url, headers=json.loads(globals.config["global"]["headers"]), data=payload)
        if r.status_code != 200:
            raise Exception("Could not send Submission json.")
        json_response = r.json()
        globals.config["session"]["submissionId"] = json_response["response"]["result"][0]["id"]
        utils.write_config()
        logging.debug(f"Submission SENT with submissionId {globals.config['session']['submissionId']}")
        
    def validate(self):
        self._validate_or_submit(action="VALIDATE")
            
    def submit(self):
        self._validate_or_submit(action="SUBMIT")

    # The VALIDATE and SUBMIT operation to prod would hang (no response received, but everything was VALIDATED/SUBMITTED...)
    def _validate_or_submit(self, action="VALIDATE"):
        if action not in ("VALIDATE", "SUBMIT"):
            raise Exception(f"For Submissions, only VALIDATE or SUBMIT actions are permitted.")
        path = f"/submissions/{globals.config['session']['submissionId']}?action={action}"
        url = globals.BASE_URL + path
        r = requests.put(url, headers=json.loads(globals.config["global"]["headers"]))
        if r.status_code != 200:
            logging.debug(r.text)
            raise Exception(f"Could not complete Submission {action}ION.")
        # Save response
        f = open(globals.config["directories"]["response_dir"] + f"submission{action}Response.json", "w")
        f.write(r.text)
        logging.debug(f"Submission {action} accepted.")

    # All of this Submissions EGA Objects, for one Object type.
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

    # Deletes one Object from EGA, given its Id and type.
    def _delete_one_by_id(self, Id, obj_type):
        if not Id:
            raise Exception(f"Please specify the Id of the {obj_type} to delete.")
        path = f"/{obj_type}/{Id}"
        url = globals.BASE_URL + path
        resp = requests.delete(url, headers=json.loads(globals.config["global"]["headers"]))
        # Not currently verifying that an object was deleted.  Even a failed delete request can returns status_code == 200.
        # TODO: EGA *often* fails to delete Objects.
        # Perhaps just a message that not everything was really deleted.
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

    # Deletes all of this Submission's EGA Objects, for all types.  Doesn't delete the Submission Object itself.
    # Sometimes all Objects don't get deleted.  It is safe to run multiple times to ensure complete deletion.
    # Sometimes the script just hangs at this operation.
    # The SP is rather slow to delete objects, so be patient.  The UI can also be used and is faster and deletes more completely.
    # Might need to code to verfiy that truly nothing remains (http errors can cause deletion failures.)
    # Tested on a 90 Run Submission.  Ran delete-all-objects 3 times and .  Then with one click in the UI, whole submission was deleted very well.  So, conclusion is that it is better to delete the entire Submission through the UI than its individual objects through this script.  Can an entire Submission be deleted through the API? 
    def delete_all_objects(self):
        # Probably only want to delete Objects unique to this Submission (samples, experiments, runs and datasets), not those shared with other submissions.
        # for obj_type in ["samples", "studies", "experiments", "runs", "dacs", "policies", "datasets", "analyses"]:
        for obj_type in ["samples", "experiments", "runs", "datasets"]:
            self.delete_all_of(obj_type)
        logging.debug(f"All EGA Objects DELETED for this Submission.")

    # Record this Submission's custom Object JSONs (as they exist at EGA) to disk (except the Submission object itself).
    # Once Objects are SUBMITTED to SP, they need to be queried with ?status=SUBMITTED appended to the request.
    # status is usually one of "DRAFT", "VALIDATED", "SUBMITTED" (though there are other possibilities).
    def _record_EGA_objects(self, status=""):
        for obj_type in ["samples", "experiments", "runs", "datasets"]:
            dir = f"record-EGA-{status}" if status else "record-EGA-objects"
            try:
                f = open(globals.config["directories"]["response_dir"] + f"{dir}/{obj_type}.json", "w")
            except:
                logging.error(f"Couldn't open file to write {obj_type} from EGA responses.")
            else:
                path = globals.BASE_URL + globals.config["session"]["submission_path"] + f"/{obj_type}?skip=0&limit=0"
                path = path + "&status=" + status if status else path
                r = requests.get(path, headers=json.loads(globals.config["global"]["headers"]))
                if r.status_code != 200:
                    raise Exception(f"Could not retrieve JSON of all {obj_type} from this Submission.")
                f.write(r.text)
                f.close()
                logging.debug(f"This Submission's {obj_type} retrieved as JSON from EGA.")

# Corresponds to EGA Sample object.
class Sample(EgaObj):
    def __init__(self, alias, template):
        self.path_to_template = globals.config["directories"]["template_dir"] + _type_to_api(self) + "/" + template
        try:
            f = open(self.path_to_template)
        except:
            logging.error("Couldn't open Sample template file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        # Ensure unique aliases submitted to EGA.  Append an autoincrement to the alias during testing.
        self.data["alias"] = utils.alias_increment(alias)
        logging.debug(f"Instantiated Sample: {self.data['alias']}")
        # if not already in globals.obj_registry.samples, append and send.
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
# Despite the EGA documentation regarding the new JSON format (Green Arrow), for Experiments, we are submitting separate experiments for each sample.
# We use a template to generate the EgaObj and store the Ids in the internal obj_registry.
# Should "design name" be a link to "See http://epigenomesportal.ca/edcc/doc/"?
class Experiment(EgaObj):
    def __init__(self, sample_alias, exp_alias, exp_template):
        self.path_to_template = globals.config["directories"]["template_dir"] + _type_to_api(self) + "/" + exp_template
        try:
            f = open(self.path_to_template)
        except:
            logging.error("Couldn't open Experiment template file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        # Ensure unique aliases submitted to EGA.  Append an autoincrement to the alias during testing.
        self.data["alias"] = utils.alias_increment(f"{exp_alias}")
        # Include Study and Sample in the Experiment.
        self.data["studyId"] = globals.config["submission"]["studyId"]
        # Lookup sample_alias in globals.obj_registry
        # Maybe pass in a Sample as a param rather than a string for lookup....
        self.data["sampleId"] = Sample.get_by_alias(sample_alias).data["id"]
        logging.debug(f"Instantiated Experiment: {self.data['alias']}")
        # if not already in globals.obj_registry.experiments, append and send.
        if not self._is_in_registry():
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Experiment {self.data['alias']} added to global list.")
            self.send()

    # Find EgaObj in globals.obj_registry by alias
    @classmethod
    def get_by_alias(cls, alias):
        return cls._get_by_alias(alias, "experiments")


# Currently restricted to only paired fastq.gz files - could be extended to other Run types later.
class Run(EgaObj):
    def __init__(self, sample_alias, exp_alias, run_alias, file1, file2):
        # pass in objects, rather than strings?...
        self.data = {}
        # Ensure unique aliases submitted to EGA.  Append an autoincrement to the alias during testing.
        self.data["alias"] = utils.alias_increment(f"{run_alias}")
        self.data["sampleId"] = Sample.get_by_alias(sample_alias).data["id"]
        self.data["runFileTypeId"] = 5 # From enums.file_types, for paired .fastq.gz
        self.data["experimentId"] = Experiment.get_by_alias(exp_alias).data["id"]
        files = []
        files.append(file1.data)
        files.append(file2.data)
        self.data["files"] = files
        logging.debug(f"Instantiated Run: {self.data['alias']}")
        # if not already in globals.obj_registry.runs, append and send.
        if not self._is_in_registry():
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Run {self.data['alias']} added to global list.")
            self.send()

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    # Find EgaObj in globals.obj_registry by alias
    @classmethod
    def get_by_alias(cls, alias):
        return cls._get_by_alias(alias, "runs")


# Non-EgaObj object encapsulating file properties.
# Currently only for paired fastq.gz files - could be extended to other file types later.
class File():
    def __init__(self, fileName, checksum, unencryptedChecksum):
        self.data = {} # "Empty"
        # self.data["fileId"] = "" # Always empty.
        self.data["fileName"] = fileName
        # self.data["alias"] = fileName
        self.data["checksum"] = checksum
        self.data["unencryptedChecksum"] = unencryptedChecksum
        self.data["checksumMethod"] = "" # Empty.

    # Pretty print
    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

class Dataset(EgaObj):
    def __init__(self, alias, template):
        self.path_to_template = globals.config["directories"]["template_dir"] + _type_to_api(self) + "/" + template
        try:
            f = open(self.path_to_template)
        except:
            logging.error("Couldn't open Dataset template file to read.")
            raise Exception("Failed to open file.")
        self.data = json.loads(f.read())
        f.close()
        # Ensure unique aliases submitted to EGA.  Append an autoincrement to the alias during testing.
        self.data["alias"] = utils.alias_increment(f"{alias}")
        self.data["policyId"] = globals.config["submission"]["policyId"]
        self.data["runsReference"] = []
        logging.debug(f"Instantiated Dataset: {self.data['alias']}")
        # if not already present in globals.obj_registry.experiments, append, but DO NOT send().
        if not self._is_in_registry():
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Dataset {self.data['alias']} added to global list.")
            # Don't send() until all Runs have been added!

    # Run: A Run object to add to data.runsReferences[]
    def add_run(self, Run):
        self.data["runsReferences"].append(Run.data["id"])
        logging.debug(f"Run {Run.data['alias']} added to Dataset {self.data['alias']}.")

    # Update a Dataset, by alias, in the obj_registry.  Usually called after adding Runs to the Dataset.
    def update_obj_registry(self):
        if self._is_in_registry():
            # Find
            for obj in globals.obj_registry[f"{_type_to_api(self)}"]:
                if self.data["alias"] == obj.data["alias"]:
                    # Remove
                    globals.obj_registry[f"{_type_to_api(self)}"].remove(obj)
            # Append new Dataset
            globals.obj_registry[f"{_type_to_api(self)}"].append(self)
            logging.debug(f"Updated {_type_to_api(self).capitalize()} with alias {self.data['alias']} in the in globals.obj_registry for {_type_to_api(self)}.")

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    # send all Datasets in the obj_registry to EGA.
    @classmethod
    def send_all(cls):
        for dataset in globals.obj_registry["datasets"]:
            dataset.send()

    # Find EgaObj in globals.obj_registry by alias
    # Couldn't this be part of EgaObject?
    @classmethod
    def get_by_alias(cls, alias):
        return cls._get_by_alias(alias, "datasets")


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
    elif isinstance(EgaObj, Submission):
        return "submissions"
    elif isinstance(EgaObj, Analysis):
        logging.error("Not implemented")
    else:
        raise Exception("Unknown EGA Object.")

# Never implemented - reusing previously submitted EGA Object.
class Study(EgaObj):
    def __init__(self):
        pass

# Never implemented - reusing previously submitted EGA Object.
class Dac(EgaObj):
    def __init__(self):
        pass

# Never implemented - reusing previously submitted EGA Object.
class Policy(EgaObj):
    def __init__(self):
        pass

# Never implemented.
class Analysis(EgaObj):
    def __init__(self):
        pass

    