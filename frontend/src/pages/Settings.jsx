import React, { useContext, useState } from 'react'
import { useSettings } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

export default function Settings() {
  const { data, loading, refetch } = useSettings()
  const addToast = useContext(ToastContext)
  const [toggling, setToggling] = useState(false)
  const [updatingKey, setUpdatingKey] = useState(null)

  const cfg = data || {}
  const paused = cfg.agent_status === 'Paused' || cfg.is_paused

  async function togglePause() {
    setToggling(true)
    try {
      const res = await client.post('/api/settings/toggle-pause')
      const isNowPaused = res.data?.is_paused
      addToast(
        isNowPaused ? 'BOB paused — autonomous actions suspended' : 'BOB resumed — autonomous actions active',
        isNowPaused ? 'warning' : 'success'
      )
      refetch()
    } catch (e) {
      addToast(e.message, 'error')
    } finally {
      setToggling(false)
    }
  }

  async function handleToggleSetting(key, currentValue) {
    setUpdatingKey(key)
    const newValue = !currentValue
    try {
      await client.put('/api/settings', { [key]: newValue })
      addToast(`Setting "${key}" updated to ${newValue ? 'ON' : 'OFF'}`, 'success')
      refetch()
    } catch (e) {
      addToast(`Failed to update setting: ${e.message}`, 'error')
    } finally {
      setUpdatingKey(null)
    }
  }

  async function handleIntervalChange(val) {
    try {
      await client.put('/api/settings', { job_search_interval_hours: parseInt(val) })
      addToast(`Search interval set to every ${val} hours`, 'success')
      refetch()
    } catch (e) {
      addToast(e.message, 'error')
    }
  }

  if (loading) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /></div></div>

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Settings &amp; Automation Control</div>
          <div className="section-subtitle">Manage BOB's operational parameters, safety limits, and autonomous behaviour</div>
        </div>
      </div>

      {/* Master control */}
      <div className="card" style={{ marginBottom: 'var(--space-4)', borderColor: paused ? 'var(--warning)' : 'var(--border-subtle)' }}>
        <div className="card-title">Master Automation Switch</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 'var(--font-size-md)' }}>
              {paused ? '⏸ BOB is currently PAUSED' : '▶ BOB is currently RUNNING & ACTIVE'}
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', marginTop: 4 }}>
              {paused
                ? 'Autonomous discovery and applications are suspended. No automatic actions will occur.'
                : 'BOB periodically hunts for official vacancies and evaluates eligibility in the background.'}
            </div>
          </div>
          <button
            className={`btn ${paused ? 'btn-primary' : 'btn-secondary'}`}
            onClick={togglePause}
            disabled={toggling}
            style={{ minWidth: 130 }}
          >
            {toggling ? 'Please wait…' : paused ? '▶ Resume BOB' : '⏸ Pause BOB'}
          </button>
        </div>
      </div>

      {/* Application settings */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Production Safety &amp; Behaviour</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {[
            {
              label: 'TEST MODE',
              desc: 'Simulates email sending and portal form submissions without live dispatch. Turn OFF when you are ready to send real applications to real employers.',
              key: 'test_mode',
              value: cfg.test_mode ?? true,
              danger: true
            },
            {
              label: 'Auto Apply (ELIGIBLE Vacancies Only)',
              desc: 'When enabled, BOB automatically prepares truthful CVs and submits for vacancies classified as 100% ELIGIBLE without waiting for manual confirmation.',
              key: 'auto_apply_enabled',
              value: cfg.auto_apply_enabled ?? false
            },
          ].map(({ label, desc, key, value, danger }) => {
            const isUpdating = updatingKey === key

            return (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--space-4)' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--font-size-sm)', color: danger && value ? 'var(--warning)' : 'var(--text-primary)' }}>
                    {label} {value ? (danger ? '(ACTIVE — SIMULATED)' : '(ACTIVE)') : '(DISABLED)'}
                  </div>
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>{desc}</div>
                </div>
                <div
                  onClick={() => !isUpdating && handleToggleSetting(key, value)}
                  style={{
                    width: 44, height: 26, borderRadius: 13,
                    background: value ? (danger ? 'var(--warning)' : 'var(--accent)') : 'var(--bg-active)',
                    position: 'relative', cursor: isUpdating ? 'wait' : 'pointer', flexShrink: 0,
                    border: '1px solid var(--border-muted)', opacity: isUpdating ? 0.6 : 1
                  }}
                  title={`Click to turn ${value ? 'OFF' : 'ON'}`}
                >
                  <div style={{
                    position: 'absolute', top: 3, left: value ? 20 : 3,
                    width: 18, height: 18, borderRadius: '50%',
                    background: '#fff', transition: 'left 0.15s ease',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                  }} />
                </div>
              </div>
            )
          })}
        </div>
        <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-3)', background: 'var(--warning-subtle)', border: '1px solid var(--border-muted)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-xs)', color: 'var(--warning)' }}>
          ⚠️ <strong>Production Notice:</strong> When <code>TEST MODE</code> is toggled OFF, BOB sends live emails through your connected Gmail account and submits real forms.
        </div>
      </div>

      {/* Search schedule */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Autonomous Search Schedule</div>
        <div className="two-col">
          <div className="form-group">
            <label className="form-label">Background Scan Interval</label>
            <select
              className="form-select"
              value={cfg.job_search_interval_hours || 6}
              onChange={e => handleIntervalChange(e.target.value)}
            >
              <option value="1">Every 1 hour</option>
              <option value="2">Every 2 hours</option>
              <option value="4">Every 4 hours</option>
              <option value="6">Every 6 hours (Recommended)</option>
              <option value="12">Every 12 hours</option>
              <option value="24">Once daily (24 hours)</option>
            </select>
            <div className="form-hint">Controls how often the background scheduler queries active job sources.</div>
          </div>
          <div className="form-group">
            <label className="form-label">Target Market</label>
            <input className="form-input" disabled value={cfg.job_market || 'South Africa'} />
            <div className="form-hint">Dedicated to South African employment portals.</div>
          </div>
        </div>
      </div>

      {/* System Details */}
      <div className="card">
        <div className="card-title">System Status</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 'var(--font-size-sm)' }}>
          {[
            ['App Name', cfg.app_name || 'Bob'],
            ['Environment', cfg.app_env || 'Production-Ready'],
            ['AI Provider', cfg.ai_provider || 'ollama'],
            ['Gmail Status', cfg.gmail_configured ? 'Configured' : 'Not Connected'],
            ['Telegram Bot', cfg.telegram_bot_configured ? 'Configured' : 'Not Configured'],
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
