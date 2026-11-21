import React from 'react'
import { useStats, useActivity, useHealth } from '../hooks/useApi'

function StatCard({ value, label, trend }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value ?? '—'}</div>
      <div className="stat-label">{label}</div>
      {trend && <div className={`stat-trend ${trend.dir}`}>{trend.text}</div>}
    </div>
  )
}

function EligibilityBar({ eligible, not_eligible, uncertain }) {
  const total = (eligible || 0) + (not_eligible || 0) + (uncertain || 0) || 1
  return (
    <div style={{ display: 'flex', gap: 4, height: 8, borderRadius: 4, overflow: 'hidden', marginTop: 8 }}>
      <div style={{ width: `${(eligible/total)*100}%`, background: 'var(--success)' }} title={`Eligible: ${eligible}`} />
      <div style={{ width: `${(uncertain/total)*100}%`, background: 'var(--warning)' }} title={`Uncertain: ${uncertain}`} />
      <div style={{ width: `${(not_eligible/total)*100}%`, background: 'var(--danger)' }} title={`Not eligible: ${not_eligible}`} />
    </div>
  )
}

export default function Overview() {
  const { data: stats, loading: sLoad, error: sErr } = useStats()
  const { data: activityData, loading: aLoad }       = useActivity()
  const { data: health }                             = useHealth()

  if (sLoad) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /><span>Loading dashboard…</span></div></div>
  if (sErr)  return <div className="page-scroll"><div className="empty-state">⚠️ Could not reach backend: {sErr}</div></div>

  const s = stats || {}
  // Backend returns array directly for /api/stats/activity
  const activities = Array.isArray(activityData) ? activityData : (activityData?.activities || [])

  return (
    <div className="page-scroll">
      {/* Header */}
      <div className="section-header">
        <div>
          <div className="section-title">Dashboard Overview</div>
          <div className="section-subtitle">BOB is {health?.status === 'online' ? 'running autonomously' : 'offline'} · {new Date().toLocaleDateString('en-ZA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="stat-grid">
        <StatCard value={s.total_discovered ?? 0}             label="Vacancies Found" />
        <StatCard value={s.applications_submitted_total ?? 0} label="Applications Sent" />
        <StatCard value={s.eligible_count ?? 0}               label="Eligible Jobs" />
        <StatCard value={s.pending_applications ?? 0}         label="Pending Review" />
        <StatCard value={s.email_applications_sent ?? 0}      label="Email Applications" />
        <StatCard value={s.failed_applications ?? 0}          label="Failed" trend={s.failed_applications > 0 ? { dir: 'down', text: 'Need attention' } : null} />
      </div>

      {/* Two-col: Eligibility breakdown + Recent Activity */}
      <div className="two-col">

        {/* Eligibility breakdown */}
        <div className="card">
          <div className="card-title">Eligibility Breakdown</div>
          <div style={{ display: 'flex', gap: 24, marginBottom: 8 }}>
            <div>
              <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--success)' }}>{s.eligible_count ?? 0}</div>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Eligible</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--warning)' }}>{s.uncertain_count ?? 0}</div>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Uncertain</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--danger)' }}>{s.not_eligible_count ?? 0}</div>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Not Eligible</div>
            </div>
          </div>
          <EligibilityBar
            eligible={s.eligible_count}
            not_eligible={s.not_eligible_count}
            uncertain={s.uncertain_count}
          />
          <div style={{ marginTop: 12, fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Only ELIGIBLE vacancies are submitted automatically.
          </div>
        </div>

        {/* Application methods */}
        <div className="card">
          <div className="card-title">Application Methods</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { label: 'Email (Gmail)', value: s.email_applications_sent ?? 0, color: 'var(--accent)' },
              { label: 'Website (Playwright)', value: s.website_applications_submitted ?? 0, color: 'var(--success)' },
              { label: 'Failed', value: s.failed_applications ?? 0, color: 'var(--danger)' },
            ].map(({ label, value, color }) => {
              const total = (s.applications_submitted_total || 1)
              return (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-sm)', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{value}</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${Math.min((value/total)*100, 100)}%`, background: color }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="divider" />

      {/* Recent activity */}
      <div className="card">
        <div className="card-title">Recent Activity</div>
        {aLoad && <div className="loading-state"><div className="spinner" /></div>}
        {!aLoad && activities.length === 0 && (
          <div className="empty-state" style={{ padding: 'var(--space-5)' }}>No activity recorded yet. BOB is ready to hunt.</div>
        )}
        <div className="activity-feed">
          {activities.map((a, i) => (
            <div key={i} className="activity-item">
              <div className="activity-dot" style={{ background: a.type === 'error' ? 'var(--danger)' : a.type === 'warning' ? 'var(--warning)' : 'var(--accent)' }} />
              <div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>{a.description || a.title}</div>
                <div className="activity-time">{a.timestamp || '—'}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
