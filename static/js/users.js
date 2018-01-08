/*
 * users.js
 */
/* global $, axios */


$(function() {

  const $users = $('.js-users')

  const $create = $('.js-user-create')
  const $email = $('.js-user-email')

  $create.click(() => {
    const email = $email.val()

    if (!email)
      return

    $email.val('')

    createUser(email)
    .then(updateUsers)
  })

  updateUsers()

  function updateUsers() {
    return fetchUserList().then(renderUsers)
  }

  function renderUsers(users) {
    $users.empty()
    users.forEach(user => {
      const $user = $('<tr>')
      const $id = $('<td>', { text: user.id })
      const $name = $('<td>', { text: user.name || '' })
      const $email = $('<td>', { text: user.email })
      const $delete = $('<button>', { class: 'btn btn-xs btn-danger' })
          .append($('<i>', { class: 'fa fa-trash' }))

      $delete.click(() => {
        deleteUser(user.id)
        .then(updateUsers)
      })

      $user.append($id)
      $user.append($name)
      $user.append($email)
      $user.append($('<td>').append($delete))

      $users.append($user)
    })
  }
})

function fetchUserList() {
  return get('/user/list')
}
function createUser(email) {
  return post('/user/create', { email })
}
function updateUser(user) {
  return post('/user/update', user)
}
function deleteUser(id) {
  return post('/user/delete', { id })
}


function fetchAPI(method, route, data) {
  return axios[method]('/api' + route, data)
    .then(result => result.data)
}
function get(route, data)  { return fetchAPI('get',  route, data) }
function post(route, data) { return fetchAPI('post', route, data) }
