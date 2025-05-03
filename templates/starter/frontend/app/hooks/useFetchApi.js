import { useState, useEffect } from 'react'
import Api from '@/services/Api'

function useFetch(method, url, req_data = null) {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  function onBefore() {
    setIsLoading(true)
  }

  function onSuccess(json) {
    setData(json)
    setIsLoading(false)
  }

  function onError(err) {
    setError(err)
    setIsLoading(false)
  }

  useEffect(() => {
    async function run() {
      await Api[method](url, req_data, { onBefore, onSuccess, onError })
    }
    run()
  }, [method, url, req_data])
  return [data, error, isLoading]
}

function useFetchGet(url, data = null) {
  return useFetch('get', url, data)
}

function useFetchPost(url, data = null) {
  return useFetch('post', url, data)
}

export const useFetchApi = {
  get: useFetchGet,
  post: useFetchPost,
}
