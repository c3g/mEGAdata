/*
 * Prepare database for merge of branch exportingScripts
 */

ALTER TABLE public_track ADD COLUMN path VARCHAR(400);
ALTER TABLE public_track ADD COLUMN file_name VARCHAR(200);
ALTER TABLE public_track ADD COLUMN file_type VARCHAR(100);

ALTER TABLE public_track MODIFY COLUMN `dataset_id` int(11) DEFAULT NULL;

ALTER TABLE public_track ADD CONSTRAINT `fk_public_track_dataset_id` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`);
ALTER TABLE donor ADD CONSTRAINT `fk_donor_taxon_id` FOREIGN KEY (`taxon_id`) REFERENCES `species` (`taxon_id`);
ALTER TABLE run ADD CONSTRAINT `fk_run_dataset_id` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`);
ALTER TABLE run DROP KEY `dataset_library_run_lane`;

-- Covert some sex = 'M' to sex = 'Male' (to follow the schema definition)
update sample_metadata
set value = 'Male'
where id in (8908, 8909, 8911, 8913)
;
