/*
 * weak-map-memoize.js
 */

export default function weakMapMemoize(fn) {
  const wm = new WeakMap()
  return (arg) => {
    if (wm.has(arg))
      return wm.get(arg)
    const result = fn(arg)
    wm.set(arg, result)
    return result
  }
}
