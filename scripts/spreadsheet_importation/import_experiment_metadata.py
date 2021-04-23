# -*- coding: future_fstrings -*-
import os
import sys
# Make models.py accessible
SCRIPTS_ROOT_DIR = os.path.dirname(os.getcwd())
sys.path.append(SCRIPTS_ROOT_DIR)

import peewee
from models import Dataset, ExperimentMetadata
import pyexcel as pe

# Inserts experiment_metadata into mEGAdata DB for all datasets, based on the experiment_type.internal_assay_short_name.

# Usage:
# Define the experiment_metadata in the JSONs below for each assay type.
# Define datasets in a .ods.
# Run this script after datasets are created by importEMCSpreadsheet.py

# .ods spreadsheet containing the datasets
importFile = "/home/assez/projects/megadata/scripts/spreadsheet_importation/allEMCcommunity.ods"

# table rows in the spreadsheet.  Start at header row, end at last row of data.
# Rightmost COMMENTS columns may be skipped by defining col_limit.
# Start at leftmost column, which is the dataset.id column.
tables = []

# References to dataset rows.
tables.append({'sheet':'EMC1', 'name':'dataset', 'start':33, 'end':41, 'col_limit':6})
tables.append({'sheet':'EMC2', 'name':'dataset', 'start':67, 'end':99, 'col_limit':6})
tables.append({'sheet':'EMC3', 'name':'dataset', 'start':60, 'end':84, 'col_limit':6})

def main():
    # Read each sheet and build list of all datasets.
    for table in tables:
        records = pe.get_records(file_name=importFile, sheet_name=table['sheet'],\
            name_columns_by_row=0,\
            start_row=table['start'] - 1, row_limit=table['end'] - table['start'] + 1,\
            column_limit=table['col_limit'] if 'col_limit' in table else -1,\
            )
        for record in records: # Essentially, for each dataset; returns an OrderedDict
            for key, value in record.items(): # returns dict of all key, values
                if key == "id": # select only the id column.
                    myDataset = Dataset.get_by_id(value) # Instantiate the Dataset model.
                    metadata = exp_meta[myDataset.experiment_type.internal_assay_short_name] # link to proper experiment_metadata dict below.
                    for entry in metadata:
                        entry["dataset_id"]=myDataset.id # Include dataset.id in metadata entry row.
                        try:
                            print(ExperimentMetadata.insert(entry).execute()) # Create and save experiment_metadata to DB.
                        except:
                            print("Error saving to DB.")
                            

# JSONs of experiment_metadata, one for each assay, copied from the .ods MM provided.
# experiment_metadata for all experiment_type.internal_short_name types.
exp_meta = {
    "BS": [
        {"experiment_property_id":1, "value":"DNA Methylation"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001863"},
        {"experiment_property_id":3, "value":"DNeasy Blood & Tissue Kit (Qiagen)"},
        {"experiment_property_id":4, "value":"E210"},
        {"experiment_property_id":5, "value": "Duty Cycle 20%, Intensity 75 W, Cycles per Burst 1000, Duration 49 sec"},
        {"experiment_property_id":6, "value":"1500 ng"},
        {"experiment_property_id":7, "value":"300 bp"},
        {"experiment_property_id":8, "value":"AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
        {"experiment_property_id":9, "value":"NxSeq AmpFREE Low DNA libary (Lucigen)"},
        {"experiment_property_id":10, "value":"300-1000 bp"},
        {"experiment_property_id":11, "value":"EZ-DNA Methylation Gold kit (Zymo Research)"},
        {"experiment_property_id":14, "value":"KAPA HiFi HotStart Uracil+Polymerase"},
        {"experiment_property_id":15, "value":"2min @ 95C-> (30sec @ 98C -> 30sec @ 60C -> 4min @72C) x 9 cycles -> 10min @ 72C -> keep @ 4C"},
        {"experiment_property_id":16, "value":"6"},
        {"experiment_property_id":17, "value":"AAT GAT ACG GCG ACC ACC GAG A"},
        {"experiment_property_id":18, "value":"CAA GCA GAA GAC GGC ATA CGA"},
        {"experiment_property_id":19, "value":"5 uM"},
        {"experiment_property_id":20, "value":"Ampure 0.8X"},
        {"experiment_property_id":36, "value":"NxSeq AmpFREE Low DNA libary (Lucigen)"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Bisulfite-Seq"},
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
        {"experiment_property_id":67, "value":"None"}, # overconversion_control_genome
    ],
    "RNASeq": [
        {"experiment_property_id":1, "value":"RNA-Seq"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001271"},
        {"experiment_property_id":3, "value":"miRNeasy Mini Kit (Qiagen)"},
        {"experiment_property_id":22, "value":"94°C for 8 minutes"},
        {"experiment_property_id":29, "value":"30°C for 10 minutes"},
        {"experiment_property_id":30, "value":"30°C for 10 minutes"},
        {"experiment_property_id":34, "value":"Enzyme : SuperScript II Reverse Transcriptase (Illumina)"},
        {"experiment_property_id":35, "value":"12"},
        {"experiment_property_id":36, "value":"Truseq Stranded RNA Core LP (Illumina)"},
        {"experiment_property_id":38, "value":"260 bp"},
        {"experiment_property_id":39, "value":"AAT GAT ACG GCG ACC ACC GAG A"},
        {"experiment_property_id":40, "value":"CAA GCA GAA GAC GGC ATA CGA"},
        {"experiment_property_id":64, "value":"total RNA"},
        {"experiment_property_id":65, "value":"RNA-Seq"},
        {"experiment_property_id":66, "value":"SO:0000356"}, # molecule_ontology_curie
        {"experiment_property_id":68, "value":"miRNeasy Mini Kit (Qiagen)"}, # extraction_protocol_rna_enrichment
        {"experiment_property_id":69, "value":"500 ng"}, # preparation_initial_rna_qnty
    ],    
    "Chipmentation_H3K27ac": [
        {"experiment_property_id":1, "value":"Histone H3K27ac"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"370 ng"},
        {"experiment_property_id":47, "value":"Dynabeads ProtA (ThermoFisher)"},
        {"experiment_property_id":48, "value":"30 uL"},
        {"experiment_property_id":49, "value":"1 ng"},
        {"experiment_property_id":50, "value":"H3K27ac"},
        {"experiment_property_id":51, "value":"Diagenode"},
        {"experiment_property_id":52, "value":"C15410196"},
        {"experiment_property_id":53, "value":"A1723-0041D"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K27ac"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
    "Chipmentation_H3K4me3": [
        {"experiment_property_id":1, "value":"Histone H3K4me3"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"370 ng"},
        {"experiment_property_id":47, "value":"Dynabeads ProtA (ThermoFisher)"},
        {"experiment_property_id":48, "value":"25 uL"},
        {"experiment_property_id":49, "value":"1 ng"},
        {"experiment_property_id":50, "value":"H3K4me3"},
        {"experiment_property_id":51, "value":"Diagenode"},
        {"experiment_property_id":52, "value":"C15410003"},
        {"experiment_property_id":53, "value":"A1052D"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K4me3"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
    "Chipmentation_H3K4me1": [
        {"experiment_property_id":1, "value":"Histone H3K4me1"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"1111 ng"},
        {"experiment_property_id":47, "value":"Dynabeads ProtA (ThermoFisher)"},
        {"experiment_property_id":48, "value":"20 uL"},
        {"experiment_property_id":49, "value":"1.7 ng"},
        {"experiment_property_id":50, "value":"H3K4me1"},
        {"experiment_property_id":51, "value":"Cell Signaling"},
        {"experiment_property_id":52, "value":"CST 9326"},
        {"experiment_property_id":53, "value":"BF"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K4me1"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
    "Chipmentation_H3K27me3": [
        {"experiment_property_id":1, "value":"Histone H3K27me3"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"1111 ng"},
        {"experiment_property_id":47, "value":"Dynabeads ProtA (ThermoFisher)"},
        {"experiment_property_id":48, "value":"25 uL "},
        {"experiment_property_id":49, "value":"10.2 ng "},
        {"experiment_property_id":50, "value":"H3K27me3"},
        {"experiment_property_id":51, "value":"Cell Signaling"},
        {"experiment_property_id":52, "value":"CST 9733"},
        {"experiment_property_id":53, "value":"S"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K27me3"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
    "Chipmentation_H3K36me3": [
        {"experiment_property_id":1, "value":"Histone H3K36me3"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"1111 ng"},
        {"experiment_property_id":47, "value":"Dynabeads M-280 Sheep Anti-Mouse IgG (ThermoFisher)"},
        {"experiment_property_id":48, "value":"30 uL"},
        {"experiment_property_id":49, "value":"1 ng"},
        {"experiment_property_id":50, "value":"H3K36me3"},
        {"experiment_property_id":51, "value":"MAB Institute"},
        {"experiment_property_id":52, "value":"CMA333"},
        {"experiment_property_id":53, "value":"13C9"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K36me3"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
    "Chipmentation_H3K9me3": [
        {"experiment_property_id":1, "value":"Histone H3K9me3"},
        {"experiment_property_id":2, "value":"http://purl.obolibrary.org/obo/OBI_0001858"},
        {"experiment_property_id":3, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":4, "value":"Bioruptor 300"},
        {"experiment_property_id":5, "value":"45"},
        {"experiment_property_id":38, "value":"300bp"},
        {"experiment_property_id":45, "value":"Auto Chipmentation Kit for Histones (Diagenode)"},
        {"experiment_property_id":46, "value":"1111 ng"},
        {"experiment_property_id":47, "value":"Dynabeads ProtA (ThermoFisher)"},
        {"experiment_property_id":48, "value":"20 uL"},
        {"experiment_property_id":49, "value":"1 ng"},
        {"experiment_property_id":50, "value":"H3K9me3"},
        {"experiment_property_id":51, "value":"Abcam"},
        {"experiment_property_id":52, "value":"ab8898"},
        {"experiment_property_id":53, "value":"Lot GR93671-1"},
        {"experiment_property_id":54, "value":"10 mins"},
        {"experiment_property_id":64, "value":"genomic DNA"},
        {"experiment_property_id":65, "value":"Chipmentation"},
        {"experiment_property_id":70, "value":"H3K9me3"}, # experiment_target_histone
        {"experiment_property_id":66, "value":"SO:0000991"}, # molecule_ontology_curie
    ],
}

if __name__ == "__main__":
  main()
