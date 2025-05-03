async function request(url, method = 'GET', data = null, callbacks = {}) {
  try {
    let query = ''
    if (callbacks.onBefore) callbacks.onBefore(url, data)
    if (method.toLowerCase() === 'get' && data) {
      query = '?' + new URLSearchParams(data).toString()
    }
    const opts = {
      method: method,
      signal: AbortSignal.timeout(30000),
    }
    if (method.toLowerCase() === 'post' && data) {
      opts.body = data
    }

    const res = await fetch('/api' + url + query, opts)

    const json = await res.json()

    if (json.error) {
      throw new Error(json.error)
    }
    if (json.detail && json.detail[0] && json.detail[0].msg) {
      throw new Error(json.detail[0].msg)
    }
    if (json.detail) {
      throw new Error(json.detail)
    }
    if (callbacks.onSuccess) callbacks.onSuccess(json)
    return [json, false]
  } catch (err) {
    if (callbacks.onError) callbacks.onError(err)
    return [false, err]
  }
}

async function get(url, data = null, callbacks = {}) {
  return await request(url, 'GET', data, callbacks)
}

async function post(url, data, callbacks = {}) {
  return await request(url, 'POST', data, callbacks)
}

const Api = {
  get,
  post,
}

export default Api
