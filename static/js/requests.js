/*
 * requests.js
 */


export function fetchUserList() {
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


export function createDonor(donor) {
  return post('/donor', donor)
}

export function createSample(sample) {
  return post('/sample', sample)
}


function fetchAPI(method, route, data) {
  return axios[method]('/api' + route, data)
    .then(result => result.data)
}
function get(route, data)  { return fetchAPI('get',  route, data) }
function post(route, data) { return fetchAPI('post', route, data) }
