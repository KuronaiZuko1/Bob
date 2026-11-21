import React, { useState } from 'react'
import { useApplications } from '../hooks/useApi'

const STATUS_BADGE = {
  sent:       'badge-sent',
  failed:     'badge-failed',
  pending:    'badge-pending',
  draft:      'badge-draft',
  paused:     'badge-uncertain',
}

export default function Applications() {
  const [filter, setFilter] = useState({ status: '', method: '' })
  const { data, loading, error, refetch } = useApplications({ status: filter.status || undefined, method: filter.method || undefined })

  const apps = data?.applications || data || []

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Applications</div>
          <div className="section-subtitle">Every application BOB has sent or attempted</div>
        </div>
        <button className="btn btn-secondary" onClick={refetch}>↻ Refresh</button>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', padding: 'var(--space-3) var(--space-4)' }}>
        <select className="form-select" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
          <option value="">All statuses</option>
          <option value="sent">Sent</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
          <option value="paused">Paused</option>
          <option value="draft">Draft</option>
        </select>
        <select className="form-select" value={filter.method} onChange={e => setFilter(f => ({ ...f, method: e.target.value }))}>
          <option value="">All methods</option>
          <option value="email">Email</option>
          <option value="website">Website</option>
          <option value="manual">Manual</option>
        </select>
      </div>

      {loading && <div className="loading-state"><div className="spinner" /><span>Loading applications…</span></div>}
      {error   && <div className="empty-state">⚠️ {error}</div>}

      {!loading && !error && apps.length === 0 && (
        <div className="empty-state">
          <div style={{ fontSize: 32 }}>📋</div>
          <div>No applications yet. BOB will apply automatically for ELIGIBLE vacancies once configured.</div>
        </div>
      )}

      {!loading && apps.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Job Title</th>
                <th>Employer</th>
                <th>Method</th>
                <th>Status</th>
                <th>Applied</th>
                <th>Ref</th>
              </tr>
            </thead>
            <tbody>
              {apps.map((a) => (
                <tr key={a.id}>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{a.vacancy?.title || a.vacancy_id}</td>
                  <td>{a.vacancy?.employer || '—'}</td>
                  <td><span className="tag">{a.application_method || '—'}</span></td>
                  <td><span className={`badge ${STATUS_BADGE[a.status] || 'badge-draft'}`}>{a.status}</span></td>
                  <td style={{ fontSize: 'var(--font-size-xs)' }}>{a.submitted_at ? new Date(a.submitted_at).toLocaleString('en-ZA') : '—'}</td>
                  <td style={{ fontSize: 'var(--font-size-xs)', fontFamily: 'var(--font-mono)' }}>{a.submission_reference || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
