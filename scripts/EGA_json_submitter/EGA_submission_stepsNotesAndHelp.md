# EGA submission notes, steps & help

The current location of *useful* submission documentation is here:  
https://ega-archive.org/submission/quickguide  
The SP UI docs and videos also apply to the the JSON API.  
Its submission portal:  
https://ega-archive.org/submitter-portal/#/


**Warning: some docs are repeated or deprecated:**
The older submission mechanism (though it still seems to work) is here:  
https://www.ebi.ac.uk/ega/submission  
An even older submission method where you submit through ENA (though it still works for some EGA things) is here:  
https://www.ebi.ac.uk/ena/browser/guides  
And its submission portal:  
https://www.ebi.ac.uk/ena/submit/sra/#home  


### Additional resources
* Most recent enums are here:
https://ega-archive.org/submission/programmatic_submissions/how-to-use-the-api#enumApiDetails
* In the old XML schemas, some fields contain descriptions that explain the purpose and expected input of the fields, similar to how a data dictionary would.  
ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ 

### A blogger's account of submitting to EGA (somewhat useful and somewhat humourous).  
https://gavinband.github.io/bioinformatics/data/2019/05/01/Me_versus_the_European_Genome_Phenome_Archive.html


# Submission Steps
## 1) Encrypt the files:
Resources & links:

### EGAcryptor
The EGACryptor will work with Openjdk-8.  
Follow the install directions at:  
https://ega-archive.org/submission/tools/egacryptor  

The JCE policy files for unlimited encryption strength need to be manually placed here (or somewhere comparable):  
/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/policy/unlimited

Run the EgaCryptor on the CWD:  
java -jar /usr/local/bin/EgaCryptor/EgaCryptor.jar -file * &

## 2) Upload the files:
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

### Future work:
* Register/Send the File objects prior to working on the JSONs?  

## 3)  Retrieve md5sums and encrypted md5sums.
Use the EgaCryptor logs to update the spreadsheets with md5sums and encrypted_md5sums.  This involves straightforward text manipulation in an editor (to get one line per file).  Turn the EgaCryptor log into a .tsv with following columns: Filename, md5sum, encrypted_md5sum.  Then some importing, sorting and copy paste in spreadsheets solves the rest.

## 4) Ingest metadata into mEGAdata DB
### Tools for metadata ingestion
* scripts/spreadsheet_importation/importEMCSpreadsheet.py - Ingests .ods into mEGAdata DB.  
* scripts/spreadsheet_importation/import_experiment_metadata.py - Ingests experiment_metadata into mEGAdata DB.  

## 5) Prepare and send the JSONs

### JSON preparation
Some JSONs (such as Sample and Experiment) can be prepared manually from the source spreadsheets with minimal effort since their numbers are small.  
Many objects (Policy, DAC, Study) can be reused from previous a Submission.


## Submission workflow (the only one that will work):
1. Use PROD Submitter Portal for testing.
2. Send all objects - leave in DRAFT status.
3. VALIDATE all objects together as part of a Submission subset.  Can check SP UI error console for errors.
4. When any and all errors resolved, SUBMIT all objects as part of a Submission subset.
5. [Don't VALIDATE or SUBMIT objects individually - referential integrity gets confused unless they are VALIDATED/SUBMITTED as part of a Submission subset.]


## Milestones reached, so far.
* All metadata sufficient for mEGAdata and EGA has now been collected and verified.  Many iterations were required.
* Ingestion of all metadata from .ods into mEGAdata automated through maintainable scripts.
* Sample and Experiment objects all Sent, Validated and Submitted (to test server).
* Proof of JSON submission workflow accomplished, including File objects and Validation/Submission through Submission subsets (on prod server).
* Quick check of Experiment JSONs and updates to spreadsheet import to reflect MM's latest changes - experiment_property_id's assigned for new fields.  release_set and release_set_to_dataset entries added.
* Generate the relations.ods from mEGAdata DB (as csv).  Initial version done.
* INSERTs into dataset_to_release_set and release_set tables.
* Link the Study into the Submission - reuse "EMC".
* DAC - Find Id and link in.  Reuse from previous Submisison.
* Policy - Find Id and link in.  Reuse from previous Submisison.
* Send Run objects (reusing old files existent on test server first).
* Refactored relationsMapping.ods to include templates. - DONE!
* Create and Send Datasets objects: EMC1, EMC2, EMC3.
    * Test with validate and submit, delete.
* Test the delete functions on the test SP. (especially for interrupted Submissions) - working well, though SP glitches during large deletes.  Multiple deletes solve this, but some code should compensate, or raise a message.  Delete whole Submission through the UI works best.
* Retrieval and updates of EGA accessions back into mEGAdata DB (can only be performed after SUBMISSION, but can be done on test SP).  


## Moving forward:
* Fix the NULLs in sample table of allEMCCommunity.ods and redo .sqls.

* Mapping on abacus through symlinks of raw file names to MS00xxx names (McGill Sample format) (abacus account has already been obtained). (This task is independant.)


* Test on prod - going well...

* Ensure no duplicates sent (possibly already handled with the unique alias constraint).  CAN this even happen?
* Ensure no premature Submission SUBMITion. (Leave a single trailing VALIDATED Object to prevent progression to SUBMITTED?)  Yeah, look into this on test - Submissions seem to submit themselves once all their objects are submitted.
* Detect or treat http errors - may need a http retry function for network timeouts.  This has sometimes been an issue.  Try many sends and deletes on prod. (Full run?)  Can do a long run (reuse files?) on test SP, eh? <- This send worked; the delete didn't.

* Tell EGA to deploy the release.
* fix that prod previous submission I seemed to have mutated to draft state...
* EpiRR submission.

* Document. (One page done, so far.  It might be enough.)


## Difficulties encountered, unmentioned in ega-archive API documentation, though resolved thanks to the ega-helpdesk@ebi.ac.uk.
* No JSON API test server URL mentioned in documentation.
* No mention of globalExperimentId or how to use it with JSON API.
* Test server not aware of files uploaded to prod ftp server (must test File and Run objects on PROD).
* Some SP UI constraints apply to the JSON API as well. (In retrospect, this should probably be assumed.)
* Objects cannot be Validated / Submitted individually, though the API supports this.  Objects must be Validated / Submitted as part of a Submission subset.  Individual Validation / Submission != collective Validation / Submission.
* Send, Validate & Submit Samples and Experiments.  Submission then shows up as status=SUBMITTED and SUBMITTED Objects are supposed to be immutable.  However, it is not immutable and further Samples or Experiments can still be sent.  So some SUBMITTED objects are immutable and others aren't.


## Future works
* Currently, there are only hg19-aligned tracks.  MM or Paul will realign everything to hg38 (timeline circa mid-end May). 
* EpiRR submission.
* IHEC DP hub generation has already been scripted (back during the EMC hg38 realignment project) so IDP submission will be relatively straightforward.  However, new submissions need to follow schema V2.0.
