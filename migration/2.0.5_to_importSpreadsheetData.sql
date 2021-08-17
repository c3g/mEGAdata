/*
 * Prepare database for merge of branch importSpreadsheetData
 */

-- New WGBS experiment_properties
INSERT INTO experiment_property(property, type, is_exported_to_ega) VALUES ('molecule_ontology_curie', 'text', 1);
INSERT INTO experiment_property(property, type, is_exported_to_ega) VALUES ('overconversion_control_genome', 'text', 1);

-- New RNA-Seq experiment_properties
INSERT INTO experiment_property(property, type, is_exported_to_ega) VALUES ('extraction_protocol_rna_enrichment', 'text', 1);
INSERT INTO experiment_property(property, type, is_exported_to_ega) VALUES ('preparation_initial_rna_qnty
', 'text', 1);

-- New ChIP-Seq experiment_properties
INSERT INTO experiment_property(property, type, is_exported_to_ega) VALUES ('experiment_target_histone', 'text', 1);

-- New release_set (aka EGA datasets) for R7
INSERT INTO release_set(`release`, `name`, `description`) VALUES ('R7', 'McGill EMC Community projects Release 7 for cell line "SaOS-2"','Complete reference epigenome (as defined by IHEC) of a SaOS-2 cell line with osteosarcoma.');
INSERT INTO release_set(`release`, `name`, `description`) VALUES ('R7', 'McGill EMC Community projects Release 7 for cell line "lung epithelial"', 'Complete reference epigenome (as defined by IHEC) of a lung epithelial cell line with non-small Cell Lung Adenocarcinoma');
INSERT INTO release_set(`release`, `name`, `description`) VALUES ('R7', 'McGill EMC Community projects Release 7 for cell line "hTERT RPE1"', 'Complete reference epigenome (as defined by IHEC) of normal hTERT RPE1 cell line as well as hTERT RPE1 cell lines engineered to express EPC1-PHF1 and JAZF1-SUZ12 fusion proteins, found in Endometrial Stromal Sarcoma.');
