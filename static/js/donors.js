/* jslint browser: true*/
/* global angular, Handsontable*/

import transformAPIResponse from './utils/transform-api-response'
import * as Renderer from './utils/hot-renderers'

const HTMLRenderer = Handsontable.renderers.Html || Handsontable.renderers.HtmlRenderer

const app = angular.module('DonorApp', ['ngHandsontable']);
app.controller('DonorCtrl', function($scope, $http) {

    $http.defaults.transformResponse = transformAPIResponse

    var that = this;

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Handsontable Renderers
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    function donorPrivateNameRenderer(instance, td, row, col, prop, value, cellProperties) {
        HTMLRenderer.apply(this, arguments);
        const rowData = $scope.donors[cellProperties.row];

        if (rowData.public_name === null)
            td.style.backgroundColor = '#CCE0EB';

        if (value !== null)
            td.innerHTML = '<a target=\'_blank\' href=\'/samples?donor=' + value + '\'>' + value + '</a>';
    }

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.load = () => {
        $http.get('/api/donors')
        .then(result => {
            // Fill the grid with all existing donors
            $scope.donors = result.data;
            $scope.isLoading = false
        });
    };

    // Add a donor in the database
    this.save = function() {
        var data = $scope.donor;

        $http.post('/api/donor', data)
            .then(function(data, status, headers, config) {
                $scope.donor = {};
                that.load();
            })
            .catch(function(data, status, headers, config) {
                alert('Donor creation failed.');
            });
    };

    // Cancel button for both modal dialogs.
    this.cancel = function() {
        // Nothing to do!
    };

    // Add donor metadata in the database
    this.saveCell = function(change, source) {
        if (source === 'loadData') {
            return;
        }

        var row = change[0][0];
        var col = change[0][1];
        var before = change[0][2];
        var after = change[0][3];

        if (source === 'edit') {
            var data = {
                donor_id: $scope.donors[row].id,
                field: col,
                value: after
            };

            $http.post('/api/donor_metadata', data);
        }
    };

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Internal methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this._addMetaColumns = function(result) {
        $scope.donorPropertiesList = result.data;
        for (var i in $scope.donorPropertiesList) {
            var p = $scope.donorPropertiesList[i];

            var c = {
                data: p.property,
                title: p.property,
                readOnly: false,
                width: 150
            };

            if (p.type === 'uri') {
                c.renderer = Renderer.URI;
            }
            else {
                c.renderer = Renderer.HTML;
            }

            $scope.columns.push(c);
        }
    };


    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Constructor
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    $scope.isLoading = true
    $scope.donor = {};
    $scope.donors = [];
    $scope.speciesList = [];
    $scope.donorPropertiesList = [];
    $scope.columns = [
        { data: 'public_name', title: 'Public Name', readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'private_name', title: 'Private Name', readOnly: true, readOnlyCellClassName:'roCell', renderer: donorPrivateNameRenderer },
        { data: 'taxon_id', title: 'Taxon ID', readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'phenotype', title: 'Phenotype', readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'is_pool', title: 'Pooled Sample', readOnly: true, readOnlyCellClassName:'roCell' }
    ];
    $scope.settings = {
        onAfterChange: function(change, source) { that.saveCell(change, source); }
    };

    // List of all existing species in database
    $http.get('/api/species')
    .then(result => {
        $scope.speciesList = result;
    });

    // List of all existing species in database
    $http.get('/api/donor_properties')
    .then(this._addMetaColumns);

    this.load();
});
