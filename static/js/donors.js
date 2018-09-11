/* jslint browser: true*/
/* global angular, Handsontable*/

import transformAPIResponse from './utils/transform-api-response'
import * as Renderer from './utils/hot-renderers'

const HTMLRenderer = Handsontable.renderers.Html || Handsontable.renderers.HtmlRenderer

const app = angular.module('DonorApp', ['ngHandsontable']);
app.controller('DonorCtrl', function($scope, $http) {

    $http.defaults.transformResponse = transformAPIResponse

    const self = this;

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
        const donor = $scope.searchParams.get('donor')
        const url = '/api/donors' + (donor ? `/${donor}` : '')
        $http.get(url)
        .then(result => {
            // Fill the grid with all existing donors
            $scope.donors = result.data;
            $scope.isLoading = false
        });
    };

    // Add a donor in the database
    this.save = function() {
        const data = $scope.donor;

        $http.post('/api/donor', data)
            .then(function(data, status, headers, config) {
                $scope.donor = {};
                self.load();
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

        const row    = change[0][0];
        const col    = change[0][1];
        const before = change[0][2];
        const after  = change[0][3];

        if (source === 'edit') {

            $http.post('/api/donor_metadata', {
                donor_id: $scope.donors[row].id,
                field: col,
                value: after
            });
        }
    };

    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Internal methods
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this._addMetaColumns = function(columns) {
        columns.forEach(p => {
            $scope.columns.push({
                data: p.property,
                title: p.property,
                readOnly: $scope.currentUser.can_edit ? false : true,
                width: 150,
                rendered: p.type === 'uri' ? Renderer.URI : Renderer.HTML
            });
        })
    };


    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Constructor
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    $scope.isLoading = true
    $scope.currentUser = {};
    $scope.donor = {};
    $scope.donors = [];
    $scope.donorPropertiesList = [];
    $scope.searchParams = new URLSearchParams(location.search);
    $scope.columns = [
        { data: 'public_name',  title: 'Public Name',   readOnly: true, readOnlyCellClassName:'roCell',   width: 120 },
        { data: 'private_name', title: 'Private Name',  readOnly: true, readOnlyCellClassName:'roCell',   width: 120, renderer: donorPrivateNameRenderer },
        { data: 'taxon_id',     title: 'Taxon ID',      readOnly: true, readOnlyCellClassName:'roCell' },
        { data: 'phenotype',    title: 'Phenotype',     readOnly: true, readOnlyCellClassName:'roCell',   width: 150 },
        { data: 'is_pool',      title: 'Pooled Sample', readOnly: true, readOnlyCellClassName:'roCell' }
    ];
    $scope.settings = {
        onAfterChange: function(change, source) { self.saveCell(change, source); }
    };

    // List of all existing species in database
    Promise.all([
        $http.get('/api/user/current'),
        $http.get('/api/donor_properties'),
    ])
    .then(([currentUser, donorPropertiesList]) => {
        $scope.currentUser = currentUser.data;
        $scope.donorPropertiesList = donorPropertiesList.data;

        this._addMetaColumns($scope.donorPropertiesList)

        $scope.$apply()
    });

    this.load();
});
