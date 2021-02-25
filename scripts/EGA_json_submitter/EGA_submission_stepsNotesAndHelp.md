## EGA submission steps, notes & help

### Warning about repeated and deprecated information:
The current submission documentation is here:
https://ega-archive.org/submission/quickguide

Its submission portal:
https://ega-archive.org/submitter-portal/#/


The older submission mechanism (though it still seems to work) is here:
https://www.ebi.ac.uk/ega/submission

An even older submission method where you submit through ENA (though it still works for some EGA things) is here:
https://www.ebi.ac.uk/ena/browser/guides
And its submission portal:
https://www.ebi.ac.uk/ena/submit/sra/#home



### 1) Encrypt the files:
Resources & links:

### EGAcryptor
The EGACryptor will work with Openjdk-8.
Follow the install directions at:
https://ega-archive.org/submission/tools/egacryptor

The JCE policy files for unlimited encryption strength need to be manually placed here (or somewhere comparable):
/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/policy/unlimited

Run the EgaCryptor on the CWD:
java -jar /usr/local/bin/EgaCryptor/EgaCryptor.jar -file * &

### 2) Transfer the files:
To transfer files to EGA, use:
ftp ftp.ega.ebi.ac.uk
Username : ega-box-209
Password : tFM3Lf3E

Once an ftp connection is established, enter the following commands to define the connection:
binary
prompt
pass

Transfer only the encrypted files with:
mput *.fastq.gz.gpg

### Register the files?

### Tools written for metadata ingestion
scripts/importEMCSpreadsheet.py
scripts/import_experiment_metadata.py

### A bloggers account of submitting to EGA (somewhat useful and somewhat humourous).
https://gavinband.github.io/bioinformatics/data/2019/05/01/Me_versus_the_European_Genome_Phenome_Archive.html


dbrownlee@Heliotrope:~/receivedData/EMC_community/EMC1$ rsync -thP *.md5 *.gpg *.log davidbr@ihec-data.vhost38:/ihec_data/share/2021_EMCforEGA/EMC1


### Use the EgaCryptor logs to update the spreadsheets with md5sums and encrypted_md5sums.  This involves straightforward text manipulation in an editor (to get one line per file).  Turn the EgaCryptor log into a .tsv with following columns: Filename, md5sum, encrypted_md5sum.  Then some importing, sorting and copy paste in spreadsheets solves the rest.

### Objects need to be submitted in a particular order (so that subsequent objects can reference them.)


### JSON preparation
Samples jsons were prepared manually since there aren't that many of them.

When sending json objects to EGA, like with this:
curl -X POST path/submissions/{submissionId}/studies -d '{Json Object, see Study}' 
the {submissionId} is found in the response header from the submission that was sent.  For example:
  "response" : {
    "numTotalResults" : 2,
    "resultType" : "eu.crg.ega.microservice.dto.submitter.SubmissionData",
    "result" : [ {
      "id" : "6009ba3198e25200016df7dc",
This last id (6009ba...) is the correct one.


### Note about enums (and where to get them.)

### See the XML schemas for data dictionary-like documenttion field descriptions.
ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ 

### Note about using JSONs for submission. Yes, they do work.
