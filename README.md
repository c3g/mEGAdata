# mEGAdata: EGA submissions made easy

## Purpose
A web interface for composing EGA submissions.

Within scripts/EGA_json_submitter is a programatic (scripted) tool to submit to EGA.  It parses source data in spreadsheets and submits to EGA through the API (now probably deprecated).  It was used to submit the EMC_Community (1, 2 & 3) and EMC_Barreiro datasets.

Includes scripts to generate the 2020 IHEC data hub for the hg38-realigned EMC data.

The database contains the metadata for the following projects:
* EMC_Asthma
* EMC_BluePrint
* EMC_BrainBank
* EMC_CageKid
* EMC_iPSC
* EMC_Leukemia
* EMC_Mature_Adipocytes
* EMC_Mitochondrial_Disease
* EMC_MSCs
* EMC_SARDs
* EMC_Temporal_Change

## Installation
### Required Software
These need to be installed beforehand:

* MySQL
* Python 2.7.17
* pip 9.0.1

  Follow the curl directions at https://pip.pypa.io/en/stable/installing/ then use `python get-pip.py pip==9.0.2`
* virtualenv

  `pip install virtualenv`
* node.js (includes npm) 10.0.0

  Follow the nvm directions at: https://github.com/nvm-sh/nvm
* bower

    Can be install with `npm install bower`

### Steps to install
```
#Prepare MySQL database
cd sql/
mysql -uuser -ppasswd -e "create database mEGAdata;"
mysql -uuser -ppasswd  mEGAdata < model.sql
mysql -uuser -ppasswd  mEGAdata < default_data.sql
```

### Install external Python dependencies
sudo apt-get install python3-dev libmysqlclient-dev build-essential
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Install external Javascript dependencies
```
cd static/
bower install
```

### Configure local settings
```
cd megadata/
cp settings_example.py settings.py (and configure local parameters)
```

### Build the node website
```
cd static/
npm install
npm run build
```
### To execute the flask server on a desktop, use:
```
cd megadata/
. venv/bin/activate
python main.py
```

### On prod, it is located at:
```bash
cd /opt/megadata
```

### On prod (megadata.vhost38.genap.ca), it is running as a service.  Confirm with:
```bash
systemctl | grep megadata
``` 

### Restart the prod service with:
```bash
sudo systemctl restart megadata
```

### Usage
Start by adding donors, then add samples, and finally, datasets, by double-clicking on a sample-experiment cell.

### Documentation

Database model diagram is available in MySQL Workbench format here: `./sql/mEGAdata.mwb`
