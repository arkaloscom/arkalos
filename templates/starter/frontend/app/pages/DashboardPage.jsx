import MainLayout from '@/layouts/MainLayout'
import Chart from '@/components/Chart'
import DataLoader from '@/components/DataLoader'

export default function DashboardPage() {
  function render(data) {
    return <Chart spec={data} />
  }

  return (
    <MainLayout title="Dashboard">
      <h1>Dashboard</h1>
      <b-grid>
        <b-card>
          <h2>Bar Chart</h2>
          <DataLoader url="/dashboard-chart?type=bar" fn={render} />
        </b-card>
        <b-card>
          <h2>Pie Chart</h2>
          <DataLoader url="/dashboard-chart?type=pie" fn={render} />
        </b-card>
        <b-card>
          <h2>Line Chart</h2>
          <DataLoader url="/dashboard-chart?type=line" fn={render} />
        </b-card>
        <b-card>
          <h2>Scatter Plot</h2>
          <DataLoader url="/dashboard-chart?type=scatter" fn={render} />
        </b-card>
        <b-card>
          <h2>Area Chart</h2>
          <DataLoader url="/dashboard-chart?type=area" fn={render} />
        </b-card>
        <b-card>
          <h2>Metric</h2>
          <b-metric>50%</b-metric>
        </b-card>
      </b-grid>
    </MainLayout>
  )
}
