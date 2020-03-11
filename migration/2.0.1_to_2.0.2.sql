/*
 * Prepare database for migration to version 2.0.2.
 */

-- Add is_paired_end to dataset table to generate EXPERIMENT XMLs at EGA
ALTER TABLE dataset ADD COLUMN library_layout VARCHAR(10);