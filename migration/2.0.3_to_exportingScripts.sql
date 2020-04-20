/*
 * Prepare database for merge of branch exportingScripts
 */

ALTER TABLE public_track ADD COLUMN path VARCHAR(400);
ALTER TABLE public_track ADD COLUMN file_name VARCHAR(200);
ALTER TABLE public_track ADD COLUMN file_type VARCHAR(100);

ALTER TABLE public_track MODIFY COLUMN `dataset_id` int(11) DEFAULT NULL;
