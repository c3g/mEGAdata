/*
 * Prepare database for migration to version 2.0.1.
 */


ALTER TABLE experiment_type ADD COLUMN ega_name VARCHAR(100);