import ChatContainer from '@/components/ChatContainer'
import Label from '@/components/Label'
import DataLoader from '@/components/DataLoader'
import Pagination from '@/components/Pagination'
import Table from '@/components/Table'
import MainLayout from '@/layouts/MainLayout'
import Api from '@/services/Api'
import DateX from '@/utils/date'
import { useSearchParams } from 'react-router'

export default function LogsPage() {
  const DEFAULT_TYPE = 'error'
  const DEFAULT_MONTH = DateX.getMonthValue()
  const [searchParams, setSearchParams] = useSearchParams({
    type: DEFAULT_TYPE,
    month: DEFAULT_MONTH,
    page: 1,
  })

  function onTypeChange(e) {
    const key = 'type'
    const val = e.target.value
    setSearchParams(curParams => {
      const newParams = new URLSearchParams(curParams)
      newParams.set(key, val)
      newParams.set('page', 1)
      newParams.set('month', DEFAULT_MONTH)
      return newParams
    })
  }

  function onMonthChange(e) {
    const key = 'month'
    const val = e.target.value
    setSearchParams(curParams => {
      const newParams = new URLSearchParams(curParams)
      newParams.set(key, val)
      return newParams
    })
  }

  function renderMonthOptions() {
    const options = []
    const now = new Date()

    for (let i = 0; i < 12; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const label = DateX.getMonthLabel(date)
      const value = DateX.getMonthValue(date)

      options.push(
        <option key={value} value={value}>
          {label}
        </option>,
      )
    }

    return options
  }

  function render(data) {
    return (
      <b-datatable>
        <LogTable data={data.data} />
        <Pagination total_pages={data.page_count} />
      </b-datatable>
    )
  }

  return (
    <MainLayout title="Logs">
      <h1>Latest Logs</h1>
      <b-grid style={{ marginBottom: '2rem' }}>
        <select name="type" onChange={onTypeChange} value={searchParams.get('type')}>
          <option value="error">Error</option>
          <option value="info">Info</option>
        </select>
        <select name="month" onChange={onMonthChange} value={searchParams.get('month')}>
          {renderMonthOptions()}
        </select>
      </b-grid>

      <DataLoader url="/logs" data={searchParams} fn={render} />
    </MainLayout>
  )
}

function LogTable({ data = [] }) {
  const columns = {
    time: { title: 'Date', fn: renderTimestampCell, style: { width: '9rem' } },
    src: { title: 'Source' },
    lvl: { title: 'Level', fn: renderLevelCell },
    msg: { title: 'Message', fn: renderMessage },
  }
  function getLevelColorType(level) {
    switch (level?.toUpperCase()) {
      case 'ERROR':
        return 'danger'
      case 'WARNING':
        return 'warning'
      case 'INFO':
        return 'success'
      case 'ACCESS':
        return 'success'
      case 'DEBUG':
        return 'info'
      default:
        return null
    }
  }

  function renderMessage(msg, row) {
    let res = msg
    if (row['data']) {
      res = res + ' - ' + JSON.stringify(row['data'])
    }
    if (row['exc']) {
      res = res + row['exc_stck']
    }
    return res
  }

  function renderLevelCell(level) {
    const type = getLevelColorType(level)
    return <Label type={type}>{level}</Label>
  }

  function renderTimestampCell(timestamp) {
    return DateX.timeAgo(timestamp)
  }

  return <Table data={data} columns={columns} />
}
