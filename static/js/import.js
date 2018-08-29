/*
 * import.js
 */

import Fuse from 'fuse.js'
import Result from 'folktale/result'

import openFile from './utils/open-file'
import readFileAsText from './utils/read-file-as-text'
import { validateAll } from './utils/validate'
import {
  createDonor,
  createSample,
  createDataset,
  createRun,
  fetchDatasetPropertiesNames,
  fetchDonors,
  fetchExperimentTypes,
  fetchSamples,
  fetchSamplePropertiesNames,
  fetchCurrentUser,
} from './requests'

const fuseOptions = {
  shouldSort: true,
  keys: ['name'],
  threshold: 0.5
}

let imports

let currentUser
let experimentNames
let experimentTypes
let experimentTypesFuse
let datasetPropertiesNames
let donors
let donorPrivateNames
let samples
let samplePrivateNames
let samplePropertiesNames

let isLoading = false
const didLoad = loadData()

function loadData() {
  isLoading = true
  const loading = []
  loading.push(fetchCurrentUser().then(res => {
    currentUser = res
  }))
  loading.push(fetchExperimentTypes().then(res => {
    experimentNames = res.map(e => e.ihec_name)
    experimentTypes = res
    experimentTypesFuse = new Fuse(experimentTypes, fuseOptions)
  }))
  loading.push(fetchDatasetPropertiesNames().then(res => {
    datasetPropertiesNames = res
  }))
  loading.push(fetchDonors().then(res => {
    donors = res
    donorPrivateNames = new Set(donors.map(d => d.private_name))
  }))
  loading.push(fetchSamples().then(res => {
    samples = res
    samplePrivateNames = new Set(samples.map(d => d.private_name))
  }))
  loading.push(fetchSamplePropertiesNames().then(res => {
    samplePropertiesNames = res
  }))
  return Promise.all(loading)
  .then(() => {
    isLoading = false
  })
}

$(() => {

  const $file = $('.js-file')
  const $fileName = $('.js-file-name')
  const $fileIcon = $('.js-file-icon')
  const $report = $('.js-report')
  const $import = $('.js-import')
  const $progress = $('.js-progress')
  const $progressBar = $('.js-progress-bar')
  const $result = $('.js-result')

  $file.on('click', onClickFile)
  $import.on('click', onClickImport)

  reset()
  didLoad.then(reset)

  function onClickFile() {
    openFile()
    .then(file => {
      $fileIcon.attr('class', 'fa fa-spin fa-spinner')
      return didLoad.then(() => file)
    })
    .then(file => {
      $fileName.text(file.name)

      readFileAsText(file)
      .then(text => {

        // Generate imports that will be inserted in the database
        const result = parseImports(text)

        result.matchWith({
          Error: ({ value }) => {
            const message = typeof value === 'string' ?
              value :
              `Some errors were found in the current data hub:<br/>${renderErrors(value)}`

            return setReport('danger', 'warning', message)
          },
          Ok: ({ value }) => {
            imports = value

            const newDatasetProperties = Object.values(imports.datasetsByID)
              .map(dataset => Object.keys(dataset.metadata).map(field => ({ field, id: dataset.__id })))
              .reduce(flattenReducer, [])
              .filter(desc => !datasetPropertiesNames.includes(desc.field))
            const newSampleProperties = Object.values(imports.samplesByID)
              .map(sample => Object.keys(sample.metadata).map(field => ({ field, id: sample.__id })))
              .reduce(flattenReducer, [])
              .filter(desc => !samplePropertiesNames.includes(desc.field))

            if (newDatasetProperties.length > 0 || newSampleProperties.length > 0) {
              setReport('warning', 'exclamation-triangle', renderWarningReport(imports, newDatasetProperties, newSampleProperties))
            }
            else {
              setReport('success', 'check', renderSuccessReport(imports))
            }

            $import.removeAttr('disabled')
          }
        })
      })
    })
    .catch(() => {})
    .then(reset)
  }

  function onClickImport() {

    $import.attr('disabled', true)

    $progress.show()
    $progressBar.css({ width: '0%' })
    $progressBar.text('0%')

    doImport(imports, progress => {
      const percent = `${progress.toFixed(2) * 100}%`
      $progressBar.css({ width: percent })
      $progressBar.attr('aria-valuenow', progress * 100)
      $progressBar.text(percent)
    })
    .then(results => {
      $progress.hide()

      if (results.length === 0) {
        // Reload the verification data if ever the user re-imports another hub
        loadData()
        return setResult('success', 'check', 'Data hub succesfuly imported')
      }

      /* eslint-disable no-console */
      const style = 'font-weight: bold; color: #dd1212;'
      console.log('%c========================', style)
      console.log('%cImport failures:', style)
      console.log(results)
      console.log('%c========================', style)
      /* eslint-enable no-console */

      setResult(
        'danger',
        'warning',
        `There were some errors while importing the data hub.
         Open the console for more details.<br/>
         ${renderResults(results)}
        `
      )
    })
  }

  function reset() {
    $report.hide()
    $progress.hide()
    $result.hide()
    $import.attr('disabled', true)

    $file.attr('disabled', isLoading || !currentUser || !currentUser.can_edit)
    $fileIcon.attr('class', isLoading ? 'fa fa-spin fa-spinner' : 'fa fa-folder-open-o')

    if (currentUser && !currentUser.can_edit) {
      setReport('warning', 'exclamation-triangle', 'You don\'t have the permissions to edit data.')
    }
  }

  function setReport(level, icon, message) {
    $report.removeClass('alert-primary alert-success alert-info alert-warning alert-danger')
    $report.addClass(`alert-${level}`)
    $report.html(`<i class="fa fa-${icon}"></i> ${message}`)
    $report.show()
  }

  function setResult(level, icon, message) {
    $result.removeClass('alert-primary alert-success alert-info alert-warning alert-danger')
    $result.addClass(`alert-${level}`)
    $result.html(`<i class="fa fa-${icon}"></i> ${message}`)
    $result.show()
  }
})

function renderErrors(errors) {
  return '<table class="table table-condensed"><tbody>' + errors.map(error =>
    `<tr>
      <th>${error.which.replace(/s$/, '')} ${error.id}</th>
      <td>${error.message}</td>
    </tr>`
  ).join('\n') + '</tbody></table>'
}

function renderResults(results) {
  return '<table class="table table-condensed"><tbody>' + results.map(result =>
    `<tr>
      <th>${result.which} ${result.data.__id}</th>
      <td>${result.message}</td>
    </tr>`
  ).join('\n') + '</tbody></table>'
}

function renderSuccessReport(imports) {
  return (
    `Data hub ready to be imported<br/>
    <table class="table-small"><tbody>
      <tr>
        <th>Donors</th>
        <td>${Object.keys(imports.donorsByID).length}</td>
      </tr>
      <tr>
        <th>Samples</th>
        <td>${Object.keys(imports.samplesByID).length}</td>
      </tr>
      <tr>
        <th>Datasets</th>
        <td>${Object.keys(imports.datasetsByID).length}</td>
      </tr>
      <tr>
        <th>Runs</th>
        <td>${Object.values(imports.datasetsByID).map(d => d.__runs.length).reduce(sumReducer)}</td>
      </tr>
    </tbody></table>
    `
  )
}

function renderWarningReport(imports, newDatasetProperties, newSampleProperties) {
  return renderSuccessReport(imports) + (
    newSampleProperties.length > 0 ?
    `
      <br/>
      <b>Some sample properties will be created:</b>
      <ul>
        ${newSampleProperties.map(desc =>
          `<li>${desc.field} (from sample ${desc.id})</li>`
        )}
      </ul>
    ` : ''
  ) + (
    newDatasetProperties.length > 0 ?
    `
      <br/>
      <b>Some dataset properties will be created:</b>
      <ul>
        ${newDatasetProperties.map(desc =>
          `<li>${desc.field} (from dataset ${desc.id})</li>`
        )}
      </ul>
    ` : ''
  )
}

function parseImports(text) {

  let dataHub = undefined
  try {
    dataHub = JSON.parse(text)
  } catch (err) {
    return Result.Error('Couldnt parse input file as JSON')
  }

  if (!dataHub.datasets || !dataHub.samples || !dataHub.hub_description) {
    return Result.Error('JSON document doesnt seem to be a data hub')
  }

  // Extract groups & tag with ids
  const hubDescription = dataHub.hub_description
  const datasetsByID = tagWithIDs(dataHub.datasets)
  const samplesByID  = tagWithIDs(dataHub.samples)

  // Generate imports that will be inserted in the database
  const imports = {
    datasetsByID: {},
    samplesByID: {},
    donorsByID: {},
  }
  Object.values(datasetsByID).forEach(data => {
    const dataset = extractDataset(data)
    imports.datasetsByID[dataset.__id] = dataset
  })
  Object.values(samplesByID).forEach(data => {
    const { donor, sample } = extractSampleDonor(data, hubDescription)

    imports.samplesByID[sample.__id] = sample
    imports.donorsByID[donor.__id]   = donor
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
        which: 'datasets',
        id: dataset.id,
        message
      })
    }
  })

  // Then, validate that we won't be inserting a duplicate private_name
  Object.values(imports.samplesByID).forEach(sample => {
    if (samplePrivateNames.has(sample.private_name)) {
      errors.push({
        which: 'samples',
        id: sample.__id,
        message: `Sample private name <b>“${sample.private_name}”</b> is already present in the database.`
      })
    }
  })
  Object.values(imports.donorsByID).forEach(donor => {
    if (donorPrivateNames.has(donor.private_name)) {
      errors.push({
        which: 'samples',
        id: donor.__sampleID,
        message: `Donor private name <b>“${donor.private_name}”</b> is already present in the database.`
      })
    }
  })

  if (errors.length > 0) {
    return Result.Error(errors)
  }

  return Result.Ok(imports)
}

function doImport(imports, progressFn) {

  let completed = 0
  let total =
    Object.values(imports).map(o => Object.keys(o).length).reduce(sumReducer)
    + Object.values(imports.datasetsByID).map(d => d.run ? d.run.length : 0).reduce(sumReducer)

  const progress = res => {
    completed++
    progressFn(completed / total)
    return res
  }

  return Promise.all(Object.values(imports.donorsByID).map(donor => {
    return createDonor(donor)
    .then(({ id: donorID }) => {
      donor.id = donorID
      return { ok: true }
    })
    .catch(err => {
      return Promise.resolve({
        ok: false,
        which: 'donor',
        message: err,
        data: donor,
      })
    })
    .then(progress)
  }))
  .then(donorResults => {

    return Promise.all(Object.values(imports.samplesByID).map(sample => {

      const donor = imports.donorsByID[sample.__donorID]
      sample.donor_id = donor.id

      return createSample(sample)
      .then(({ id: sampleID }) => {
        sample.id = sampleID
        return { ok: true }
      })
      .catch(err => {
        return Promise.resolve({
          ok: false,
          which: 'sample',
          message: err,
          data: sample,
        })
      })
      .then(progress)
    }))
    .then(results => donorResults.concat(results))
  })
  .then(otherResults => {

    return Promise.all(Object.values(imports.datasetsByID).map(dataset => {

      const sample = imports.samplesByID[dataset.__sampleID]
      dataset.sample_id = sample.id
      dataset.release_status = 'P'

      return createDataset(dataset)
      .then(({ id: datasetID }) => {
        dataset.id = datasetID
        return { ok: true }
      })
      .catch(err => {
        return Promise.resolve({
          ok: false,
          which: 'dataset',
          message: err,
          data: dataset,
        })
      })
      .then(progress)
    }))
    .then(results => otherResults.concat(results))
    .then(results => {

      const runs =
        Object.values(imports.datasetsByID)
        .map(d => d.__runs.map(r => {
          r.__datasetID = d.__id
          r.dataset_id = d.id
          return r
        }))
        .reduce(flattenReducer, [])

      return Promise.all(runs.map(run =>
        (
          run.dataset_id === undefined ?
            Promise.reject('Undefined dataset id (dataset creation might have failed)') :
            Promise.resolve(run)
        )
        .then(createRun)
        .then(() => ({ ok: true }))
        .catch(err => {
          return Promise.resolve({
            ok: false,
            which: 'dataset (on runs)',
            message: err,
            data: imports.datasetsByID[run.__datasetID],
          })
        })
        .then(progress)
      ))
      .then(runResults => results.concat(runResults))
    })
  })
  .then(results => results.filter(r => !r.ok))
}

function extractSampleDonor(sampleData, hubDescription) {
  const donor  = {
    __id: sampleData.donor_id,
    __sampleID: sampleData.id,
    public_name: null,
    private_name: sampleData.donor_id,
    phenotype: sampleData.donor_health_status,
    taxon_id: hubDescription.taxon_id,
    is_pool: 0,
    metadata: {}
  }
  const sample = {
    __id: sampleData.id,
    __donorID: sampleData.donor_id,
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
    __sampleID: data.sample_id,
    __runs: data.run || [],
    sample_id: null,
    experiment_type: findExperimentType(data.experiment_attributes.experiment_type),
    release_status: '',
    metadata: {
      ...data.experiment_attributes
    },
  }
}

function tagWithIDs(itemsByID) {
  Object.keys(itemsByID).forEach(id => itemsByID[id].id = id)
  return itemsByID
}

function findExperimentType(type) {
  const experimentType = experimentTypes.find(e => e.ihec_name.toLowerCase() === type.toLowerCase())
  return experimentType ? experimentType.ihec_name : type
}

function sumReducer(acc, cur) {
  return acc + cur
}

function flattenReducer(acc, cur) {
  return acc.concat(cur)
}
