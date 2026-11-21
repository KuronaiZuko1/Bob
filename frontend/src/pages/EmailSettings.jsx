import React, { useContext, useState } from 'react'
import { ToastContext } from '../App'
import client from '../api/client'

export default function EmailSettings() {
  const addToast = useContext(ToastContext)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  async function startOAuth() {
    setLoading(true)
    try {
      const res = await client.post('/api/settings/gmail/auth-url')
      const authUrl = res.data?.auth_url
      if (authUrl) {
        // Open in system browser via Electron IPC, or in browser
        if (window.electronAPI?.openExternal) {
          window.electronAPI.openExternal(authUrl)
        } else {
          window.open(authUrl, '_blank')
        }
        setStatus({ msg: 'Google OAuth page opened. Complete sign-in in your browser, then click "Check Status".', ok: true })
      }
    } catch (e) {
      setStatus({ msg: `Error: ${e.message}`, ok: false })
    } finally { setLoading(false) }
  }

  async function checkStatus() {
    setLoading(true)
    try {
      const res = await client.get('/api/settings/gmail/status')
      if (res.data?.connected) {
        setStatus({ msg: `✓ Connected as ${res.data.email}`, ok: true })
        addToast('Gmail connected successfully', 'success')
      } else {
        setStatus({ msg: 'Not connected yet. Complete the OAuth flow in your browser.', ok: false })
      }
    } catch (e) {
      setStatus({ msg: e.message, ok: false })
    } finally { setLoading(false) }
  }

  async function disconnect() {
    if (!window.confirm('Disconnect Gmail? BOB will not be able to send email applications.')) return
    try {
      await client.delete('/api/settings/gmail/disconnect')
      addToast('Gmail disconnected', 'success')
      setStatus(null)
    } catch (e) {
      addToast(e.message, 'error')
    }
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Email Settings (Gmail)</div>
          <div className="section-subtitle">Connect Gmail via official Google OAuth 2.0. BOB never stores your password.</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Gmail OAuth 2.0</div>

        <div style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
          BOB uses Gmail's official API to send job applications. Authentication uses Google OAuth 2.0 — you sign in directly with Google. BOB never sees your password.
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 'var(--space-4)' }}>
          {[
            'BOB never stores your Gmail password',
            'Only sends emails — does not read your inbox',
            'You can revoke access at any time via Google Account settings',
            'Credentials stored locally in your .env file',
          ].map(rule => (
            <div key={rule} style={{ display: 'flex', gap: 10, alignItems: 'center', fontSize: 'var(--font-size-sm)' }}>
              <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
              <span style={{ color: 'var(--text-secondary)' }}>{rule}</span>
            </div>
          ))}
        </div>

        {status && (
          <div style={{ marginBottom: 'var(--space-4)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', background: status.ok ? 'var(--success-subtle)' : 'var(--warning-subtle)', color: status.ok ? 'var(--success)' : 'var(--warning)', fontSize: 'var(--font-size-sm)' }}>
            {status.msg}
          </div>
        )}

        <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={startOAuth} disabled={loading}>Connect Gmail Account</button>
          <button className="btn btn-secondary" onClick={checkStatus} disabled={loading}>Check Status</button>
          <button className="btn btn-secondary" onClick={disconnect} style={{ color: 'var(--danger)' }}>Disconnect</button>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Email Application Settings</div>
        <div className="form-group">
          <label className="form-label">Default CC Address (optional)</label>
          <input className="form-input" placeholder="yourcc@example.com" style={{ maxWidth: 360 }} />
          <div className="form-hint">Optionally CC yourself on every application email.</div>
        </div>
        <div className="form-group">
          <label className="form-label">Test Mode</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <input type="checkbox" id="test-mode" defaultChecked />
            <label htmlFor="test-mode" style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>
              Send to your own email address instead of real employers (recommended during setup)
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
