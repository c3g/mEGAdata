/*
 * transform-api-response.js
 */

export default [
  res => JSON.parse(res),
  res => {
    if (!res.ok)
      return Promise.reject(new Error(res.message))
    return res.data
  }
]
