from configparser import ExtendedInterpolation, RawConfigParser
import logging
from egaobj import Submission

# def define():
# Initialize configuration
# global config
config = RawConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())  # comment_prefixes=';',
config.optionxform = lambda option: option
config.read("settings.ini")

# Initialize logging
logging.basicConfig(filename="send.log", filemode='w', level=eval(config["logging"]["level"]))
logging.debug("Defining globals")

# global API BASE_URL constant
BASE_URL = ""
if config["global"]["test_or_prod"] == "prod":
    BASE_URL = config["global"]["prod_url"]
else:
    BASE_URL = config["global"]["test_url"]
logging.debug(f"Running in {config['global']['test_or_prod']} mode.")

# Write config file to disk.
def write_config():
    with open("settings.ini", "w") as configfile:
        config.write(configfile)

# Define increment to be applied to alias for this submission since EGA does not allow repeated aliases.
if config.getboolean("global", "alias_increment"):
    config["global"]["alias_append"] = str(config.getint("global", "alias_append") + 1)
    write_config()

# Define EgaObject lists
samples = []
experiments = []
runs = []
datasets = []

# Submission, global for now...
mySub = Submission()

# Define local EgaObject registry
obj_registry = {
    "samples": [],\
    "experiments": [],\
    "runs": [],\
    }
