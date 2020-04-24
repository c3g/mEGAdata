# mEGAdata scripts

Scripts for pairing data files with the mEGAdata  DB and exporting them as a an IHEC data hub.

### Why a separate venv?
The main mEGAdata program (running peewee 2.5.1) has its models incorrectly defined and only works through exploiting the side-effect of a bug (corrected in future versions of peewee).  The models, as defined, are incompatible with all future versions of peewee.  See note in mEGAdata/models.py for details.  Corrections could be somewhat involved and wide-reaching.  Considering the limited internal use nature of the mEGAdata user interface, it was decided not to repair the models at this time.

However, to prevent furthering the mess and complicating future repairs, new development on these database-heavy export scripts is done within its own virtualenv.

### Software platform
Current versions in use:
* python 3.6.9
* pip 20.0.2

### Install external Python dependencies
virtualenv scripts-venv # Create a fresh virtualenc for the scripts to run in.
. scripts-venv/bin/activate
pip install -r requirements.txt

### Steps to install
cp settings_example.py setting.py  # and make your changes.

