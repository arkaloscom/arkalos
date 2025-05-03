import ErrorMessage from '@/components/ErrorMessage'
import MainLayout from '@/layouts/MainLayout'

export default function ErrorPage({ message }) {
  return (
    <main className="index">
      <h1>Something Went Wrong</h1>
      <h2 className="error">{message}</h2>
    </main>
  )
}
