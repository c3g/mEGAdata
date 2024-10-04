## Further points to document:
* Objects need to be submitted in a particular order (so that subsequent objects can reference them.)
* Do not Validate / Submit one object at a time.  For referential integrity, only Validate / Submit as part of a Submission subset.
* Started a data dictionary .ods.  Now put it somewhere useful.
* Notes about which objects to reuse (study, policy, dac, etc.)

### When going live...
Run migration .sql script.
add f-string compiler directive?  Won't actually be running it from megadata.vhost...

### From fresh, recent backup.sql...
#### From ~/sql
mysql mEGAdata < megadata-backup-2021-04-09.sql
mysql mEGAdata < ~/projects/megadata/migration/2.0.5_to_importSpreadsheetData.sql

#### From ~/projects/megadata/scripts/spreadsheet_importation
python importEMCSpreadsheet.py
python import_experiment_metadata.py

#### From ~/sql
mysqldump mEGAdata > megadata-community-inserted-with-metadata.sql


### Code improvements (to be prioritized...)
* Change "" to NULLs.
* Change public_file paths to something true.

* Need a better name for this script: EGAtransact, talktoEGA...  EGAzap!  EGArequest.py?
* Review and clean comments.

* Add f-string directives to all .py files.
* Will be a git merge, eventually.  After EpiRR submisison.
* rebuild node website and restart on megadata.vhost prod.

* The CLAs are a mess.  Maybe just make only one CLA possible at a time.
* Make R7 a CLA for generate_relation_mapping.py

### Future improvements
* Some egaobj.py __init__ code could be further generalized.
* egaobj.py __str__ methods could be generalized to base class. 
* TODO: Is storing path_to_template needed for all Objects?
* self.registration_status = "INSTANTIATED" <-- Is this used / useful?
* EGA often fails to delete Objects.  Do something about it, or at lest provide a message.  Check, then automatically retry?
  * delete-all-objects doesn't delete the Submission itself.  Is there a way to do this from the API?

* Turn this into a list of known bugs and shelf them.

### Going live...
* Can I curl all Files object accession Ids? No.
* Run spreadsheet_import scripts directly on mEGAdata.vhost.  Maybe, maybe not.
* Submit through assez - get response jsons.  Save the submission ID. <- Also in curls
* Run absorb_EGA_accessions.py on mEGAdata.vhost.  Use the python3.5 and f-string compiler directive.
* Retrieve EGAF (for files), if quick.  Not available through API, but ICGC has a method for retrieval.  Separate and not quick.

### Going live DONEs
* Why is sample EMC1_? - Ah, keep it.
* Fix NULLs, "".  last_mod times should get updated during EGA accession update. & last mod time in sample.
* Regenerate .sqls from freshest mEGAdata backup.
* Alias quotes caused problems on prod. - seems fine now...


### Not going to do.
* Ensure no duplicates sent (possibly already handled with the unique alias constraint).  CAN this even happen?
* Ensure no premature Submission SUBMITion. (Leave a single trailing VALIDATED Object to prevent progression to SUBMITTED?)  Yeah, look into this on test - Submissions seem to submit themselves once all their objects are submitted.
* Detect or treat http errors - may need a http retry function for network timeouts.  This has sometimes been an issue.  Try many sends and deletes on prod. (Full run?)  Can do a long run (reuse files?) on test SP, eh? <- This send worked; the delete didn't.
* fix that prod previous submission I seemed to have mutated to draft state...  Just leave it.  Nothing can be done.


#### Less important...
* Are all of those import globals & import utils needed (circular ref?)
* Modify hard-coded path/filenames to settings.ini (these are only in the import_spreadsheet dir & generate_relation_mapping.py (output to &1?), which is separate, and doesn't even use globals.config.)
* rotate logs? (or append)
* Integrate that curl stuff as a python script. (absolutely all SUBMITTED ega objects, from every Submission).
* is spreadsheet_importation a good dir for the files / code?

#### Probably ignore...
* Preserve obj_registry between send.py's.  (Currently blanked when non "send" command sent.. Such as `send.py --validate pass`.)
* Review previous submissions - are they complete and accurate?
* EgeObj as an ABC?  Never seemed to get it working...


## DONE
* Fix that super-nasty experiment part where it looks up the .json template based on substring of the alias.
* relationsMapping.ods mods:
  * Remove ID columns from relationMapping.ods - they are never used.
  * Add a template column to relationsMapping.ods.
* separate auto_increment from test/prod option. - DONE!
* Be careful about those number appending to aliases.  Review before live.  Test on test SP, but only as far as VALIDATED.
* Redo submission template description.
* relation_mapping.ods hard-coded numbers need to be settings.ini.
* Clean up EMC_Community_json directory - division between input templates and output JSONs.
  * Put the all_file_ega_inbox.json somewhere useful.
* In settings.ini, merge / deconvolute session / submission sections.

## Note:
When sending JSON objects to EGA, like with this:  
curl -X POST path/submissions/{submissionId}/studies -d '{JSON Object, see Study}'  
The {submissionId} is found in the response header from the Submission that was sent.  For example:  
```bash
  "response" : {
    "numTotalResults" : 2,
    "resultType" : "eu.crg.ega.microservice.dto.submitter.SubmissionData",
    "result" : [ {
      "id" : "6009ba3198e25200016df7dc",
```
This last id (6009ba...) is the correct one.

