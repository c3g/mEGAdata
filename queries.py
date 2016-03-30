#!/usr/bin/python

#Peewee
from flask import request
from models import *
import json

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MySQL accession functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSpeciesList():
    recordList = []
    query = Species.select()
    for species in query:
        recordList.append(species.toJson())
    return json.dumps(recordList)


def getDonorList(pFilter=None):
    recordObj = {}
    
    query = Donor.select()
    if pFilter:
        query = query.where(Donor.private_name.contains(pFilter))
    
    for donor in query:
        recordObj[donor.id] = donor.toJson()

    appendDonorsMetadata(recordObj, pFilter)
    recordList = recordObj.values()
    return json.dumps(recordList)


def appendDonorsMetadata(recordList, pFilter=None):
    query = DonorMetadata.select(DonorMetadata, Donor.id.alias('donor_id'), DonorProperty.property.alias('property')).join(Donor).switch(DonorMetadata).join(DonorProperty)
    if pFilter:
        query = query.where(Donor.private_name.contains(pFilter))

    for dm in query.naive():
        recordList[dm.donor_id][dm.property] = dm.value


def getExperimentTypeList():
    recordList = []
    for et in ExperimentType.select():
        recordList.append(et.toJson())
    return json.dumps(recordList)


def getSampleList(donor):
    query = Sample.select(Sample, Donor).join(Donor)
    
    #Refine based on donor
    if donor is not None:
        query = query.where(Donor.private_name == donor)
    
    recordObj = {}
    for sample in query:
        sampleRecord = sample.toJson()
        
        sampleRecord['id'] = sample.id
        
        datasetList = {}
        query2 = Dataset.select(Dataset, ExperimentType, Sample).join(ExperimentType).switch(Dataset).join(Sample).where(Sample.id == sample.id)
        for dataset in query2:
            datasetList[dataset.experiment_type.name] = dataset.release_status
        
        sampleRecord['datasets'] = datasetList
        recordObj[sample.id] = sample.toJson()

    appendSamplesMetadata(recordObj)
    appendSamplesDatasets(recordObj)
    recordList = recordObj.values()
    return json.dumps(recordList)


def appendSamplesMetadata(recordList):
    query = SampleMetadata.select(SampleMetadata, Sample.id.alias('sample_id'), SampleProperty.property.alias('property')).join(Sample).switch(SampleMetadata).join(SampleProperty)

    for dm in query.naive():
        recordList[dm.sample_id][dm.property] = dm.value


def appendSamplesDatasets(recordList):
    query = Dataset.select(Dataset, Sample.id.alias('sample_id'), ExperimentType.name.alias('experiment_name')).join(Sample).switch(Dataset).join(ExperimentType)

    for dm in query.naive():
        recordList[dm.sample_id][dm.experiment_name] = dm.release_status


def insertDonor():
    dataJson = request.get_json()
    Donor.create(
        public_name = dataJson.get('public_name'),
        private_name = dataJson.get('private_name'),
        taxon_id = dataJson.get("taxon_id"),
        phenotype = dataJson.get("phenotype"),
        is_pool = dataJson.get("is_pool"),
    )
      
    donor = Donor.select().order_by(Donor.id.desc()).get()
    return json.dumps(donor.toJson())


def insertDonorMetadata():
    dataJson = request.get_json()
    dm = DonorMetadata()
    dm.donor = Donor.get(id=dataJson.get('donor_id'))
    dm.donor_property = DonorProperty.select().where(DonorProperty.property == dataJson.get('field'))
    dm.value = dataJson.get('value')
    DonorMetadata.save(dm)
    return {}





def insertSample():
    dataJson = request.get_json()
    d = Donor.get(id=dataJson.get("donor_id"))
    
    p = dataJson.get('project') or {}
    
    Sample.create(
        public_name = dataJson.get('public_name'),
        private_name = dataJson.get('private_name'),
        donor = d
    )
     
    sample = Sample.select().order_by(Sample.id.desc()).get()
    return json.dumps(sample.toJson())



def insertSampleMetadata():
    dataJson = request.get_json()
    dm = SampleMetadata()
    dm.sample = Sample.get(id=dataJson.get('sample_id'))
    dm.sample_property = SampleProperty.select().where(SampleProperty.property == dataJson.get('field'))
    dm.value = dataJson.get('value')
    SampleMetadata.save(dm)
    return {}



def insertDataset():
    dataJson = request.get_json()
    s = Sample.get(id=dataJson.get("sample_id"))
    et = ExperimentType.get(name=dataJson.get("experiment_type"))
     
    Dataset.create(
        sample = s,
        experiment_type = et,
        release_status = "P"   
    )
     
    dataset = Dataset.select().order_by(Dataset.id.desc()).get()
    return json.dumps(dataset.toJson())


def getDonorProperties():
    recordList = []
    query = DonorProperty.select()
    for p in query:
        recordList.append(p.toJson())
    return json.dumps(recordList)


def getSampleProperties():
    recordList = []
    query = SampleProperty.select()
    for p in query:
        recordList.append(p.toJson())
    return json.dumps(recordList)