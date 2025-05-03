import ChatContainer from '@/components/ChatContainer'
import DataLoader from '@/components/DataLoader'
import MainLayout from '@/layouts/MainLayout'

export default function AIChatPage() {
  function render(data) {
    return <ChatContainer intro={data} />
  }

  return (
    <MainLayout title="AI Chat">
      <DataLoader url="/chat-intro" fn={render} />
    </MainLayout>
  )
}
