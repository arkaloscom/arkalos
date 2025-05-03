import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router'

import '@/css/_app.css'

import { ErrorBoundary } from './components/ErrorBoundary'
import _404NotFoundPage from '@/pages/error/_404NotFoundPage.jsx'

import IndexPage from '@/pages/IndexPage.jsx'
import DashboardPage from '@/pages/DashboardPage.jsx'
import AIChatPage from '@/pages/AIChatPage.jsx'
import LogsPage from '@/pages/LogsPage'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<_404NotFoundPage />} />
          <Route path="/" element={<IndexPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat" element={<AIChatPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
