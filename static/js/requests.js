/*
 * requests.js
 */


export function fetchUsers() {
  return get('/user/list')
}
export function createUser(email) {
  return post('/user/create', { email })
}
export function updateUser(user) {
  return post('/user/update', user)
}
export function deleteUser(id) {
  return post('/user/delete', { id })
}

export function fetchExperimentTypes() {
  return get('/experiment_types')
}

export function fetchDonors() {
  return get('/donors')
}
export function createDonor(donor) {
  return post('/donor', donor)
}

export function fetchSamples() {
  return get('/samples')
}
export function createSample(sample) {
  return post('/sample', sample)
}

export function createDataset(dataset) {
  return post('/dataset', dataset)
}


function fetchAPI(method, route, data) {
  return axios[method]('/api' + route, data)
    .then(result => {
      const apiResult = result.data

      if (apiResult.ok)
        return Promise.resolve(apiResult.data)
      else
        return Promise.reject(new Error(apiResult.message))
    })
}
function get(route, data)  { return fetchAPI('get',  route, data) }
function post(route, data) { return fetchAPI('post', route, data) }
