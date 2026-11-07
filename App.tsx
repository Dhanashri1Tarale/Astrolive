import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuthStore } from './store/useAuthStore'

import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import AstrologerDiscovery from './pages/AstrologerDiscovery'
import ConsultationPage from './pages/ConsultationPage'
import ConsultationSummary from './pages/ConsultationSummary'
import MyAstroJourney from './pages/MyAstroJourney'
import Goals from './pages/Goals'
import ShareCardPage from './pages/ShareCardPage'
import AnalyticsPage from './pages/AnalyticsPage'

export default function App() {
  const hydrate = useAuthStore((s) => s.hydrate)

  useEffect(() => {
    hydrate()
  }, [hydrate])

  return (
    <div className="min-h-screen">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/astrologers" element={<ProtectedRoute><AstrologerDiscovery /></ProtectedRoute>} />
        <Route path="/consult/:astrologerId" element={<ProtectedRoute><ConsultationPage /></ProtectedRoute>} />
        <Route path="/consultations/:id" element={<ProtectedRoute><ConsultationSummary /></ProtectedRoute>} />
        <Route path="/journey" element={<ProtectedRoute><MyAstroJourney /></ProtectedRoute>} />
        <Route path="/goals" element={<ProtectedRoute><Goals /></ProtectedRoute>} />
        <Route path="/share" element={<ProtectedRoute><ShareCardPage /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      </Routes>
    </div>
  )
}
