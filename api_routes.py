#!/usr/bin/python
from functools import wraps
from flask import Response, request, current_app
from flask_login import login_required, current_user

from app import app
from queries import *

def JSONResponse(value):
    return Response(json.dumps(value), mimetype='application/json')

# API Functions decorator.
# Makes all functions return { ok: true|false, ... }
def api_function(edit=False):
    def decorator(fn):
        @wraps(fn)
        def fn_wrapped(*args, **kwargs):
            print current_user.can_edit
            # Login required
            if not current_user.is_authenticated:
                return JSONResponse({'ok': False, 'message': 'Not logged in'})
            # user.can_edit
            if edit and not current_user.can_edit:
                return JSONResponse({'ok': False, 'message': 'Current user cannot edit content'})
            try:
                return JSONResponse({'ok': True, 'data': fn(*args, **kwargs)})
            except Exception as e:
                return JSONResponse({'ok': False, 'message': str(e)})
        return fn_wrapped
    return decorator


#==============================================================================
# Dataset
#==============================================================================

@app.route("/api/dataset", methods=['POST'])
@api_function(edit=True)
def _dataset_add():
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

    return insertedDataset


#==============================================================================
# Run
#==============================================================================

@app.route('/api/run', methods=['POST'])
@api_function(edit=True)
def _run_create():
    return insertRun(request.get_json())

@app.route('/api/run/<string:dataset_id>', methods=['GET'])
@api_function()
def _run_get(dataset_id):
    return getRunsForDataset(dataset_id, attach_files=True)

#==============================================================================
# Users
#==============================================================================

@app.route("/api/user/list", methods=['GET'])
@api_function()
def _user_list():
    return listUsers()

@app.route("/api/user/current", methods=['GET'])
@api_function()
def _user_current():
    return current_user.toJSON()

@app.route("/api/user/create", methods=['POST'])
@api_function(edit=True)
def _user_create():
    return createUser(request.get_json())

@app.route("/api/user/update", methods=['POST'])
@api_function(edit=True)
def _user_update():
    return updateUser(request.get_json())

@app.route("/api/user/delete", methods=['POST'])
@api_function(edit=True)
def _user_delete():
    return deleteUser(request.get_json())


#==============================================================================
# Donor
#==============================================================================

@app.route("/api/donors", methods=['GET'])
@app.route("/api/donors/<string:filter>", methods=['GET'])
@api_function()
def _get_donors(filter=None):
    """
    Returns all registered donors. If a filter string is provided, returns filtered list of registered donors.
    """
    return getDonorList(filter)


@app.route("/api/donor_properties", methods=['GET'])
@api_function()
def _get_donor_properties(filter=None):
    """
    Returns all properties that can be specified for a donor.
    """
    return getDonorProperties()

@app.route("/api/donor", methods=['POST'])
@api_function(edit=True)
def _donor_add():
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

    return insertedDonor


@app.route("/api/donor_metadata", methods=['POST'])
@api_function(edit=True)
def _donor_metadata_add():
    return insertDonorMetadata(request.get_json())


#==============================================================================
# Experiment Types
#==============================================================================

@app.route("/api/experiment_types")
@api_function()
def route_json_experimentList():
    return getExperimentTypeList()


#==============================================================================
# Experiment Metadata
#==============================================================================

@app.route("/api/experiment_metadata/<string:dataset_id>")
@api_function()
def route_json_experiment_metadata_get(dataset_id):
    return getExperimentMetadata(dataset_id)


#==============================================================================
# Sample
#==============================================================================

@app.route("/api/samples", methods=['GET'])
@app.route("/api/samples/donor/<string:donor>", methods=['GET'])
@api_function()
def route_json_sampleList(donor=None):
    return getSampleList(donor=donor)


@app.route("/api/samples/metadata", methods=['GET'])
@api_function()
def route_json_sampleList_metadata_filter():
    return getSampleList(filter=request.args)


@app.route("/api/sample_properties", methods=['GET'])
@api_function()
def _get_sample_properties(filter=None):
    """
    Returns all properties that can be specified for a sample.
    """
    return getSampleProperties()


@app.route("/api/sample_properties/names", methods=['GET'])
@api_function()
def _get_sample_properties_names():
    return getSamplePropertiesNames()


@app.route("/api/sample", methods=['POST'])
@api_function(edit=True)
def _sample_add():
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

    return insertedSample


@app.route("/api/sample_metadata", methods=['GET'])
@api_function()
def _sample_metadata_get():
    return getSampleMetadataList()


@app.route("/api/sample_metadata", methods=['POST'])
@api_function(edit=True)
def _sample_metadata_add():
    return insertSampleMetadata(request.get_json())


#==============================================================================
# Species
#==============================================================================

@app.route("/api/species", methods=['GET'])
@api_function()
def _get_species():
    """
    Returns all support species with this instance of mEGAdata.
    """
    return getSpeciesList()


#==============================================================================
# Tracks
#==============================================================================

@app.route("/api/track/<string:dataset_id>", methods=['GET'])
@api_function()
def _tracks_get(dataset_id):
    """
    Returns all the tracks for a dataset
    """
    return getPublicTracksList(dataset_id)
