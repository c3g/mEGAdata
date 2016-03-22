/*jslint browser: true*/
/*global console, alert, d3, angular, Handsontable*/

var app = angular.module('DonorApp', ['angucomplete-alt', 'ngHandsontable']);
app.controller('DonorCtrl', function($scope, $http) {
    "use strict";
    var that = this;

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handsontable Renderers
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.donorPrivateNameRenderer = function(instance, td, row, col, prop, value, cellProperties) {
        Handsontable.renderers.HtmlRenderer.apply(this, arguments);
        var rowData = $scope.donors[cellProperties.row];
        if (rowData.public_name === null) {
            td.style.backgroundColor = '#CCE0EB';
        }
        if (value !== null) {
            td.innerHTML = "<a target='_blank' href='/sample/sample.html?donor=" + value + "'>" + value + "</a>";
        }
    };

    this.donorMetadataHtmlRenderer = function(instance, td, row, col, prop, value, cellProperties) {
        Handsontable.renderers.HtmlRenderer.apply(this, arguments);
        var rowData = $scope.donors[cellProperties.row];
        td.className = "metadata_cell";
    };

    this.donorMetadataUriRenderer = function(instance, td, row, col, prop, value, cellProperties) {
        Handsontable.renderers.HtmlRenderer.apply(this, arguments);
        var rowData = $scope.donors[cellProperties.row];
        td.className = "metadata_cell";
        if (value !== null) {
            td.innerHTML="<a target='_blank' href='" + value + "'>" + value + "</a>";
        }
    };

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Methods
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.load = function() {
        $http({
            method: 'GET',
            url: '/api/donors'
        }).then(drawGrid);

        //Fill the grid with all existing donors
        function drawGrid(result) {
            $scope.donors = result.data;
        }
    };

	//Add a donor in the database
    this.save = function() {
    	var data = $scope.donor;

    	$http.post('/api/donor', data)
    		.success(function(data, status, headers, config) {
                alert("Success.");
                $scope.donor = {};
                that.load();
    		})
        	.error(function(data, status, headers, config) {
        		alert("Donor creation failed.");
        	});
    };

    //Cancel button for both modal dialogs.
    this.cancel = function() {
    	//Nothing to do!
    };

	//Add donor metadata in the database
    this.saveCell = function(change, source) {
        if (source === "loadData") {
            return;
        }

        var row = change[0][0];
        var col = change[0][1];
        var before = change[0][2];
        var after = change[0][3];

        if (source === "edit") {
            var data = {
                donor_id: $scope.donors[row].id,
                field: col,
                value: after
            };

            $http.post('/api/donor_metadata', data);
        }
    };

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Internal methods
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

            if (p.type === "uri") {
                c.renderer = that.donorMetadataUriRenderer;
            }
            else {
                c.renderer = that.donorMetadataHtmlRenderer;
            }

            $scope.columns.push(c);
        }
    };


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Constructor
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	$scope.donor = {};
    $scope.donors = [];
    $scope.speciesList = [];
    $scope.columns = [
        { data: 'public_name', title: 'Public Name', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'private_name', title: 'Private Name', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'taxon_id', title: 'Taxon ID', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'phenotype', title: 'Phenotype', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'is_pool', title: 'Pooled Sample', readOnly: true, readOnlyCellClassName:"roCell" }
    ];
    $scope.settings = {
        onAfterChange: function(change, source) {that.saveCell(change, source);}
    };

	//List of all existing species in database
	$http({
		method: 'GET',
		url: '/api/species'
	}).success(function (result) {
		$scope.speciesList = result;
	});

	//List of all existing species in database
	$scope.donorPropertiesList = [];
	$http({
		method: 'GET',
		url: '/api/donor_properties'
	}).then(that._addMetaColumns);

    this.load();
});