import React, { useContext, useState } from 'react'
import { ToastContext } from '../App'
import client from '../api/client'

export default function TelegramSettings() {
  const addToast = useContext(ToastContext)
  const [status, setStatus]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [token, setToken]     = useState('')
  const [userId, setUserId]   = useState('')

  async function saveAndTest() {
    if (!token.trim()) { addToast('Enter a bot token first', 'warning'); return }
    setLoading(true)
    try {
      await client.put('/api/settings', { telegram: { bot_token: token, allowed_user_id: userId } })
      const res = await client.post('/api/settings/test-telegram')
      if (res.data?.ok) {
        setStatus({ msg: `✓ Telegram connected. Bot: @${res.data.bot_username}`, ok: true })
        addToast('Telegram connected!', 'success')
      } else {
        setStatus({ msg: `Bot responded but reported an error: ${res.data?.description}`, ok: false })
      }
    } catch (e) {
      setStatus({ msg: e.message, ok: false })
    } finally { setLoading(false) }
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Telegram Notifications</div>
          <div className="section-subtitle">BOB notifies you via Telegram and accepts commands from your Telegram account</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Bot Configuration</div>
        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
          Create a Telegram bot via <strong>@BotFather</strong>, then paste the token below. BOB uses your Telegram User ID to restrict access to your account only.
        </div>

        <div className="form-group">
          <label className="form-label">Bot Token</label>
          <input className="form-input" type="password" value={token} onChange={e => setToken(e.target.value)} placeholder="123456:ABC-DEF…" style={{ maxWidth: 400 }} />
          <div className="form-hint">Get this from @BotFather on Telegram</div>
        </div>

        <div className="form-group">
          <label className="form-label">Your Telegram User ID</label>
          <input className="form-input" value={userId} onChange={e => setUserId(e.target.value)} placeholder="1234567890" style={{ maxWidth: 200 }} />
          <div className="form-hint">Get your user ID by messaging @userinfobot on Telegram</div>
        </div>

        {status && (
          <div style={{ marginBottom: 'var(--space-4)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', background: status.ok ? 'var(--success-subtle)' : 'var(--danger-subtle)', color: status.ok ? 'var(--success)' : 'var(--danger)', fontSize: 'var(--font-size-sm)' }}>
            {status.msg}
          </div>
        )}

        <button className="btn btn-primary" onClick={saveAndTest} disabled={loading}>{loading ? 'Connecting…' : 'Save & Test Connection'}</button>
      </div>

      <div className="card">
        <div className="card-title">Telegram Commands BOB Supports</div>
        <table className="data-table">
          <thead><tr><th>Command</th><th>Description</th></tr></thead>
          <tbody>
            {[
              ['/status',   'Get a live summary of BOB\'s current activity'],
              ['/stats',    'View today\'s application statistics'],
              ['/pause',    'Pause all automatic applications'],
              ['/resume',   'Resume automatic applications'],
              ['/vacancies','List today\'s discovered vacancies'],
              ['/applied',  'List today\'s submitted applications'],
              ['/report',   'Generate a detailed daily report'],
              ['/help',     'Show all available commands'],
            ].map(([cmd, desc]) => (
              <tr key={cmd}>
                <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 'var(--font-size-sm)' }}>{cmd}</td>
                <td>{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          🔒 BOB only responds to commands from your configured Telegram User ID. All other messages are ignored.
        </div>
      </div>
    </div>
  )
}
