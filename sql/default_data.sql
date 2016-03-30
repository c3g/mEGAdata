INSERT INTO `species` VALUES
  (9544,'Macaca mulatta','rhesus monkey'),
  (9592,'Gorilla','gorilla'),
  (9597,'Pan paniscus','bonobo'),
  (9598,'Pan troglodytes','chimpanzee'),
  (9606,'Homo sapiens','human'),
  (10090,'Mus musculus','house mouse');


INSERT INTO `donor_property` VALUES
  (1,'disease','string',1),
  (2,'disease_ontology_uri','uri',1),
  (3,'specific_disease_information','text',0),
  (4,'age','string',1),
  (5,'year_of_birth','string',0),
  (6,'sex','string',1),
  (7,'ethnicity','string',1),
  (8,'smoking_status','string',1),
  (9,'health_status','string',1),
  (10,'medication','string',0),
  (11,'additional_information','text',0);


INSERT INTO `sample_property` VALUES
  (1,'project_name','string',0),
  (2,'project_id','int',0),
  (3,'time_point','string',0),
  (4,'biomaterial_type','string',1),
  (5,'tissue_type','string',1),
  (6,'tissue_type_ontology_uri','uri',1),
  (7,'tissue_depot','string',1),
  (8,'tissue_depot_ontology_uri','uri',1),
  (9,'cell_type','string',1),
  (10,'cell_type_ontology_uri','uri',1),
  (11,'molecule','string',1),
  (12,'additional_information','string',0),
  (13,'epirr_id','string',0);


INSERT INTO `experiment_type` VALUES
(1,'Bisulfite-seq','BS','WGB-Seq','Methylation profiling by high-throughput sequencing','wgb_seq'),
(2,'RNA-seq','RNASeq','RNA-Seq','Transcriptome profiling by high-throughput sequencing','rna_seq'),
(3,'mRNA-seq','mRNASeq','mRNA-Seq','Transcriptome profiling by high-throughput sequencing','rna_seq'),
(4,'smRNA-seq','smRNASeq','smRNA-Seq','Transcriptome profiling by high-throughput sequencing','smallrna_seq'),
(5,'ChIP-Seq Input','ChIP_Input','Input','','chip_seq'),
(6,'H3K27me3','ChIP_H3K27me3','H3K27me3','','chip_seq'),
(7,'H3K36me3','ChIP_H3K36me3','H3K36me3','','chip_seq'),
(8,'H3K4me1','ChIP_H3K4me1','H3K4me1','','chip_seq'),
(9,'H3K4me3','ChIP_H3K4me3','H3K4me3','','chip_seq'),
(10,'H3K27ac','ChIP_H3K27ac','H3K27ac','','chip_seq'),
(11,'H3K9me3','ChIP_H3K9me3','H3K9me3','','chip_seq'),
(12,'ATAC-seq','ATACSeq','ATAC-Seq','Sequencing of transposase-accessible chromatin','atac_seq'),
(13,'Capture Methylome','CM','Capture Methylome','Methylome capture: targeted capture of the functional methylome','wgb_seq');


INSERT INTO `experiment_metadata_set` VALUES
(1,'Bisulfite-seq','1'),
(2,'RNA-seq','1'),
(3,'mRNA-seq','1'),
(4,'smRNA-seq','1'),
(5,'ChIP-Seq Input','1'),
(6,'H3K27me3','1'),
(7,'H3K36me3','1'),
(8,'H3K4me1','1'),
(9,'H3K4me3','1'),
(10,'H3K27ac','1'),
(11,'H3K9me3','1'),
(12,'ATAC-seq','1'),
(13,'Capture Methylome','1');