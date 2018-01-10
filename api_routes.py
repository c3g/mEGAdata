#!/usr/bin/python
import requests
from flask import Response, request
from flask.ext.login import login_required

from app import app
from queries import *

def JSONResponse(value):
    return Response(json.dumps(value), mimetype='application/json')

#==============================================================================
# Dataset
#==============================================================================

@app.route("/api/dataset", methods=['POST'])
@login_required
def route_api_dataset_add():
    dataset = request.get_json()
    insertedDataset = insertDataset(dataset)

    if dataset.has_key('metadata'):
        metadata = dataset['metadata']
        for field in metadata.keys():
            value = metadata[field]
            insertExperimentMetadata({
                'dataset_id': insertedDataset['id'],
                'field': field,
                'value': value
            })

    return JSONResponse(insertedDataset)


#==============================================================================
# Users
#==============================================================================

@app.route("/api/user/list", methods=['GET'])
@login_required
def route_api_user_list():
    return JSONResponse(listUsers())

@app.route("/api/user/create", methods=['POST'])
@login_required
def route_api_user_create():
    return JSONResponse(createUser(request.get_json()))


@app.route("/api/user/update", methods=['POST'])
@login_required
def route_api_user_update():
    return JSONResponse(updateUser(request.get_json()))


@app.route("/api/user/delete", methods=['POST'])
@login_required
def route_api_user_delete():
    return JSONResponse(deleteUser(request.get_json()))


#==============================================================================
# Donor
#==============================================================================

@app.route("/api/donors", methods=['GET'])
@app.route("/api/donors/<string:filter>", methods=['GET'])
@login_required
def route_api_get_donors(filter=None):
    """
    Returns all registered donors. If a filter string is provided, returns filtered list of registered donors.
    """
    return JSONResponse(getDonorList(filter))


@app.route("/api/donor_properties", methods=['GET'])
@login_required
def route_api_get_donor_properties(filter=None):
    """
    Returns all properties that can be specified for a donor.
    """
    return JSONResponse(getDonorProperties())

@app.route("/api/donor", methods=['POST'])
@login_required
def route_api_donor_add():
    donor = request.get_json()
    insertedDonor = insertDonor(donor)

    if donor.has_key('metadata'):
        metadata = donor['metadata']
        for field in metadata.keys():
            value = metadata[field]
            insertDonorMetadata({
                'donor_id': insertedDonor['id'],
                'field': field,
                'value': value
            })

    return JSONResponse(insertedDonor)


@app.route("/api/donor_metadata", methods=['POST'])
@login_required
def route_api_donor_metadata_add():
    return JSONResponse(insertDonorMetadata(request.get_json()))



#==============================================================================
# Experiment Types
#==============================================================================

@app.route("/api/experiment_types")
@login_required
def route_json_experimentList():
    return JSONResponse(getExperimentTypeList())


#==============================================================================
# Sample
#==============================================================================

@app.route("/api/samples", methods=['GET'])
@app.route("/api/samples/donor/<string:donor>", methods=['GET'])
@login_required
def route_json_sampleList(donor=None):
    return JSONResponse(getSampleList(donor=donor))


@app.route("/api/samples/metadata", methods=['GET'])
@login_required
def route_json_sampleList_metadata_filter():
    return JSONResponse(getSampleList(filter=request.args))


@app.route("/api/sample_properties", methods=['GET'])
@login_required
def route_api_get_sample_properties(filter=None):
    """
    Returns all properties that can be specified for a sample.
    """
    return JSONResponse(getSampleProperties())


@app.route("/api/sample", methods=['POST'])
@login_required
def route_api_sample_add():
    sample = request.get_json()
    insertedSample = insertSample(sample)

    if sample.has_key('metadata'):
        metadata = sample['metadata']
        for field in metadata.keys():
            value = metadata[field]
            insertSampleMetadata({
                'sample_id': insertedSample['id'],
                'field': field,
                'value': value
            })

    return JSONResponse(insertedSample)


@app.route("/api/sample_metadata", methods=['POST'])
@login_required
def route_api_sample_metadata_add():
    return JSONResponse(insertSampleMetadata(request.get_json()))



#==============================================================================
# Species
#==============================================================================

@app.route("/api/species", methods=['GET'])
@login_required
def route_api_get_species():
    """
    Returns all support species with this instance of mEGAdata.
    """
    return JSONResponse(getSpeciesList())
