/* jslint browser: true*/
/* global angular, Handsontable*/

import transformAPIResponse from './utils/transform-api-response'
import * as Renderer from './utils/hot-renderers'
import queryString from './utils/query-string'
import { fetchCurrentUser } from './requests.js'


const app = angular.module('SampleApp', ['angucomplete-alt', 'ngHandsontable']);
app.config(['$interpolateProvider', (provider) => {
  provider.startSymbol('{:')
  provider.endSymbol(':}')
}])
app.controller('SampleCtrl', function($scope, $http) {
    $http.defaults.transformResponse = transformAPIResponse

    this.isMetadataCollapsed = false;


    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Handsontable Editors
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // CustomEditor will ask if an unreleased dataset should be released
    this.DatasetEditor = createEditor({
        getValue: (editor) => {},
        setValue: (editor, newValue) => {},
        open: (editor, ...args) => {
            editor.finishEditing();
            const row = editor.row
            const prop = editor.prop
            const sample = $scope.samples[row]
            const dataset = editor.originalValue
            this.onClickExperimentCell(dataset, sample, prop, row)
            // this._updateDataset(editor.row, editor.prop, editor.originalValue);
        },
        close: (editor) => {},
        focus: (editor) => {},
    })



    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.loadDonors = () => {
        const donor = $scope.searchParams.get('donor')
        let url = '/api/samples';

        if (donor) {
            url += '/donor/' + donor
            $scope.donorName = ' for ' + donor;
        } else if (Array.from($scope.searchParams.keys()).length > 0) {
            url += '/metadata' + location.search;
        }

        $http.get(url).then((result) => {
            $scope.isLoading = false
            $scope.samples = result.data
        });
    };

    this.loadDatasetDetails = (datasetID) => {
        Promise.all([
            $http.get(`/api/experiment_metadata/${datasetID}`),
            $http.get(`/api/track/${datasetID}`),
            $http.get(`/api/run/${datasetID}`)
        ])
        .then(([metadata, tracks, runs]) => {
            $scope.runModalView.metadata = metadata.data
            $scope.runModalView.publicTracks = tracks.data
            $scope.runModalView.runs = runs.data
            $scope.runModalView.isLoading = false
            $scope.$apply()
        })
    }

    // Add a sample in the database
    this.save = () => {
        $scope.sample.donor_id = $scope.sample.donor.originalObject.id;

        $http.post('/api/sample', $scope.sample)
            .then((response) => {
                alert('Success.');
                $scope.sample = {};
                this.loadDonors();
            })
            .catch((err) => {
                alert('Sample creation failed.');
            });
    };

    this.cancel = () => {
        // Nothing to do!
    };

    // Add sample metadata in the database
    this.onAfterChange = (change, source) => {
        if (source === 'loadData' || change === null)
            return;

        const row    = change[0][0];
        const col    = change[0][1];
        const before = change[0][2];
        const after  = change[0][3];

        if (/^datasets\./.test(col))
            return;

        this._saveMetadata(source, row, col, before, after);
    };

    this.onClickExperimentCell = (dataset, sample, prop, row) => {
        if (dataset && (dataset.runs.length > 0 || dataset.release_status === 'P')) {
            $scope.runModalView = {
                sample: sample,
                dataset: dataset,
                datasetName: prop.replace('datasets.', ''),
                metadata: [],
                runs: [],
                publicTracks: [],
                isLoading: true,
            }
            $scope.runModal.modal('show')
            $scope.$apply()

            this.loadDatasetDetails(dataset.id)
        }
    }

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Internal methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this._saveMetadata = (source, row, col, before, after) => {
        if (source === 'edit') {
            const data = {
                sample_id: $scope.samples[row].id,
                field: col,
                value: after
            };

            $http.post('/api/sample_metadata', data);
        }
    };

    this._updateDataset = (row, prop, data) => {
        const dataset = data === null ?
            {
                sample_id: $scope.samples[row].id,
                experiment_type: prop.replace('datasets.', ''),
                release_status: 'P',
            } :
            {
                id: data.id,
                release_status: 'P',
            };

        $http.post('/api/dataset', dataset)
            .then((response) => this.loadDonors())
            .catch((err) => alert('Dataset modification failed.'));
    };

    this._addMetaColumns = (columns) => {
        columns.forEach(p => {
            $scope.columns.push({
                data: p.property,
                title: p.property,
                readOnly: $scope.currentUser.can_edit ? false : true,
                width: 150,
                is_metadata_column: true,
                renderer: p.type === 'uri' ? Renderer.URI : Renderer.HTML,
            })
        })
    };

    this._addDatasetColumns = (columns) => {
        columns.forEach(p => {
            $scope.columns.push({
                data: `datasets.${p.name}`,
                title: p.name,
                readOnly: false,
                width: 100,
                renderer: Renderer.dataset,
                editor: this.DatasetEditor,
            })
        })
    };

    // Expand/Collapse metadata columns
    this.toggleMetadata = () => {
        this.isMetadataCollapsed = !this.isMetadataCollapsed;
        this._updateMetadataDimensions()
    }
    this.collapseMetadata = () => {
        this.isMetadataCollapsed = true
        this._updateMetadataDimensions()
    }
    this._updateMetadataDimensions = () => {
        const colwidth = this.isMetadataCollapsed ? 20 : 150;

        for (let c in $scope.columns) {
            const col = $scope.columns[c];

            if (col.is_metadata_column)
                col.width = colwidth;
        }
    }

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Constructor
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    $scope.isLoading = true
    $scope.currentUser = {};
    $scope.sample = {};
    $scope.samples = [];
    $scope.experimentTypeList = [];
    $scope.samplePropertiesList = [];
    $scope.dataset = {};
    $scope.searchParams = new URLSearchParams(location.search);
    $scope.columns = [
        { data: 'public_name',        title: 'Public Name',      readOnly: true, readOnlyCellClassName: 'roCell',   width: 120 },
        { data: 'private_name',       title: 'Private Name',     readOnly: true, readOnlyCellClassName: 'roCell',   width: 120 },
        { data: 'donor.private_name', title: 'Donor',            readOnly: true, readOnlyCellClassName: 'roCell',   renderer: Renderer.donor },
        { data: 'EGA_EGAN',           title: 'EGA EGAN',         readOnly: true, readOnlyCellClassName: 'roCell' },
        { data: 'biomaterial_type',   title: 'Biomaterial Type', readOnly: true, readOnlyCellClassName: 'roCell' },
    ];
    $scope.settings = {
        onAfterChange: this.onAfterChange
    };
    $scope.addSampleButton = $('#addSampleButton')
    $scope.addSampleModal  = $('#addSampleModal').modal('hide')

    $scope.runModalView    = { sample: {}, dataset: {}, datasetName: '', metadata: [], runs: [], publicTracks: [], isLoading: false }
    $scope.runModal        = $('#runModal').modal('hide')

    $scope.addSampleButton.on('click', () => {
        $scope.addSampleModal.modal('show')
    })

    // Load list of sample metadata + experiments fields and add columns
    // Load list of sample metadata + experiments fields and add columns
    Promise.all([
        $http.get('/api/user/current'),
        $http.get('/api/sample_properties'),
        $http.get('/api/experiment_types')
    ])
    .then(([currentUser, resultSample, resultExperiment]) => {
        $scope.currentUser          = currentUser.data;
        $scope.samplePropertiesList = resultSample.data;
        $scope.experimentTypeList   = resultExperiment.data;

        this._addMetaColumns($scope.samplePropertiesList);
        this._addDatasetColumns($scope.experimentTypeList);

        $scope.$apply()
    })

    this.loadDonors();
});


function createEditor(methods) {
    const Editor = Handsontable.editors.BaseEditor.prototype.extend();

    for (let name in methods) {
        let method = methods[name]
        Editor.prototype[name] = function(...args) { return method(this, ...args) }
    }

    return Editor
}
