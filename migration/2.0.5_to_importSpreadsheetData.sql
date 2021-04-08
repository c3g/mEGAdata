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
