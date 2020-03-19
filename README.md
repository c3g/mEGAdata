# mEGAdata: EGA submission made easy

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
sudo apt-get install libmysqlclient-dev
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
### Execute flask the server
```
cd megadata/
. venv/bin/activate
python main.py
```

### Usage
Start by adding donors, then add samples, and finally, datasets, by double-clicking on a sample-experiment cell.

### Documentation

Database model diagram is available in MySQL Workbench format here: `./sql/mEGAdata.mwb`
