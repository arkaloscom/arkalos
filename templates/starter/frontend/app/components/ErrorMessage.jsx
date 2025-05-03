export default function ErrorMessage({ className, message }) {
  return (
    <div className={className}>
      <p className="error">⚠️ {message && message}</p>
    </div>
  )
}
