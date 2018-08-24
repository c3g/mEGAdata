/*
 * users.js
 */
/* global $, axios */

import {
  fetchUsers,
  createUser,
  updateUser,
  deleteUser
} from './requests'

let state = {
  users: [],
}

$(function() {

  const $users = $('.js-users')
  const $create = $('.js-user-create')
  const $email = $('.js-user-email')
  const alert = new Alert('.js-alert')

  $create.click(onCreateUser)

  loadUsers()

  function setState(patch) {
    state = { ...state, ...patch }
    render(state)
  }

  function loadUsers() {
    return fetchUsers()
      .then(users => {
        setState({ users })
      })
      .catch(onError)
  }

  function onCreateUser() {
    const email = $email.val()

    if (!email)
      return

    $email.val('')

    createUser(email)
    .then(loadUsers)
  }

  function onError(err) {
    alert.show('Snap! An error occured:', err.message)
  }

  function render(state) {
    $users.empty()

    state.users.forEach(user => {
      const $user = $('<tr>')
      const $id = $('<td>', { text: user.id })
      const $name = $('<td>', { text: user.name || '' })
      const $email = $('<td>', { text: user.email })
      const $canEdit = $('<button>', { class: 'btn btn-xs' })
          .append($('<i>', { class: 'fa fa-' + (user.can_edit ? 'check-' : '') + 'square-o' }))
      const $delete = $('<button>', { class: 'btn btn-xs btn-danger' })
          .append($('<i>', { class: 'fa fa-trash' }))

      $delete.click(() => {
        deleteUser(user.id)
        .then(loadUsers)
        .catch(onError)
      })

      $canEdit.click(() => {
        updateUser({ ...user, can_edit: !user.can_edit })
        .then(newUser => {
          setState({ users: state.users.map(u => u.id === newUser.id ? newUser : u) })
        })
        .catch(onError)
      })

      $user.append($id)
      $user.append($name)
      $user.append($email)
      $user.append($('<td>').append($canEdit))
      $user.append($('<td>').append($delete))

      $users.append($user)
    })
  }
})

class Alert {
  constructor(selector) {
    this.$element = $(selector)
    this.$element.hide()
    this.$element.addClass('fade out')
    setTimeout(() => this.$element.show(), 500)
    this.$close = this.$element.find('.close')
    this.$close.click(() => {
      this.hide()
    })
  }
  show(title, message) {
    this.$element.find('.alert-title').text(title)
    this.$element.find('.alert-message').text(message)
    this.$element.removeClass('fade out')
    this.$element.addClass('fade in')
  }
  hide() {
    this.$element.removeClass('fade in')
    this.$element.addClass('fade out')
  }
}
