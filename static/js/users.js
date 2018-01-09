/*
 * users.js
 */
/* global $, axios */

import {
  fetchUserList,
  createUser,
  updateUser,
  deleteUser
} from './requests'

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
