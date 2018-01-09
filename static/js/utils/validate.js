/*
 * validate.js
 */

import JSONSchema from 'jsonschema';

import weakMapMemoize from './weak-map-memoize';

import HubDescriptionSchema from '../../schemas/hubDescription.schema.json';
import DatasetSchema from '../../schemas/dataset.schema.json';
import CellLineSchema from '../../schemas/cellLine.schema.json';
import PrimaryCellSchema from '../../schemas/primaryCell.schema.json';
import PrimaryCellCultureSchema from '../../schemas/primaryCellCulture.schema.json';
import PrimaryTissueSchema from '../../schemas/primaryTissue.schema.json';

const { keys, values } = Object


export const VALIDATION_ERROR = {
    HUB_DESCRIPTION:          'HUB_DESCRIPTION'
  , SCHEMA_FAILED:            'SCHEMA_FAILED'
  , UNEXISTENT_SAMPLE:        'UNEXISTENT_SAMPLE'
  , INVALID_BIOMATERIAL_TYPE: 'INVALID_BIOMATERIAL_TYPE'

  /* schema error subtypes */
  , schema: {
      FORMAT: 'schema.FORMAT'
    , TYPE:   'scheam.TYPE'
    , ENUM:   'scheam.ENUM'
  }
}

function validateJSONSchema(data, schema, options) {
  const result = JSONSchema.validate(data, schema, options)
  result.errors = result.errors.map(e => {
    let { property, message, instance } = e

    property = property.replace(/instance\.?/, '')

    if (message.startsWith('is not exactly one from ['))
      message = 'is not exactly one from: ' + e.schema.oneOf.map(schemaToString).join('; ')

    message = [
      property,
      valueToLabel(instance),
      message
    ].join(' ')

    const subtype =
      /does not conform to the ".*" format/.test(e.stack) ?
      VALIDATION_ERROR.schema.FORMAT :
      /is not exactly one from/.test(e.stack) ?
      VALIDATION_ERROR.schema.FORMAT :
      /is not of a type/.test(e.stack) ?
      VALIDATION_ERROR.schema.TYPE :
      /is not one of enum values/.test(e.stack) ?
      VALIDATION_ERROR.schema.ENUM :
      undefined

    return { ...e, property, message, subtype, value: instance }
  })

  return result
}

const validationSchemas = new WeakMap()
function memoizedValidateJSONSchema(data, schema) {
  if (!validationSchemas.has(schema))
    validationSchemas.set(schema, weakMapMemoize(d => validateJSONSchema(d, schema)))

  const fn = validationSchemas.get(schema)

  return fn(data)
}


/**
 * Fails at the first error found
 * (actually not, because of https://github.com/tdegrunt/jsonschema/issues/210)
 */
function fastValidate(data, schema) {
  // oneOf doesnt work with throwError: true, but we would otherwise
  // use it to just catch the first error
  //   const options = { throwError: true }
  //   const result = validateJSONSchema(data, schema, options)

  const result = memoizedValidateJSONSchema(data, schema)

  if (result.errors.length > 0) {
    return { valid: false, message: result.errors[0].message }
  }

  return { valid: true }
}

export function validateDataset(data) {
  return fastValidate(data, DatasetSchema)
}

export function validateSample(data) {
  switch (data.biomaterial_type) {
    case 'Cell Line':            return fastValidate(data, CellLineSchema)
    case 'Primary Cell':         return fastValidate(data, PrimaryCellSchema)
    case 'Primary Cell Culture': return fastValidate(data, PrimaryCellCultureSchema)
    case 'Primary Tissue':       return fastValidate(data, PrimaryTissueSchema)
  }
  return { valid: false, message: 'Property biomaterial_type must be one of: "Cell Line", "Primary Cell", "Primary Cell Culture", or "Primary Tissue"' }
}

export function getSchemaForSample(sample) {
  switch (sample.biomaterial_type) {
    case 'Cell Line':            return CellLineSchema
    case 'Primary Cell':         return PrimaryCellSchema
    case 'Primary Cell Culture': return PrimaryCellCultureSchema
    case 'Primary Tissue':       return PrimaryTissueSchema
  }
  return undefined
}



// Validate the whole dataHub
export function validateAll(datasetsByID, samplesByID, hubDescription) {
  const results = []

  results.push(
    ...memoizedValidateJSONSchema(hubDescription, HubDescriptionSchema)
      .errors
      .map(e => ({
        ...e,
        type: VALIDATION_ERROR.HUB_DESCRIPTION,
        which: 'hubDescription'
      })))

  // Validate datasets
  keys(datasetsByID).forEach(id => {
    const dataset = datasetsByID[id]

    results.push(
      ...memoizedValidateJSONSchema(dataset, DatasetSchema)
        .errors
        .map(e => ({
          ...e,
          type: VALIDATION_ERROR.SCHEMA_FAILED,
          which: 'datasets',
          id: id,
        })))

    keys(dataset.browser || {}).forEach(trackType => {
      if (![
            'signal_unstranded',
            'signal_forward',
            'signal_reverse',
            'peak_calls',
            'methylation_profile',
            'contigs'
          ].includes(trackType)) {
        results.push({
          type: VALIDATION_ERROR.SCHEMA_FAILED,
          which: 'datasets',
          id: id,
          message: `Track type is not in known types: ${trackType}`
        })
      }

      const tracks = dataset.browser[trackType]

      if (tracks && tracks.length > 1 && tracks.filter(t => t.primary).length > 1)
        results.push({
          type: VALIDATION_ERROR.SCHEMA_FAILED,
          which: 'datasets',
          id: id,
          message: `Track type “${trackType}” has more than 1 primary track`
        })
    })

    // Validate that all used sample ids exist
    const samplesID = Array.isArray(dataset.sample_id) ? dataset.sample_id : [dataset.sample_id]
    samplesID.forEach(sampleID => {
      if (samplesByID[sampleID] === undefined)
        results.push({
          type: VALIDATION_ERROR.UNEXISTENT_SAMPLE,
          which: 'datasets',
          id: id,
          message: `Sample “${sampleID}” does not exists`,
          data: sampleID
        })
    })
  })

  // Validate samples
  keys(samplesByID).forEach(id => {
    const sample = samplesByID[id]
    const schema = getSchemaForSample(sample)

    if (schema)
      results.push(
        ...memoizedValidateJSONSchema(sample, schema)
          .errors
          .map(e => ({
            ...e,
            type: VALIDATION_ERROR.SCHEMA_FAILED,
            which: 'samples',
            id: id,
          })))
    else
      results.push({
        type: VALIDATION_ERROR.INVALID_BIOMATERIAL_TYPE,
        which: 'samples',
        id: id,
        message: `Invalid biomaterial type “${sample.biomaterial_type}”`
      })
  })

  return results
}

function valueToLabel(value) {
  const type = typeof value
  if (type === 'string' || type == 'number')
    return `(“${value}”)`
  if (type === null)
    return `(null)`
  if (type === undefined)
    return `(undefined)`
  return ''
}

function schemaToString(schema) {
  switch (schema.type) {
    case 'number': {
      return (
          (schema.exclusiveMinimum ? ']' : '[')
        + (schema.minimum != undefined ? schema.minimum : '')
        + ('-')
        + (schema.maximum != undefined ? schema.maximum : '')
        + (schema.exclusiveMaximum ? '[' : ']')
      )
    }
    case 'string': {
      if (schema.enum)
        return '(' + schema.enum.join(', ') + ')'
      if (schema.pattern)
        return `/${schema.pattern}/`
    }
  }
  return JSON.stringify(schema)
}
