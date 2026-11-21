import React, { useState, useContext } from 'react'
import { useApplications } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

const STATUS_BADGE = {
  SUBMITTED:           'badge-eligible',
  SENT:                'badge-eligible',
  SUBMITTED_TEST_MODE: 'badge-eligible',
  PENDING:             'badge-uncertain',
  FAILED:              'badge-not-eligible',
  REQUIRES_ATTENTION:  'badge-not-eligible',
  PAUSED:              'badge-draft',
}

export default function Applications() {
  const [filter, setFilter] = useState({ status: '', method: '' })
  const { data, loading, error, refetch } = useApplications({
    status: filter.status || undefined,
    method: filter.method || undefined
  })
  const [submittingId, setSubmittingId] = useState(null)
  const addToast = useContext(ToastContext)

  const apps = data?.applications || data || []

  async function handleSubmit(appId) {
    if (!window.confirm('Submit this application now?')) return
    setSubmittingId(appId)
    try {
      const res = await client.post(`/api/applications/${appId}/submit`)
      addToast(`Application #${appId} dispatched! Status: ${res.data.status}`, 'success')
      refetch()
    } catch (err) {
      addToast(`Submission failed: ${err.response?.data?.detail || err.message}`, 'error')
    } finally {
      setSubmittingId(null)
    }
  }

  function handleDownload(appId, type, fmt = 'pdf') {
    const url = type === 'cv'
      ? `/api/applications/${appId}/download-cv?fmt=${fmt}`
      : `/api/applications/${appId}/download-cover-letter`
    window.open(`http://localhost:8000${url}`, '_blank')
  }

  async function handleDelete(appId) {
    if (!window.confirm(`Delete application record #${appId}?`)) return
    try {
      await client.delete(`/api/applications/${appId}`)
      addToast('Application deleted', 'success')
      refetch()
    } catch (err) {
      addToast(`Delete failed: ${err.message}`, 'error')
    }
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Applications</div>
          <div className="section-subtitle">Real employment applications managed, tailored, and submitted by BOB</div>
        </div>
        <button className="btn btn-secondary" onClick={refetch}>↻ Refresh</button>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', padding: 'var(--space-3) var(--space-4)' }}>
        <select className="form-select" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
          <option value="">All statuses</option>
          <option value="SUBMITTED">Submitted / Sent</option>
          <option value="PENDING">Pending</option>
          <option value="FAILED">Failed</option>
          <option value="PAUSED">Paused</option>
        </select>
        <select className="form-select" value={filter.method} onChange={e => setFilter(f => ({ ...f, method: e.target.value }))}>
          <option value="">All methods</option>
          <option value="email">Email (Gmail)</option>
          <option value="website">Web Portal (Playwright)</option>
        </select>
      </div>

      {loading && <div className="loading-state"><div className="spinner" /><span>Loading applications…</span></div>}
      {error   && <div className="empty-state">⚠️ {error}</div>}

      {!loading && !error && apps.length === 0 && (
        <div className="empty-state">
          <div style={{ fontSize: 32 }}>📋</div>
          <div>No applications created yet. Go to <strong>Job Discovery</strong> and click <strong>⚡ Generate Tailored CV &amp; Letter</strong> on an ELIGIBLE vacancy.</div>
        </div>
      )}

      {!loading && apps.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Job Title / Employer</th>
                <th>Method</th>
                <th>Status</th>
                <th>Tailored Documents</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {apps.map((a) => {
                const isPending = a.status === 'PENDING'
                const isSubmitting = submittingId === a.id

                return (
                  <tr key={a.id}>
                    <td>
                      <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                        {a.vacancy?.title || `Vacancy #${a.vacancy_id}`}
                      </div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                        {a.vacancy?.employer || '—'} · Ref: {a.vacancy?.reference_number || 'N/A'}
                      </div>
                    </td>
                    <td>
                      <span className="tag">{a.application_method || 'email'}</span>
                    </td>
                    <td>
                      <span className={`badge ${STATUS_BADGE[a.status] || 'badge-draft'}`}>
                        {a.status}
                      </span>
                      {a.submitted_at && (
                        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
                          {new Date(a.submitted_at).toLocaleDateString('en-ZA')}
                        </div>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {a.tailored_cv_path && (
                          <>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleDownload(a.id, 'cv', 'pdf')}>
                              CV (PDF)
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleDownload(a.id, 'cv', 'docx')}>
                              CV (DOCX)
                            </button>
                          </>
                        )}
                        {a.cover_letter_path && (
                          <button className="btn btn-secondary btn-sm" onClick={() => handleDownload(a.id, 'cover_letter')}>
                            Cover Letter
                          </button>
                        )}
                        {!a.tailored_cv_path && (
                          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>Not generated</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {isPending && (
                          <button
                            className="btn btn-primary btn-sm"
                            disabled={isSubmitting}
                            onClick={() => handleSubmit(a.id)}
                          >
                            {isSubmitting ? 'Sending…' : '🚀 Submit Now'}
                          </button>
                        )}
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => handleDelete(a.id)}
                          style={{ color: 'var(--danger)' }}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
