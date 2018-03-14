/*
 * promise-progress.js
 */

export default function promiseProgress(promises, callback) {
  let d = 0
  callback(0)
  promises.forEach(p => {
    p.then(()=> {
      d++
      callback((d * 100) / promises.length)
    })
  })
  return Promise.all(promises)
}
