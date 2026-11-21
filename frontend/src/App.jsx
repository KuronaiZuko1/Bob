import React, { useState, useCallback } from 'react'
import { HashRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'

// Pages (lazy for performance)
import Overview      from './pages/Overview'
import Profile       from './pages/Profile'
import Discovery     from './pages/Discovery'
import Applications  from './pages/Applications'
import Documents     from './pages/Documents'
import AIConfig      from './pages/AIConfig'
import EmailSettings from './pages/EmailSettings'
import TelegramSettings from './pages/TelegramSettings'
import Settings      from './pages/Settings'

/* ── Toast context (simple) ── */
export const ToastContext = React.createContext(null)

function ToastContainer({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.type}`}>
          <strong>{t.type === 'success' ? '✓' : t.type === 'error' ? '✗' : '!'}</strong>{' '}
          {t.message}
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000)
  }, [])

  return (
    <ToastContext.Provider value={addToast}>
      <Router>
        <div className="app-shell">
          <Sidebar />
          <div className="main-content">
            <Routes>
              <Route path="/"          element={<Overview />} />
              <Route path="/profile"   element={<Profile />} />
              <Route path="/discovery" element={<Discovery />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/ai"        element={<AIConfig />} />
              <Route path="/email"     element={<EmailSettings />} />
              <Route path="/telegram"  element={<TelegramSettings />} />
              <Route path="/settings"  element={<Settings />} />
            </Routes>
          </div>
        </div>
        <ToastContainer toasts={toasts} />
      </Router>
    </ToastContext.Provider>
  )
}
