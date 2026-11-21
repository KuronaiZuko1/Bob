import React, { useState, useContext } from 'react'
import { useVacancies } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

const ELIGIBILITY_BADGES = {
  ELIGIBLE:     'badge-eligible',
  NOT_ELIGIBLE: 'badge-not-eligible',
  UNCERTAIN:    'badge-uncertain',
}

function EligibilityBadge({ status }) {
  return <span className={`badge ${ELIGIBILITY_BADGES[status] || 'badge-draft'}`}>{status?.replace('_', ' ') || 'Unknown'}</span>
}

function VacancyDetail({ v, onClose }) {
  if (!v) return null
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 1000,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-surface)', border: '1px solid var(--border-muted)',
        borderRadius: 'var(--radius-lg)', padding: 24, maxWidth: 640, width: '100%',
        maxHeight: '80vh', overflowY: 'auto'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 'var(--font-size-lg)', color: 'var(--text-primary)' }}>{v.title}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>{v.employer} · {v.location}</div>
          </div>
          <EligibilityBadge status={v.eligibility_status} />
        </div>
        <div className="divider" style={{ margin: '12px 0' }} />
        {[
          ['Province', v.province],
          ['Employment Type', v.employment_type],
          ['Salary', v.salary],
          ['Closing Date', v.closing_date],
          ['Reference Number', v.reference_number],
          ['Application Method', v.application_method],
          ['Application Email', v.application_email],
        ].map(([k, val]) => val && (
          <div key={k} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: 'var(--font-size-sm)' }}>
            <span style={{ color: 'var(--text-muted)', minWidth: 160 }}>{k}</span>
            <span style={{ color: 'var(--text-primary)' }}>{val}</span>
          </div>
        ))}
        {v.description && (
          <>
            <div className="divider" style={{ margin: '12px 0' }} />
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', maxHeight: 200, overflowY: 'auto' }}>{v.description}</div>
          </>
        )}
        {v.eligibility_explanation && (
          <>
            <div className="divider" style={{ margin: '12px 0' }} />
            <div className="card-title">BOB's Eligibility Assessment</div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>{v.eligibility_explanation}</div>
          </>
        )}
        <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
          {v.source_url && <a href={v.source_url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">View Original</a>}
          <button className="btn btn-secondary btn-sm" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}

export default function Discovery() {
  const [filter, setFilter] = useState({ eligibility: '', search: '' })
  const { data, loading, error, refetch } = useVacancies({ eligibility: filter.eligibility || undefined, search: filter.search || undefined })
  const [selected, setSelected] = useState(null)
  const [scanning, setScanning] = useState(false)
  const addToast = useContext(ToastContext)

  const vacancies = data?.vacancies || data || []

  async function handleTriggerDiscovery() {
    setScanning(true)
    try {
      const res = await client.post('/api/vacancies/discover')
      const stats = res.data?.stats
      if (stats) {
        addToast(`Scanned ${stats.sources_scanned} sources. Found ${stats.discovered_total} posts (+${stats.new_vacancies_added} new, ${stats.evaluated_eligible} eligible).`, 'success')
      } else {
        addToast(res.data?.message || 'Discovery completed.', 'success')
      }
      refetch()
    } catch (err) {
      addToast(`Discovery failed: ${err.message}`, 'error')
    } finally {
      setScanning(false)
    }
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Job Discovery</div>
          <div className="section-subtitle">South African vacancies discovered by BOB across official DPSA, entry-level, and corporate sources</div>
        </div>
        <div className="topbar-actions" style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-primary" onClick={handleTriggerDiscovery} disabled={scanning}>
            {scanning ? 'Searching...' : '🔍 Scan Sources Now'}
          </button>
          <button className="btn btn-secondary" onClick={refetch}>↻ Refresh</button>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', alignItems: 'center', padding: 'var(--space-3) var(--space-4)' }}>
        <input
          className="form-input"
          placeholder="Search vacancies by title, employer, description…"
          style={{ flex: 1 }}
          value={filter.search}
          onChange={e => setFilter(f => ({ ...f, search: e.target.value }))}
        />
        <select className="form-select" value={filter.eligibility} onChange={e => setFilter(f => ({ ...f, eligibility: e.target.value }))}>
          <option value="">All eligibility</option>
          <option value="ELIGIBLE">Eligible</option>
          <option value="UNCERTAIN">Uncertain</option>
          <option value="NOT_ELIGIBLE">Not Eligible</option>
        </select>
      </div>

      {loading && <div className="loading-state"><div className="spinner" /><span>Loading vacancies…</span></div>}
      {error   && <div className="empty-state">⚠️ {error}</div>}

      {!loading && !error && vacancies.length === 0 && (
        <div className="empty-state">
          <div style={{ fontSize: 32 }}>🔍</div>
          <div>No vacancies found. Click <strong>Scan Sources Now</strong> to search official South African portals.</div>
        </div>
      )}

      {!loading && vacancies.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Job Title</th>
                <th>Employer</th>
                <th>Location</th>
                <th>Closing</th>
                <th>Eligibility</th>
                <th>Method</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {vacancies.map((v) => (
                <tr key={v.id} style={{ cursor: 'pointer' }} onClick={() => setSelected(v)}>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{v.title}</td>
                  <td>{v.employer}</td>
                  <td>{v.location || v.province || '—'}</td>
                  <td style={{ fontSize: 'var(--font-size-xs)' }}>{v.closing_date || '—'}</td>
                  <td><EligibilityBadge status={v.eligibility_status} /></td>
                  <td style={{ fontSize: 'var(--font-size-xs)' }}>{v.application_method || '—'}</td>
                  <td><button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); setSelected(v) }}>View</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <VacancyDetail v={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
