# mEGAdata DB backups, in stages.
# Keep old copies
version=beforeBigLn
mv megadata-with-migration.sql megadata-with-migration.${version}.sql
mv megadata-with-addTrackToDB.sql megadata-with-addTrackToDB.${version}.sql
mv megadata-with-tracksLinked.sql megadata-with-tracksLinked.${version}.sql

# Generate new .sql files
mysql mEGAdata < megadata-backup-2020-03-04.sql
# Run the 2.0.3_to_exportingScripts.sql migration .sql script
mysql mEGAdata < ~/projects/megadata/migration/2.0.3_to_exportingScripts.sql
# Then...
mysqldump mEGAdata > megadata-with-migration.sql

# cd to script dir
python add_tracks_to_db.py
# cd back to ~/sql dir
mysqldump mEGAdata > megadata-with-addTrackToDB.sql

# Preserve old log dir.
# Set .sql scripts to all EMC projects.
# cd to script dir
# run without the db wipe at the end.
./run_and_log.sh

# cd back to ~/sql dir
mysqldump mEGAdata > megadata-with-tracksLinked.sql
