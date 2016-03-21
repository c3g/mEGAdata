#!/usr/bin/python
from app import app
from flask.ext.stormpath import login_required, groups_required
import requests
from flask import Response
from queries import *


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dataset
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/api/dataset", methods=['POST'])
# @login_required
def route_api_dataset_add():
    return Response(insertDataset(), mimetype='application/json')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Donor
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/api/donors", methods=['GET'])
@app.route("/api/donors/<string:filter>", methods=['GET'])
# @login_required
def route_api_get_donors(filter=None):
    """Returns all registered donors. If a filter string is provided, returns filtered list of registered donors."""
    return Response(getDonorList(filter), mimetype='application/json')


@app.route("/api/donor_properties", methods=['GET'])
# @login_required
def route_api_get_donor_properties(filter=None):
    """Returns all properties that can be specified for a donor."""
    return Response(getDonorProperties(), mimetype='application/json')


@app.route("/api/donor", methods=['POST'])
# @login_required
def route_api_donor_add():
    return Response(insertDonor(), mimetype='application/json')


@app.route("/api/donor_metadata", methods=['POST'])
# @login_required
def route_api_donor_metadata_add():
    return Response(insertDonorMetadata(), mimetype='application/json')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Experiment
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/api/experiments")
# @login_required
def route_json_experimentList():
    return Response(getExperimentList(), mimetype='application/json')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sample
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/api/samples", methods=['GET'])
@app.route("/api/samples/<donor>")
# @login_required
def route_json_sampleList(donor=None):
    return Response(getSampleList(donor), mimetype='application/json')


@app.route("/api/sample_properties", methods=['GET'])
# @login_required
def route_api_get_sample_properties(filter=None):
    """Returns all properties that can be specified for a sample."""
    return Response(getSampleProperties(), mimetype='application/json')


@app.route("/api/sample", methods=['POST'])
# @login_required
def route_api_sample_add():
    return Response(insertSample(), mimetype='application/json')


@app.route("/api/sample_metadata", methods=['POST'])
# @login_required
def route_api_sample_metadata_add():
    return Response(insertSampleMetadata(), mimetype='application/json')



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Species
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/api/species", methods=['GET'])
# @login_required
def route_api_get_species():
    """Returns all support species with this instance of mEGAdata."""
    return Response(getSpeciesList(), mimetype='application/json')