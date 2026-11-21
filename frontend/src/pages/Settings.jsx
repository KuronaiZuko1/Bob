import React, { useContext, useState } from 'react'
import { useSettings } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

export default function Settings() {
  const { data, loading, refetch } = useSettings()
  const addToast = useContext(ToastContext)
  const [toggling, setToggling] = useState(false)

  const cfg = data || {}
  const paused = cfg.is_paused

  async function togglePause() {
    setToggling(true)
    try {
      await client.post('/api/settings/toggle-pause')
      addToast(paused ? 'BOB resumed — applications re-enabled' : 'BOB paused — applications suspended', paused ? 'success' : 'warning')
      refetch()
    } catch (e) {
      addToast(e.message, 'error')
    } finally { setToggling(false) }
  }

  if (loading) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /></div></div>

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Settings</div>
          <div className="section-subtitle">Control BOB's autonomous behaviour</div>
        </div>
      </div>

      {/* Master control */}
      <div className="card" style={{ marginBottom: 'var(--space-4)', borderColor: paused ? 'var(--warning)' : 'var(--border-subtle)' }}>
        <div className="card-title">Automation Control</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
              {paused ? '⏸ BOB is currently PAUSED' : '▶ BOB is currently RUNNING'}
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', marginTop: 4 }}>
              {paused ? 'No new applications will be submitted.' : 'BOB is autonomously searching and applying.'}
            </div>
          </div>
          <button
            className={`btn ${paused ? 'btn-primary' : 'btn-secondary'}`}
            onClick={togglePause}
            disabled={toggling}
            style={{ minWidth: 110 }}
          >
            {toggling ? 'Please wait…' : paused ? '▶ Resume BOB' : '⏸ Pause BOB'}
          </button>
        </div>
      </div>

      {/* Application settings */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Application Behaviour</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { label: 'TEST MODE', desc: 'Send email applications to your own address instead of real employers. MUST be off for real applications.', key: 'test_mode', value: cfg.test_mode ?? true, danger: true },
            { label: 'Auto Apply (ELIGIBLE only)', desc: 'Automatically submit applications for ELIGIBLE vacancies without manual approval.', key: 'auto_apply_enabled', value: cfg.auto_apply_enabled ?? false },
            { label: 'Send Telegram notifications', desc: 'Notify your Telegram account when BOB applies or encounters an issue.', key: 'telegram_notifications', value: cfg.telegram_notifications ?? true },
            { label: 'Generate daily reports', desc: 'Send a daily statistics report to your Telegram.', key: 'daily_reports', value: cfg.daily_reports ?? true },
          ].map(({ label, desc, key, value, danger }) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--space-4)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--font-size-sm)', color: danger && value ? 'var(--warning)' : 'var(--text-primary)' }}>{label}</div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>{desc}</div>
              </div>
              <div style={{
                width: 42, height: 24, borderRadius: 12,
                background: value ? (danger ? 'var(--warning)' : 'var(--accent)') : 'var(--bg-active)',
                position: 'relative', cursor: 'pointer', flexShrink: 0,
                border: '1px solid var(--border-muted)',
              }}>
                <div style={{
                  position: 'absolute', top: 2, left: value ? 18 : 2,
                  width: 18, height: 18, borderRadius: '50%',
                  background: '#fff', transition: 'left 0.15s ease',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                }} />
              </div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-3)', background: 'var(--warning-subtle)', border: '1px solid var(--border-muted)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-xs)', color: 'var(--warning)' }}>
          ⚠️ Disable TEST MODE only when you are ready to send real job applications. BOB will apply to real employers.
        </div>
      </div>

      {/* Search schedule */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Search Schedule</div>
        <div className="two-col">
          <div className="form-group">
            <label className="form-label">Search Interval</label>
            <select className="form-select" defaultValue="6">
              <option value="1">Every hour</option>
              <option value="2">Every 2 hours</option>
              <option value="6">Every 6 hours</option>
              <option value="12">Every 12 hours</option>
              <option value="24">Once daily</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Maximum applications per day</label>
            <input className="form-input" type="number" defaultValue={10} min={1} max={50} />
            <div className="form-hint">Prevents excessive submissions that may look suspicious to employers.</div>
          </div>
        </div>
      </div>

      {/* Version info */}
      <div className="card">
        <div className="card-title">About BOB</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 'var(--font-size-sm)' }}>
          {[
            ['Version', '1.0.0'],
            ['Backend', `${cfg.version || '1.0.0'} (FastAPI + SQLAlchemy)`],
            ['Database', 'SQLite (PostgreSQL-ready)'],
            ['AI Engine', 'Ollama (local) + OpenAI-compatible fallback'],
            ['Browser Automation', 'Playwright'],
            ['Platform', 'Windows (Electron + React + Vite)'],
          ].map(([k, v]) => (
            <div key={k} style={{ display: 'flex', gap: 16 }}>
              <span style={{ color: 'var(--text-muted)', minWidth: 160 }}>{k}</span>
              <span style={{ color: 'var(--text-secondary)' }}>{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
