export default function LoadingIndicator({ className, text }) {
  return (
    <b-loader className={className}>
      <div className="loader" />
      <p>{text}...</p>
    </b-loader>
  )
}
