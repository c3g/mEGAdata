/*
 * navbar.js
 */


$(function() {

  const url = new URL(location)
  url.hash = ''
  url.search = ''

  $('.navbar-nav li').each((i, el) => {
    const link = el.querySelector('a')

    if (link.href === url.href)
      $(el).addClass('active')
  })
})
