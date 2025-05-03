export default function Label({ type, data, children }) {
  const content = data || children
  return <b-label type={type}>{content}</b-label>
}
