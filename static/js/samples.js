/* jslint browser: true*/
/* global angular, Handsontable*/

import transformAPIResponse from './utils/transform-api-response'
import * as Renderer from './utils/hot-renderers'
import queryString from './utils/query-string'


const app = angular.module('SampleApp', ['angucomplete-alt', 'ngHandsontable']);
app.controller('SampleCtrl', function($scope, $http) {
    $http.defaults.transformResponse = transformAPIResponse

    this.is_metadata_collapsed = false;


    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Handsontable Editors
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // CustomEditor will ask if an unreleased dataset should be released
    this.DatasetEditor = createEditor({
        getValue: () => {},
        setValue: (newValue) => {},
        open: (editor, ...args) => {
            editor.finishEditing();
            this._updateDataset(editor.row, editor.prop, editor.originalValue);
        },
        close: () => {},
        focus: () => {},
    })



    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.load = () => {
        let url = '/api/samples';

        if ('donor' in $scope.queryDict) {
            url += '/donor/' + $scope.queryDict['donor'];
            $scope.donorName = ' for ' + $scope.queryDict['donor'];
        } else if (Object.keys($scope.queryDict).length > 0) {
            url += '/metadata?' + queryString($scope.queryDict);
        }

        $http.get(url).then((result) => {
            $scope.isLoading = false
            $scope.samples = result.data
        });
    };

    // Add a sample in the database
    this.save = () => {
        $scope.sample.donor_id = $scope.sample.donor.originalObject.id;

        $http.post('/api/sample', $scope.sample)
            .then((response) => {
                alert('Success.');
                $scope.sample = {};
                this.load();
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
        if (source === 'loadData' || /^datasets\./.test(col))
            return;

        const row    = change[0][0];
        const col    = change[0][1];
        const before = change[0][2];
        const after  = change[0][3];

        this._saveMetadata(source, row, col, before, after);
    };

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
            .then((response) => this.load())
            .catch((err) => alert('Dataset modification failed.'));
    };

    this._addMetaColumns = (result) => {

        $scope.samplePropertiesList = result.data;

        for (let i in $scope.samplePropertiesList) {
            const p = $scope.samplePropertiesList[i];

            $scope.columns.push({
                data: p.property,
                title: p.property,
                readOnly: false,
                width: 150,
                is_metadata_column: true,
                renderer: p.type === 'uri' ? Renderer.URI : Renderer.HTML,
            });
        }
    };

    this._addExperimentColumns = (result) => {

        for (let i in $scope.experimentTypeList) {
            const p = $scope.experimentTypeList[i];

            $scope.columns.push({
                data: `datasets.${p.name}`,
                title: p.name,
                readOnly: false,
                width: 100,
                renderer: Renderer.dataset,
                editor: this.DatasetEditor,
            });
        }
    };

    // Expand/Collapse metadata columns
    this.toggleMetadata = () => {
        this.is_metadata_collapsed = !this.is_metadata_collapsed;
        this._updateMetadataDimensions()
    }
    this.collapseMetadata = () => {
        this.is_metadata_collapsed = true
        this._updateMetadataDimensions()
    }
    this._updateMetadataDimensions = () => {
        const colwidth = this.is_metadata_collapsed ? 20 : 150;

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
    $scope.sample = {};
    $scope.samples = [];
    $scope.experimentTypeList = [];
    $scope.samplePropertiesList = [];
    $scope.dataset = {};
    $scope.queryDict = {};

    // Extract GET parameters to a dictionary
    if (location.search !== '') {
        location.search.substr(1).split('&').forEach((item) => { $scope.queryDict[item.split('=')[0]] = item.split('=')[1]; });
    }

    $scope.columns = [
        { data: 'public_name',        title: 'Public Name',         readOnly: true, readOnlyCellClassName:'roCell',   width: 120 },
        { data: 'private_name',       title: 'Private Name',        readOnly: true, readOnlyCellClassName:'roCell',   width: 120 },
        { data: 'donor.private_name', title: 'Donor',               readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'EGA_EGAN',           title: 'EGA EGAN',            readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'biomaterial_type',   title: 'Biomaterial Type',    readOnly: true, readOnlyCellClassName:'roCell' },
    ];

    $scope.settings = {
        onAfterChange: this.onAfterChange
    };

    // Load list of sample metadata fields and add columns
    $http.get('/api/sample_properties')
    .then(this._addMetaColumns);

    // Load list of experiments  and add a column for each
    $http.get('/api/experiment_types')
    .then((result) => {
        $scope.experimentTypeList = result.data;
        this._addExperimentColumns();
    });

    this.load();
});


function createEditor(methods) {
    const Editor = Handsontable.editors.BaseEditor.prototype.extend();

    for (let name in methods) {
        let method = methods[name]
        Editor.prototype[name] = function(...args) { return method(this, ...args) }
    }

    return Editor
}
