const DateX = {
  timeAgo,
  getMonthLabel,
  getMonthValue,
}

export default DateX

function timeAgo(timestamp) {
  if (!timestamp) return 'Unknown'

  try {
    const date = new Date(timestamp.replace(',', '.'))
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)

    if (isNaN(diffInSeconds)) return timestamp

    if (diffInSeconds < 5) return 'just now'
    if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`

    const diffInMinutes = Math.floor(diffInSeconds / 60)
    if (diffInMinutes < 60) return diffInMinutes === 1 ? '1 minute ago' : `${diffInMinutes} minutes ago`

    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`

    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return diffInDays === 1 ? 'yesterday' : `${diffInDays} days ago`

    // For older dates, show the actual date
    return date.toLocaleDateString()
  } catch (error) {
    return timestamp
  }
}

function getMonthLabel(date = null) {
  // e.g. "May 2025"
  if (!date) date = new Date()
  const label = date.toLocaleString('default', { month: 'long', year: 'numeric' })
  return label
}

function getMonthValue(date = null) {
  // e.g. "2025-05"
  if (!date) date = new Date()
  const value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
  return value
}
