#!/usr/bin/python
import requests
from flask import Response
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
    return JSONResponse(insertDataset())


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
    return JSONResponse(createUser())


@app.route("/api/user/update", methods=['POST'])
@login_required
def route_api_user_update():
    return JSONResponse(updateUser())


@app.route("/api/user/delete", methods=['POST'])
@login_required
def route_api_user_delete():
    return JSONResponse(deleteUser())


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
    """Returns all properties that can be specified for a donor."""
    return JSONResponse(getDonorProperties())


@app.route("/api/donor", methods=['POST'])
@login_required
def route_api_donor_add():
    return JSONResponse(insertDonor())


@app.route("/api/donor_metadata", methods=['POST'])
@login_required
def route_api_donor_metadata_add():
    return JSONResponse(insertDonorMetadata())


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
    return JSONResponse(insertSample())


@app.route("/api/sample_metadata", methods=['POST'])
@login_required
def route_api_sample_metadata_add():
    return JSONResponse(insertSampleMetadata())



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
