/*
 * Prepare database for migration to version 2.0.0.
 */


-- Create experiment_property table, holding all possible experimental metadata properties
CREATE TABLE `experiment_property` (
  `id`                  int(11) NOT NULL AUTO_INCREMENT,
  `property`            varchar(100) DEFAULT NULL,
  `type`                set('string','int','float','text','uri') DEFAULT NULL,
  `is_exported_to_ega`  tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
);


-- Create one experiment_property record per existing property in the previous experiment_metadata table
INSERT INTO `experiment_property` (`property`, `type`, `is_exported_to_ega`) (
    SELECT DISTINCT `attribute`, 'text', FALSE FROM experiment_metadata
);


-- Create new experiment_metadata table that will hold values for all properties of all dataset entries
RENAME TABLE `experiment_metadata` to `experiment_metadata_old`;
CREATE TABLE `experiment_metadata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_id` int(11) NOT NULL,
  `experiment_property_id` int(11) NOT NULL,
  `value` text,
  primary key (`id`),
  KEY `fk_experiment_metadata_dataset1_idx` (`dataset_id`),
  KEY `fk_experiment_metadata_experiment_property1_idx` (`experiment_property_id`),
  CONSTRAINT `fk_experiment_metadata_dataset1` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_experiment_metadata_experiment_property1` FOREIGN KEY (`experiment_property_id`) REFERENCES `experiment_property` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);


-- Create one experiment_metadata record per dataset-property combination
INSERT INTO `experiment_metadata` (`dataset_id`, `experiment_property_id`, `value`) (
    SELECT d1.id, ep1.id, emo1.value
    FROM dataset d1
    JOIN experiment_metadata_set ems1 ON d1.experiment_metadata_set_id = ems1.id
    JOIN experiment_metadata_old emo1 ON emo1.experiment_metadata_set_id = ems1.id
    JOIN experiment_property ep1 ON ep1.property = emo1.attribute
);


-- Drop unused tables & columns
ALTER TABLE `dataset` DROP FOREIGN KEY `dataset_ibfk_1`;
ALTER TABLE `dataset` DROP COLUMN `experiment_metadata_set_id`;
DROP TABLE `experiment_metadata_old`;
DROP TABLE `experiment_metadata_set`;
ALTER TABLE `sample` DROP COLUMN `public_archive_id`;


-- Create users table
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
