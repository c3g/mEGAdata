# DB work
# from ~/sql
mysql mEGAdata < megadata-backup-2021-05-03.sql
mysql mEGAdata < ~/projects/megadata/migration/2.0.5_to_importSpreadsheetData.sql
# from ~/projects/megadata/scripts/spreadsheet_importation
python importEMCSpreadsheet.py
python import_experiment_metadata.py
mysqldump mEGAdata > megadata-community-inserted-before-live-withMatchingQuotes.sql

# sample prod submission
# Configure settings.ini
python send.py --new-submission send
# Save the Submission ID: 609434f498e2520001af3cbe
python send.py record-EGA-objects
python send.py --validate pass
python send.py record-EGA-objects
# From these return JSONS, check that everything is in status=VALIDATED. and nothing left in status=DRAFT.
python send.py --submit pass
python send.py record-EGA-submitted
# Update mEGAdata with:
python absorb_EGA_accessions.py
# Revert the settings.ini, at least to test server.


JUNK
----
# Run the curl - change dir name.
# Run the curl again.
