/*jslint browser: true*/
/*global console, alert, d3, $, angular, Handsontable*/

var app = angular.module('SampleApp', ["angucomplete-alt", 'ngHandsontable']);
app.controller('SampleCtrl', function($scope, $http) {
	"use strict";
	var that = this;
    that.is_metadata_collapsed = false;

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handsontable Renderers
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.releaseStatusRenderer = function(instance, td, row, col, prop, value, cellProperties) {
		Handsontable.renderers.TextRenderer.apply(this, arguments);
		td.style.fontWeight = "900";
		td.style.textAlign = "center";
        td.className = "dataset_release_cell";

		if (value === null) {
			cellProperties.readOnly = false;
			return;
		}
		else if (value.slice(0,2) === "R_") {
			td.style.backgroundColor = '#FF6666';
			cellProperties.readOnly = true;
		}
		else if (value.charAt(0) === "R") {
			td.style.color = 'green';
			cellProperties.readOnly = true;
		}
		else if (value.charAt(0) === "P") {
			td.style.color = 'green';
			td.style.backgroundColor = 'rgba(150, 235, 0, 0.27)';
			cellProperties.readOnly = true;
		}
    };


    this.sampleMetadataHtmlRenderer = function(instance, td, row, col, prop, value, cellProperties) {
		Handsontable.renderers.HtmlRenderer.apply(this, arguments);
        var rowData = $scope.samples[cellProperties.row];
        td.className = "metadata_cell";
    };


	this.sampleMetadataUriRenderer = function(instance, td, row, col, prop, value, cellProperties) {
        Handsontable.renderers.HtmlRenderer.apply(this, arguments);
        var rowData = $scope.samples[cellProperties.row];
        td.className = "metadata_cell";
        if (value !== null) {
            td.innerHTML="<a target='_blank' href='" + value + "'>" + value + "</a>";
        }
    };




//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handsontable Editors
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  	//CustomEditor will ask if an unreleased dataset should be released
    this.DatasetEditor = Handsontable.editors.BaseEditor.prototype.extend();
    this.DatasetEditor.prototype.getValue = function() {};
    this.DatasetEditor.prototype.setValue = function(newValue) {};
    this.DatasetEditor.prototype.open = function() {this.finishEditing();};
    this.DatasetEditor.prototype.close = function() {};
    this.DatasetEditor.prototype.focus = function() {};



//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Methods
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    this.load = function() {
        var url = "/api/samples";
        if ("donor" in $scope.queryDict) {
            url += "/donor/" + $scope.queryDict["donor"];
            $scope.donorName = " for " + $scope.queryDict["donor"];
        }
        else if (Object.keys($scope.queryDict).length > 0) {
            var params = [];
            for (var key in $scope.queryDict) {
                params.push(key + "=" + $scope.queryDict[key]);
            }
            url += "/metadata?" + params.join("&");
        }


        $http({
            method: 'GET',
            url: url
        }).then(drawGrid);

        //Fill the grid with all existing samples
        function drawGrid(result) {
            $scope.samples = result.data;
        }
    };

	//Add a sample in the database
    this.save = function() {
        $scope.sample.donor_id = $scope.sample.donor.originalObject.id;
    	var data = $scope.sample;

    	$http.post('/api/sample', data)
    		.success(function(data, status, headers, config) {
                alert("Success.");
                $scope.sample = {};
                that.load();
    		})
        	.error(function(data, status, headers, config) {
        		alert("Sample creation failed.");
        	});
    };


    this.cancel = function() {
    	//Nothing to do!
    };

	//Add sample metadata in the database
    this.saveCell = function(change, source) {
        if (source === "loadData") {
            return;
        }

        var row = change[0][0];
        var col = change[0][1];
        var before = change[0][2];
        var after = change[0][3];

		var experiment_types = $scope.experimentTypeList.reduce(function(a, b) { a[b.name] = b; return a; }, {});
		var properties = $scope.samplePropertiesList.reduce(function(a, b) { a[b.property] = b; return a; }, {});

		if (col in properties) {
			that._saveMetadata(source, row, col, before, after);
		}
		if (col in experiment_types) {
			that._saveDataset(source, row, col, before, after);
		}

    };


    this.collapseMetadata = function() {
        that.is_metadata_collapsed = !that.is_metadata_collapsed;
        var colwidth = 150;
        if (that.is_metadata_collapsed) {
            colwidth = 20;
        }

        for (var c_idx in $scope.columns) {
            var col = $scope.columns[c_idx];
            if (col.is_metadata_column) {
                col.width = colwidth;
            }
        }
    }


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Internal methods
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	this._saveMetadata = function(source, row, col, before, after) {
        if (source === "edit") {
            var data = {
                sample_id: $scope.samples[row].id,
                field: col,
                value: after
            };

            $http.post('/api/sample_metadata', data);
        }
	};

	this._saveDataset = function(source, row, col, before, after) {
        if (source === "edit") {
			var data = {
				sample_id: $scope.samples[row].id,
				experiment_type: col
			};

			$http.post('/api/dataset', data)
				.success(function(data, status, headers, config) {
					that.load();
				})
				.error(function(data, status, headers, config) {
					alert("Dataset modification failed.");
				});
        }
	};


	this._addMetaColumns = function(result) {
        $scope.samplePropertiesList = result.data;
        for (var i in $scope.samplePropertiesList) {
            var p = $scope.samplePropertiesList[i];

            var c = {
                data: p.property,
                title: p.property,
                readOnly: false,
                width: 150,
                is_metadata_column: true
            };

            if (p.type === "uri") {
                c.renderer = that.sampleMetadataUriRenderer;
            }
            else {
                c.renderer = that.sampleMetadataHtmlRenderer;
            }

            $scope.columns.push(c);
        }
    };


	this._addExperimentColumns = function(result) {
        for (var i in $scope.experimentTypeList) {
            var p = $scope.experimentTypeList[i];

            var c = {
                data: p.name,
                title: p.name,
                readOnly: false,
                width: 100,
				renderer: that.releaseStatusRenderer
            };

			c.editor = that.DatasetEditor;
            $scope.columns.push(c);
        }
    };

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Constructor
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	$scope.sample = {};
	$scope.samples = [];
	$scope.experimentTypeList = [];
	$scope.samplePropertiesList = [];
	$scope.dataset = {};
	$scope.queryDict = {};

    //Extract GET parameters to a dictionary
    if (location.search !== "") {
        location.search.substr(1).split("&").forEach(function(item) {$scope.queryDict[item.split("=")[0]] = item.split("=")[1];});
    }

	$scope.columns = [
		{ data: 'public_name', title: 'Public Name', readOnly: true, readOnlyCellClassName:"roCell", width: 130 },
        { data: 'private_name', title: 'Private Name', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'donor.private_name', title: 'Donor Name', readOnly: true, readOnlyCellClassName:"roCell" },
        { data: 'EGAN', title: 'Phenotype', readOnly: true, readOnlyCellClassName:"roCell" },
    ];
    $scope.settings = {
        onAfterChange: function(change, source) {that.saveCell(change, source);}
    };

	//Load list of sample metadata fields and add columns
	$http({
		method: 'GET',
		url: '/api/sample_properties'
	}).then(that._addMetaColumns);
    
    
	//Load list of experiments  and add a column for each
	$http({
		method: 'GET',
		url: '/api/experiment_types'
	}).then(function (result) {
		$scope.experimentTypeList = result.data;
		that._addExperimentColumns();
	});

	this.load();
});