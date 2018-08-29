#!/usr/bin/python

from models import Dataset, Donor, DonorMetadata, DonorProperty, ExperimentMetadata, ExperimentProperty, ExperimentType
from models import PublicTrack, User, Sample, SampleMetadata, SampleProperty, Species, Run, RunFile

#==============================================================================~
# User
#==============================================================================~

def listUsers():
    return [user.toJSON() for user in User.select()]

def createUser(body):
    user = User(email=body['email'])
    user.save()

    return user.toJSON()

def updateUser(body):
    user = User.get(User.id == body['id'])
    user.name = body['name']
    user.email = body['email']
    user.can_edit = body['can_edit']
    user.save()

    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'can_edit': user.can_edit,
    }

def deleteUser(body):
    user = User.get(User.id == body['id'])
    user.delete_instance()

    return {'ok': True}


#==============================================================================~
# Donor
#==============================================================================~

def getDonorList(pFilter=None):
    donorsByID = {}

    query = Donor.select()
    if pFilter:
        query = query.where(Donor.private_name.contains(pFilter))

    donorsByID = {donor.id: donor.toJSON() for donor in query}

    appendDonorsMetadata(donorsByID, pFilter)

    return donorsByID.values()

def insertDonor(dataJson):
    Donor.create(
        public_name=dataJson.get('public_name'),
        private_name=dataJson.get('private_name'),
        taxon_id=dataJson.get("taxon_id"),
        phenotype=dataJson.get("phenotype"),
        is_pool=dataJson.get("is_pool"),
    )

    donor = Donor.select().order_by(Donor.id.desc()).get()
    return donor.toJSON()

def insertDonorMetadata(dataJson):
    dm = DonorMetadata()
    dm.donor = Donor.get(id=dataJson.get('donor_id'))
    try:
        dm.donor_property = DonorProperty.get(DonorProperty.property == dataJson.get('field'))
    except:
        insertDonorProperty({
            'property': dataJson.get('field'),
            'type': 'text',
            'is_exported_to_ega': False,
        })
        dm.donor_property = DonorProperty.get(DonorProperty.property == dataJson.get('field'))
    dm.value = dataJson.get('value')
    DonorMetadata.save(dm)
    return {}

def insertDonorProperty(dataJson):
    p = DonorProperty()
    p.property = dataJson.get('property')
    p.type = dataJson.get('type')
    p.is_exported_to_ega = dataJson.get('is_exported_to_ega')
    DonorProperty.save(p)
    return p.toJSON()

def appendDonorsMetadata(recordList, pFilter=None):
    query = DonorMetadata.select(DonorMetadata, Donor.id.alias('donor_id'), DonorProperty.property.alias('property')).join(Donor).switch(DonorMetadata).join(DonorProperty)
    if pFilter:
        query = query.where(Donor.private_name.contains(pFilter))

    for dm in query.naive():
        recordList[dm.donor_id][dm.property] = dm.value


#==============================================================================~
# Sample
#==============================================================================~

def getSampleList(donor=None, filter={}):
    """
    Returns list of samples in JSON format. If a donor object was provided, returns
    only samples that belong to that donor.
    Metadata can also be used to filter samples.
    """

    query = Sample.select(Sample, Donor).join(Donor)

    if len(filter) > 0:
        for prop in filter:
            sp = SampleProperty.select().where(SampleProperty.property == prop)
            query = query.switch(Sample).join(SampleMetadata).where(SampleMetadata.sample_property == sp, SampleMetadata.value == filter[prop])

    # Refine based on donor
    if donor is not None:
        query = query.where(Donor.private_name == donor)

    samplesByID = {}

    for sample in query:
        sampleRecord = sample.toJSON()

        datasetByExperiment = {}

        for dataset in getDatasetsForSample(sample.id):
            datasetResult = {
                'id': dataset.id,
                'release_status': dataset.release_status or None,
                'runs': getRunsForDataset(dataset.id)
            }
            datasetByExperiment[dataset.experiment_type.name] = datasetResult

        sampleRecord['datasets'] = datasetByExperiment
        samplesByID[sample.id] = sampleRecord

    appendSamplesMetadata(samplesByID)

    return samplesByID.values()

def appendSamplesMetadata(recordList):
    query = SampleMetadata.select(SampleMetadata, Sample.id.alias('sample_id'), SampleProperty.property.alias('property'))\
        .join(Sample)\
        .switch(SampleMetadata).join(SampleProperty)\
        .naive()

    for dm in query:
        if dm.sample_id in recordList:
            recordList[dm.sample_id][dm.property] = dm.value

def insertSample(dataJson):
    d = Donor.get(id=dataJson.get("donor_id"))

    Sample.create(
        public_name=dataJson.get('public_name'),
        private_name=dataJson.get('private_name'),
        donor=d
    )

    sample = Sample.select().order_by(Sample.id.desc()).get()
    return sample.toJSON()

def insertSampleMetadata(dataJson):
    s = Sample.get(id=dataJson.get('sample_id'))

    # Create property in database if it doesn't exist
    try:
        sp = SampleProperty.get(SampleProperty.property == dataJson.get('field'))
    except:
        insertSampleProperty({
            'property': dataJson.get('field'),
            'type': 'text',
            'is_exported_to_ega': False,
        })
        sp = SampleProperty.get(SampleProperty.property == dataJson.get('field'))

    # If a value already exists for this sample/property, just update the record
    try:
        dm = SampleMetadata.get(SampleMetadata.sample == s, SampleMetadata.sample_property == sp)
    except:
        dm = SampleMetadata()
        dm.sample = s
        dm.sample_property = sp

    dm.value = dataJson.get('value')
    SampleMetadata.save(dm)
    return {}

def insertSampleProperty(dataJson):
    p = SampleProperty()
    p.property = dataJson.get('property')
    p.type = dataJson.get('type')
    p.is_exported_to_ega = dataJson.get('is_exported_to_ega')
    SampleProperty.save(p)
    return p.toJSON()

def getSamplePropertiesNames():
    names = []
    for p in SampleProperty.select():
        names.append(p.property)
    return sorted(list(set(names)))


#==============================================================================~
# Dataset
#==============================================================================~

def insertDataset(dataJson):
    if dataJson.has_key('id'):
        return updateDataset(dataJson)

    s = Sample.get(id=dataJson.get("sample_id"))
    et = ExperimentType.get(ihec_name=dataJson.get("experiment_type"))

    Dataset.create(
        sample=s,
        experiment_type=et,
        release_status=dataJson.get("release_status") if dataJson.get("release_status") != None else "P"
    )

    dataset = Dataset.select().order_by(Dataset.id.desc()).get()
    return dataset.toJSON()

def updateDataset(dataJson):
    dataset = Dataset.get(id=dataJson['id'])

    for key in dataJson.keys():
        if key == 'id':
            continue
        if hasattr(dataset, key):
            setattr(dataset, key, dataJson[key])

    dataset.save()
    return dataset.toJSON()

def insertExperimentMetadata(dataJson):
    dm = ExperimentMetadata()
    dm.dataset = Dataset.get(id=dataJson.get('dataset_id'))
    try:
        dm.experiment_property = ExperimentProperty.get(ExperimentProperty.property == dataJson.get('field'))
    except:
        insertExperimentProperty({
            'property': dataJson.get('field'),
            'type': 'text',
            'is_exported_to_ega': False,
        })
        dm.experiment_property = ExperimentProperty.get(ExperimentProperty.property == dataJson.get('field'))
    dm.value = dataJson.get('value')
    ExperimentMetadata.save(dm)
    return {}

def insertExperimentProperty(dataJson):
    p = ExperimentProperty()
    p.property = dataJson.get('property')
    p.type = dataJson.get('type')
    p.is_exported_to_ega = dataJson.get('is_exported_to_ega')
    ExperimentProperty.save(p)
    return p.toJSON()

def getDatasetsForSample(sampleID):
    query = Dataset.select(Dataset, ExperimentType, Sample)\
                   .join(ExperimentType).switch(Dataset).join(Sample)\
                   .where(Sample.id == sampleID)

    return query

def getExperimentPropertiesNames():
    names = []
    for p in ExperimentProperty.select():
        names.append(p.property)
    return sorted(list(set(names)))

#==============================================================================~
# Run
#==============================================================================~

def insertRun(data):
    dataset = Dataset.get(id=data['dataset_id'])

    run = Run()
    run.dataset = dataset
    run.library_name = data['library_name']
    run.run = data['run']
    run.lane = data['lane']
    run.save()

    if data.has_key('files'):
        for f in data['files']:
            file = RunFile()
            file.run_id = run.id
            file.name = f['name']
            file.md5 = f['md5']
            file.encrypted_md5 = f['encrypted_md5']
            file.save()

    return run.toJSON()


def getRunsForDataset(datasetID, attach_files=False):
    query = Run.select().join(Dataset).where(Dataset.id == datasetID)

    runs = []
    for row in query:
        run = {
            'id': row.id,
            'library_name': row.library_name,
            'run': row.run,
            'lane': row.lane,
            'EGA_EGAR': row.EGA_EGAR
        }
        if attach_files:
            run['files'] = [{
                'name': file.name,
                'md5': file.md5,
                'encrypted_md5': file.encrypted_md5,
            } for file in RunFile.select().where(RunFile.run_id == row.id)]

        runs.append(run)

    return runs


#==============================================================================~
# RunFile
#==============================================================================~

def getRunFilesForRun(runID):
    query = RunFile.select().where(RunFile.run_id == runID)

    files = []
    for file in query:
        files.append({
            'id': file.id,
            'name': file.name,
            'md5': file.md5,
            'encrypted_md5': file.encrypted_md5,
        })

    return files


#==============================================================================~
# Other
#==============================================================================~

def getDonorProperties():
    """
    Returns all information on available donor properties in a JSON document, ordered by id.
    """
    return [p.toJSON() for p in DonorProperty.select()]


def getSampleProperties():
    """
    Returns all information on available sample properties in a JSON document, ordered by id.
    """
    return [p.toJSON() for p in SampleProperty.select()]

def getSpeciesList():
    """
    Returns all information on species in a JSON document.
    """
    return [species.toJSON() for species in Species.select()]

def getExperimentTypeList():
    return [exp.toJSON() for exp in ExperimentType.select()]

def getPublicTracksList(dataset_id):
    """
    Returns all the tracks for a dataset
    """
    return [track.toJSON() for track in PublicTrack.select().where(PublicTrack.dataset_id == dataset_id)]

def getExperimentMetadata(dataset_id):
    """
    Returns all the experiment metadata for a dataset
    """
    return [
        {
            'property': metadata.experiment_property.property,
            'type': metadata.experiment_property.type,
            'value': metadata.value,
        }
        for metadata in ExperimentMetadata.select().where(ExperimentMetadata.dataset_id == dataset_id)]
