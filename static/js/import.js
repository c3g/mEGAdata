/*
 * import.js
 */
/* global $, axios */

import openFile from './utils/open-file'
import readFileAsText from './utils/read-file-as-text'
import { validateAll } from './utils/validate'

let dataHub = undefined
let datasetsByID
let samplesByID

$(() => {

  const $file = $('.js-file')
  const $fileName = $('.js-file-name')
  const $report = $('.js-report')
  const $import = $('.js-import')

  $report.hide()
  $import.attr('disabled', true)

  $file.on('click', (ev) => {
    openFile()
    .then(file => {
      $report.hide()
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

        datasetsByID = dataHub.datasets
        samplesByID = dataHub.samples
        Object.keys(datasetsByID).forEach(id => datasetsByID[id].id = id)
        Object.keys(samplesByID).forEach(id => samplesByID[id].id = id)

        const results = validateAll(datasetsByID, samplesByID, dataHub.hub_description)

        if (results.length > 0) {
          return setReport(
            'danger',
            'warning',
            `Some errors were found in the current data hub:<br/>${renderResults(results)}`
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

  })


  function setReport(level, icon, message) {
    $report.removeClass(`alert-primary alert-success alert-info alert-warning alert-danger`)
    $report.addClass(`alert-${level}`)
    $report.html(`<i class="fa fa-${icon}"></i> ${message}`)
    $report.show()
  }
})

function renderResults(results) {
  return `<table class="table table-condensed"><tbody>` + results.map(result =>
    `<tr>
      <th>${result.which.replace(/s$/, '')} ${result.id}</th>
      <td>${result.message}</td>
    </tr>`
  ).join('\n') + `</tbody></table>`
}
