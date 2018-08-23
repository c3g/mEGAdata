/*
 * hot-renderers.js
 * Handsontable renderers
 */
/* global Handsontable*/

export function dataset(instance, td, row, col, prop, data, cellProperties) {

  const releaseStatus = data === null ? '' : (data.release_status || '')
  const runs = data === null ? [] : data.runs

  Handsontable.renderers.TextRenderer.apply(this, [
    instance,
    td,
    row,
    col,
    prop,
    /* value = */ releaseStatus,
    cellProperties
  ]);

  td.className = 'cell--dataset';

  if (releaseStatus.charAt(0) === 'R') {
    cellProperties.readOnly = true;
  }
  else if (releaseStatus.charAt(0) === 'P') {
    td.className = 'cell--dataset-pending';
    cellProperties.readOnly = true;
  }
  else {
    cellProperties.readOnly = false;
  }

  if (runs.length > 0) {
    td.className += ' cell--has-run'
  }
}

export function HTML(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.HtmlRenderer.apply(this, arguments);
  td.className = 'cell--metadata';
}

export function URI(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.HtmlRenderer.apply(this, arguments);
  td.className = 'cell--metadata';
  if (value !== null) {
    td.innerHTML = '<a target=\'_blank\' href=\'' + value + '\'>' + value + '</a>';
  }
}

export function donor(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.HtmlRenderer.apply(this, arguments);
  if (value !== null) {
    td.innerHTML = '<a href=\'/donors?donor=' + value + '\'>' + value + '</a>';
  }
}
