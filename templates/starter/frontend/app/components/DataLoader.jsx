import { useFetchApi } from '@/hooks/useFetchApi'
import LoadingIndicator from '@/components/LoadingIndicator'
import ErrorMessage from '@/components/ErrorMessage'

export default function DataLoader({ url, data, fn }) {
  const [d, err, isLoading] = useFetchApi.get(url, data)

  function renderLoader() {
    return <LoadingIndicator text="Loading" />
  }

  function renderError(error) {
    let msg = error.name + ': ' + error.message
    if (error.name === 'TimeoutError') {
      msg = 'TimeoutError: Request timed out. Is backend running?'
    }
    return <ErrorMessage message={msg} />
  }

  function render() {
    if (isLoading) return renderLoader()
    if (err) return renderError(err)
    if (d) return fn(d)
  }

  return render()
}
