SET foreign_key_checks=0;
DROP TABLE IF EXISTS `dataset`;
CREATE TABLE `dataset` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '		',
  `sample_id` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `release_status` varchar(100) DEFAULT NULL,
  `EGA_EGAX` varchar(16) DEFAULT NULL,
  `last_modification` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `experiment_metadata_set_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sample_experiment_UNIQUE` (`sample_id`,`experiment_id`),
  KEY `fk_dataset_1_idx` (`experiment_id`),
  KEY `fk_dataset_2_idx` (`sample_id`),
  KEY `experiment_metadata_set_id` (`experiment_metadata_set_id`),
  CONSTRAINT `dataset_ibfk_1` FOREIGN KEY (`experiment_metadata_set_id`) REFERENCES `experiment_metadata_set` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_dataset_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_dataset_2` FOREIGN KEY (`sample_id`) REFERENCES `sample` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4596 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `dataset_to_release_set`;
CREATE TABLE `dataset_to_release_set` (
  `dataset_id` int(11) NOT NULL,
  `release_set_id` int(11) NOT NULL,
  PRIMARY KEY (`dataset_id`,`release_set_id`),
  KEY `release_set_id` (`release_set_id`),
  CONSTRAINT `dataset_to_release_set_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `dataset_to_release_set_ibfk_2` FOREIGN KEY (`release_set_id`) REFERENCES `release_set` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `donor`;
CREATE TABLE `donor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `public_name` varchar(100) DEFAULT NULL,
  `private_name` varchar(100) DEFAULT NULL,
  `taxon_id` int(11) DEFAULT NULL,
  `last_modification` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_pool` tinyint(1) DEFAULT '0',
  `phenotype` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `private_name_UNIQUE` (`private_name`),
  KEY `taxon_id` (`taxon_id`),
  CONSTRAINT `donor_ibfk_1` FOREIGN KEY (`taxon_id`) REFERENCES `species` (`taxon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=318 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `donor_metadata`;
CREATE TABLE `donor_metadata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `donor_id` int(11) NOT NULL,
  `donor_property_id` int(11) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`),
  KEY `fk_donor_metadata_donor1_idx` (`donor_id`),
  KEY `fk_donor_metadata_donor_property1_idx` (`donor_property_id`),
  CONSTRAINT `fk_donor_metadata_donor1` FOREIGN KEY (`donor_id`) REFERENCES `donor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_donor_metadata_donor_property1` FOREIGN KEY (`donor_property_id`) REFERENCES `donor_property` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5427 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `donor_property`;
CREATE TABLE `donor_property` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `property` varchar(100) DEFAULT NULL,
  `type` set('string','int','float','text','uri') DEFAULT NULL,
  `is_exported_to_ega` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `experiment`;
CREATE TABLE `experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `internal_assay_short_name` varchar(50) DEFAULT NULL,
  `ihec_name` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `internal_assay_category` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `experiment_metadata`;
CREATE TABLE `experiment_metadata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attribute` varchar(200) DEFAULT NULL,
  `value` text,
  `experiment_metadata_set_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experiment_metadata_set_id` (`experiment_metadata_set_id`),
  CONSTRAINT `experiment_metadata_set_id` FOREIGN KEY (`experiment_metadata_set_id`) REFERENCES `experiment_metadata_set` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=418 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `experiment_metadata_set`;
CREATE TABLE `experiment_metadata_set` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `version` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `release_set`;
CREATE TABLE `release_set` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release` varchar(10) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text,
  `EGA_EGAD` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `run`;
CREATE TABLE `run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_id` int(11) NOT NULL,
  `run` varchar(15) NOT NULL,
  `lane` varchar(15) NOT NULL,
  `md5_read_1` varchar(32) NOT NULL,
  `md5_read_2` varchar(32) NOT NULL,
  `md5_encEGA_read_1` varchar(32) NOT NULL,
  `md5_encEGA_read_2` varchar(32) NOT NULL,
  `EGA_EGAR` varchar(16) DEFAULT NULL,
  `fastq_read_1` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dataset_run_lane` (`dataset_id`,`run`,`lane`),
  CONSTRAINT `dataset_id` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=911 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `sample`;
CREATE TABLE `sample` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `donor_id` int(11) DEFAULT NULL,
  `public_name` varchar(100) DEFAULT NULL,
  `private_name` varchar(100) DEFAULT NULL,
  `public_archive_id` varchar(50) NOT NULL DEFAULT '',
  `EGA_EGAN` varchar(16) DEFAULT NULL,
  `last_modification` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_name_UNIQUE` (`public_name`),
  KEY `fk_sample_1_idx` (`donor_id`),
  CONSTRAINT `fk_sample_1` FOREIGN KEY (`donor_id`) REFERENCES `donor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=528 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `sample_metadata`;
CREATE TABLE `sample_metadata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sample_id` int(11) NOT NULL,
  `sample_property_id` int(11) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`),
  KEY `fk_sample_metadata_sample1_idx` (`sample_id`),
  KEY `fk_sample_metadata_sample_property1_idx` (`sample_property_id`),
  CONSTRAINT `fk_sample_metadata_sample1` FOREIGN KEY (`sample_id`) REFERENCES `sample` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_sample_metadata_sample_property1` FOREIGN KEY (`sample_property_id`) REFERENCES `sample_property` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=6115 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `sample_property`;
CREATE TABLE `sample_property` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `property` varchar(100) DEFAULT NULL,
  `type` set('string','int','float','text','uri') DEFAULT NULL,
  `is_exported_to_ega` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `species`;
CREATE TABLE `species` (
  `taxon_id` int(11) NOT NULL,
  `scientific_name` varchar(200) NOT NULL,
  `common_name` varchar(200) NOT NULL,
  PRIMARY KEY (`taxon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET foreign_key_checks=1;