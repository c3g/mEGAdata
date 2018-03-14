#mEGAdata: EGA submission made easy

### Required Software

These need to be installed beforehand:

* MySQL
* Python
* pip
* virtualenv
* npm
* bower


###Steps to install
```
#Prepare MySQL database
cd sql
mysql -uuser -ppasswd -e "create database mEGAdata;"
mysql -uuser -ppasswd  mEGAdata < model.sql
mysql -uuser -ppasswd  mEGAdata < default_data.sql

#Install external Python dependencies
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

#Install external Javascript dependencies
cd static
bower install
```

Then, copy settings_example.py to settings.py, and configure parameters.


###To execute
```
. venv/bin/activate
python main.py
```

Start by adding donors, then add samples, and finally, datasets, by double-clicking on a sample-experiment cell.

###Documentation

Database model diagram is available in MySQL Workbench format here: ./sql/mEGAdata.mwb
