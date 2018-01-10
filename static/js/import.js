/*
 * import.js
 */
/* global $, axios */

import Fuse from 'fuse.js'
import openFile from './utils/open-file'
import readFileAsText from './utils/read-file-as-text'
import promiseProgress from './utils/promise-progress'
import { validateAll } from './utils/validate'
import {
  createDonor,
  createSample,
  createDataset,
  fetchExperimentTypes,
} from './requests'

let dataHub
let hubDescription
let datasetsByID
let samplesByID
let objects = []

const fuseOptions = {
  shouldSort: true,
  keys: ['name'],
  threshold: 0.5
}

let experimentNames
let experimentTypes
let experimentTypesFuse
fetchExperimentTypes()
.then(res => {
  experimentNames = res.map(e => e.name)
  experimentTypes = res
  experimentTypesFuse = new Fuse(experimentTypes, fuseOptions)
})


$(() => {

  const $file = $('.js-file')
  const $fileName = $('.js-file-name')
  const $report = $('.js-report')
  const $import = $('.js-import')
  const $progress = $('.js-progress')
  const $result = $('.js-result')

  $report.hide()
  $progress.hide()
  $result.hide()
  $import.attr('disabled', true)

  $file.on('click', (ev) => {
    openFile()
    .then(file => {
      $report.hide()
      $progress.hide()
      $import.attr('disabled', true)
      $fileName.text(file.name)

      readFileAsText(file)
      .then(text => {

        dataHub = undefined
        try {
          dataHub = JSON.parse(text)
        } catch (err) {
          return setReport('danger', 'warning', 'Couldnt parse input file as JSON')
        }

        if (!dataHub.datasets || !dataHub.samples || !dataHub.hub_description) {
          return setReport('danger', 'warning', 'JSON document doesnt seem to be a data hub')
        }

        // Extract groups & tag with ids
        hubDescription = dataHub.hub_description
        datasetsByID = dataHub.datasets
        samplesByID = dataHub.samples
        Object.keys(datasetsByID).forEach(id => datasetsByID[id].id = id)
        Object.keys(samplesByID).forEach(id => samplesByID[id].id = id)

        // Generate objects that will be inserted in the database
        objects = Object.values(datasetsByID).map(data => {
          const { donor, sample } = extractSampleDonor(samplesByID[data.sample_id])
          const dataset = extractDataset(data)
          return { dataset, donor, sample }
        })

        // Validate schema first
        const errors = validateAll(datasetsByID, samplesByID, dataHub.hub_description)

        // Then, validate that the corresponding entities in the database are present
        Object.values(datasetsByID).forEach(dataset => {

          const type = findExperimentType(dataset.experiment_attributes.experiment_type)

          // If we dont have a matching experiment, generate an error
          if (!experimentNames.includes(type)) {

            const alternatives = experimentTypesFuse.search(type)

            let message = `Experiment type <b>“${type}”</b> is not present in the database. `

            if (alternatives.length > 0) {
              if (alternatives.length === 1) {
                message += `<div class="suggestion">Try “${alternatives[0].name}”?</div>`
              } else {
                message += `<div class="suggestion">Try one of these?
                  <ul>
                    ${alternatives.slice(0, 5).map(a => `<li>“${a.name}”</li>`).join('\n')}
                  </ul>
                </div>`
              }
            }

            errors.push({
              type: undefined,
              which: 'datasets',
              id: dataset.id,
              message
            })
          }
        })

        if (errors.length > 0) {
          return setReport(
            'danger',
            'warning',
            `Some errors were found in the current data hub:<br/>${renderErrors(errors)}`
          )
        }

        setReport('success', 'check',
          `Data hub ready to be imported<br/>
          <table class="table-small"><tbody>
            <tr>
              <th>Datasets</th>
              <td>${Object.keys(datasetsByID).length}</td>
            </tr>
            <tr>
              <th>Samples</th>
              <td>${Object.keys(samplesByID).length}</td>
            </tr>
          </tbody></table>
          `
        )
        $import.removeAttr('disabled')
      })
    })
  })

  $import.on('click', () => {

    $import.attr('disabled', true)

    $progress.show()
    $progress.css({ width: '0%' })
    $progress.text('0%')

    doImport(progress => {
      const percent = `${progress * 100}%`
      $progress.css({ width: percent })
      $progress.text(percent)
    })
    .then(results => {
      console.log(results)

      $progress.hide()

      if (results.every(r => r.ok)) {
        return setResult('success', 'check', 'Data hub succesfuly imported')
      }

      setResult(
        'danger',
        'warning',
        `There were some errors while importing the data hub:<br/>${renderResults(results)}`
      )
    })
  })


  function setReport(level, icon, message) {
    $report.removeClass(`alert-primary alert-success alert-info alert-warning alert-danger`)
    $report.addClass(`alert-${level}`)
    $report.html(`<i class="fa fa-${icon}"></i> ${message}`)
    $report.show()
  }

  function setResult(level, icon, message) {
    $result.removeClass(`alert-primary alert-success alert-info alert-warning alert-danger`)
    $result.addClass(`alert-${level}`)
    $result.html(`<i class="fa fa-${icon}"></i> ${message}`)
    $result.show()
  }
})

function renderErrors(errors) {
  return `<table class="table table-condensed"><tbody>` + errors.map(error =>
    `<tr>
      <th>${error.which.replace(/s$/, '')} ${error.id}</th>
      <td>${error.message}</td>
    </tr>`
  ).join('\n') + `</tbody></table>`
}

function renderResults(results) {
  return `<table class="table table-condensed"><tbody>` + results.filter(r => !r.ok).map(result =>
    `<tr>
      <th>Dataset ${result.id}</th>
      <td>${result.message}</td>
    </tr>`
  ).join('\n') + `</tbody></table>`
}

function doImport(progressFn) {
  return promiseProgress(objects.map(({ donor, sample, dataset }) => {
    const id = dataset.__id

    return createDonor(donor)
    .then(donor => {
      console.log(donor)

      sample.donor_id = donor.id

      return createSample(sample)
      .then(sample => {
        console.log(sample)

        dataset.sample_id = sample.id

        return createDataset(dataset)
        .then(dataset => {
          console.log(dataset)

          return Promise.resolve({
            ok: true,
            id: id,
            donor,
            sample,
            dataset
          })
        })
      })
    })
    .catch(err => {
      console.log(err)
      return Promise.resolve({
        ok: false,
        id: id,
        message: err,
        donor,
        sample,
        dataset
      })
    })
  }), progressFn)
}

function extractSampleDonor(sampleData) {
  const donor  = {
    public_name: null,
    private_name: sampleData.donor_id,
    phenotype: sampleData.donor_health_status,
    taxon_id: hubDescription.taxon_id,
    is_pool: 0,
    metadata: {}
  }
  const sample = {
    __id: sampleData.id,
    public_name: null,
    private_name: sampleData.id,
    metadata: {}
  }
  Object.keys(sampleData).forEach(key => {
    if (key === 'id')
      return;
    if (/^donor_/i.test(key))
      donor.metadata[key.replace(/^donor_/i, '').toLowerCase()] = sampleData[key]
    else
      sample.metadata[key.toLowerCase()] = sampleData[key]
  })
  return { donor, sample }
}

function extractDataset(data) {
  return {
    __id: data.id,
    sample_id: null,
    experiment_type: findExperimentType(data.experiment_attributes.experiment_type),
    release_status: '',
    metadata: {
      ...data.experiment_attributes
    }
  }
}

function findExperimentType(type) {
  return experimentNames.find(name => name.toLowerCase() === type.toLowerCase()) || type
}
