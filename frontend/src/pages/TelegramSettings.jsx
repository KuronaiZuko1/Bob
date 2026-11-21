import React, { useContext, useState, useEffect } from 'react'
import { useSettings } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

export default function TelegramSettings() {
  const { data, refetch } = useSettings()
  const addToast = useContext(ToastContext)
  const [status, setStatus]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [token, setToken]     = useState('')
  const [userId, setUserId]   = useState('')

  useEffect(() => {
    if (data?.telegram_allowed_user_id) {
      setUserId(String(data.telegram_allowed_user_id))
    }
  }, [data])

  async function saveAndTest() {
    if (!token.trim()) { addToast('Enter a bot token first', 'warning'); return }
    setLoading(true)
    try {
      await client.put('/api/settings', { telegram: { bot_token: token, allowed_user_id: userId } })
      const res = await client.post('/api/settings/test-telegram')
      if (res.data?.ok) {
        setStatus({ msg: `✓ Telegram connected. Bot: @${res.data.bot_username}`, ok: true })
        addToast('Telegram connected!', 'success')
        refetch()
      } else {
        setStatus({ msg: `Bot responded but reported an error: ${res.data?.description}`, ok: false })
      }
    } catch (e) {
      setStatus({ msg: e.message, ok: false })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Telegram Notifications &amp; Commands</div>
          <div className="section-subtitle">BOB sends live notifications to your Telegram and accepts remote control commands</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Bot Configuration</div>
        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
          Create a Telegram bot via <strong>@BotFather</strong>, then paste the token below. BOB uses your Telegram User ID to restrict access to your account only.
        </div>

        <div className="form-group">
          <label className="form-label">Bot Token</label>
          <input className="form-input" type="password" value={token} onChange={e => setToken(e.target.value)} placeholder="123456:ABC-DEF…" style={{ maxWidth: 440 }} />
          <div className="form-hint">Obtain from @BotFather on Telegram</div>
        </div>

        <div className="form-group">
          <label className="form-label">Your Telegram User ID</label>
          <input className="form-input" value={userId} onChange={e => setUserId(e.target.value)} placeholder="e.g. 1916380095" style={{ maxWidth: 220 }} />
          <div className="form-hint">Get your user ID by messaging @userinfobot on Telegram</div>
        </div>

        {status && (
          <div style={{
            marginBottom: 'var(--space-4)', padding: 'var(--space-3)',
            borderRadius: 'var(--radius-md)',
            background: status.ok ? 'var(--success-subtle)' : 'var(--danger-subtle)',
            color: status.ok ? 'var(--success)' : 'var(--danger)',
            fontSize: 'var(--font-size-sm)'
          }}>
            {status.msg}
          </div>
        )}

        <button className="btn btn-primary" onClick={saveAndTest} disabled={loading}>
          {loading ? 'Connecting & Verifying…' : 'Save & Test Connection'}
        </button>
      </div>

      <div className="card">
        <div className="card-title">Supported Remote Telegram Commands</div>
        <table className="data-table">
          <thead><tr><th>Command</th><th>Action</th></tr></thead>
          <tbody>
            {[
              ['/status',   'Check live operational status of BOB'],
              ['/stats',    'View application counts and discovery statistics'],
              ['/pause',    'Pause all automatic job applications remotely'],
              ['/resume',   'Resume background applications and scanning'],
              ['/vacancies','List today\'s top eligible South African vacancies'],
              ['/applied',  'List your latest submitted applications'],
              ['/help',     'Display the command cheat-sheet'],
            ].map(([cmd, desc]) => (
              <tr key={cmd}>
                <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>{cmd}</td>
                <td>{desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          🔒 <strong>Privacy Shield:</strong> BOB masks all South African ID numbers and never reveals confidential document secrets in Telegram messages.
        </div>
      </div>
    </div>
  )
}
