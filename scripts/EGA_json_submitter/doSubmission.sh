# DB work
# from ~/sql
mysql mEGAdata < megadata-backup-2021-05-03.sql
mysql mEGAdata < ~/projects/megadata/migration/2.0.5_to_importSpreadsheetData.sql
# from ~/projects/megadata/scripts/spreadsheet_importation
python importEMCSpreadsheet.py
python import_experiment_metadata.py
mysqldump mEGAdata > megadata-community-inserted-before-live-withMatchingQuotes.sql

# sample prod submission
# Make changes to settings.ini
python send.py --new-submission send
# Run the curl - change dir name.
# Save the Submission ID: 609434f498e2520001af3cbe
python send.py record-EGA-objects
python send.py --validate pass
python send.py record-EGA-objects
# Check that everything is in status=VALIDATED. and nothing left in status=DRAFT.
python send.py --submit pass
python send.py record-EGA-submitted
python absorb_EGA_accessions.py
# Run the curl again.
# Revert the settings.ini
