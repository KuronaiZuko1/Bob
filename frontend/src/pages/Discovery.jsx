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
  return <span className={`badge ${ELIGIBILITY_BADGES[status] || 'badge-draft'}`}>{status?.replace('_', ' ') || 'Pending Check'}</span>
}

function AddVacancyModal({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState({
    title: '', employer: '', location: 'Gauteng', province: 'Gauteng',
    employment_type: 'Full-time', qualification_requirements: '',
    experience_requirements: '', skills_requirements: '',
    application_method: 'email', application_email: '', application_url: '',
    reference_number: '', description: '', closing_date: ''
  })
  const [loading, setLoading] = useState(false)
  const addToast = useContext(ToastContext)

  if (!isOpen) return null

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.title.trim() || !form.employer.trim() || !form.description.trim()) {
      addToast('Please provide Title, Employer, and Job Description.', 'warning')
      return
    }
    setLoading(true)
    try {
      const res = await client.post('/api/vacancies', form)
      addToast(`Vacancy "${res.data.title}" added and evaluated by BOB!`, 'success')
      onCreated()
      onClose()
    } catch (err) {
      addToast(`Failed to add vacancy: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.65)', zIndex: 1100,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-surface)', border: '1px solid var(--border-muted)',
        borderRadius: 'var(--radius-lg)', padding: 24, maxWidth: 680, width: '100%',
        maxHeight: '85vh', overflowY: 'auto'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ fontWeight: 700, fontSize: 'var(--font-size-lg)', marginBottom: 4 }}>Add Real Job Vacancy</div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginBottom: 16 }}>
          Paste details of any real South African job you want BOB to analyze, tailor documents for, and submit.
        </div>

        <form onSubmit={handleSubmit}>
          <div className="two-col" style={{ gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Job Title *</label>
              <input className="form-input" required value={form.title} onChange={e => set('title', e.target.value)} placeholder="e.g. Marketing Coordinator" />
            </div>
            <div className="form-group">
              <label className="form-label">Employer / Company *</label>
              <input className="form-input" required value={form.employer} onChange={e => set('employer', e.target.value)} placeholder="e.g. Shoprite or Dept of Health" />
            </div>
            <div className="form-group">
              <label className="form-label">Location / City</label>
              <input className="form-input" value={form.location} onChange={e => set('location', e.target.value)} placeholder="e.g. Johannesburg" />
            </div>
            <div className="form-group">
              <label className="form-label">Province</label>
              <select className="form-select" value={form.province} onChange={e => set('province', e.target.value)}>
                {['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Free State', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 'National'].map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Application Method</label>
              <select className="form-select" value={form.application_method} onChange={e => set('application_method', e.target.value)}>
                <option value="email">Email Application</option>
                <option value="website">Online Web Portal</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Reference Number (optional)</label>
              <input className="form-input" value={form.reference_number} onChange={e => set('reference_number', e.target.value)} placeholder="e.g. REF-2026/09" />
            </div>
            <div className="form-group">
              <label className="form-label">Application Email (if applicable)</label>
              <input className="form-input" type="email" value={form.application_email} onChange={e => set('application_email', e.target.value)} placeholder="careers@company.co.za" />
            </div>
            <div className="form-group">
              <label className="form-label">Closing Date (optional)</label>
              <input className="form-input" value={form.closing_date} onChange={e => set('closing_date', e.target.value)} placeholder="e.g. 2026-12-15" />
            </div>
          </div>

          <div className="form-group" style={{ marginTop: 8 }}>
            <label className="form-label">Application URL / Link (optional)</label>
            <input className="form-input" value={form.application_url} onChange={e => set('application_url', e.target.value)} placeholder="https://careers.company.co.za/job/123" />
          </div>

          <div className="form-group" style={{ marginTop: 8 }}>
            <label className="form-label">Qualification &amp; Experience Requirements</label>
            <input className="form-input" value={form.qualification_requirements} onChange={e => set('qualification_requirements', e.target.value)} placeholder="e.g. Matric, Marketing Certificate N5, no prior experience needed" />
          </div>

          <div className="form-group" style={{ marginTop: 8 }}>
            <label className="form-label">Job Description / Requirements *</label>
            <textarea className="form-input" required rows={4} style={{ resize: 'vertical' }} value={form.description} onChange={e => set('description', e.target.value)} placeholder="Paste the job advertisement duties, requirements, and instructions here…" />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 16 }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Ingesting…' : 'Add & Analyze with BOB'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function VacancyDetail({ v, onClose, onRefresh }) {
  const [generating, setGenerating] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const addToast = useContext(ToastContext)

  if (!v) return null

  async function handleGenerateDocuments() {
    setGenerating(true)
    try {
      const res = await client.post(`/api/applications/generate-documents/${v.id}`)
      addToast(`Tailored CV & Cover Letter generated successfully for "${v.title}"!`, 'success')
      if (onRefresh) onRefresh()
    } catch (err) {
      addToast(`Document generation failed: ${err.response?.data?.detail || err.message}`, 'error')
    } finally {
      setGenerating(false)
    }
  }

  async function handleReEvaluate() {
    setEvaluating(true)
    try {
      const res = await client.post(`/api/vacancies/${v.id}/evaluate`)
      addToast(`Eligibility evaluated: ${res.data.eligibility_status}`, 'success')
      if (onRefresh) onRefresh()
    } catch (err) {
      addToast(`Evaluation failed: ${err.message}`, 'error')
    } finally {
      setEvaluating(false)
    }
  }

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
          ['Requirements', v.qualification_requirements],
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
        <div style={{ marginTop: 20, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {v.eligibility_status === 'ELIGIBLE' && (
            <button className="btn btn-primary btn-sm" onClick={handleGenerateDocuments} disabled={generating}>
              {generating ? 'Generating Documents…' : '⚡ Generate Tailored CV & Letter'}
            </button>
          )}
          <button className="btn btn-secondary btn-sm" onClick={handleReEvaluate} disabled={evaluating}>
            {evaluating ? 'Evaluating…' : '🔄 Re-evaluate Eligibility'}
          </button>
          {v.source_url && v.source_url !== 'Manual Entry' && (
            <a href={v.source_url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">View Original</a>
          )}
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
  const [addModalOpen, setAddModalOpen] = useState(false)
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
          <div className="section-subtitle">Real South African vacancies discovered by BOB across official DPSA, entry-level, and corporate sources</div>
        </div>
        <div className="topbar-actions" style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={() => setAddModalOpen(true)}>
            + Add Real Vacancy
          </button>
          <button className="btn btn-primary" onClick={handleTriggerDiscovery} disabled={scanning}>
            {scanning ? 'Searching Sources…' : '🔍 Scan Sources Now'}
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
          <div>No vacancies found yet. Click <strong>Scan Sources Now</strong> to discover real South African jobs or click <strong>+ Add Real Vacancy</strong> to paste one.</div>
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
                  <td><span className="tag">{v.application_method || 'email'}</span></td>
                  <td>
                    <button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); setSelected(v) }}>
                      View &amp; Apply
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <VacancyDetail v={selected} onClose={() => setSelected(null)} onRefresh={refetch} />
      <AddVacancyModal isOpen={addModalOpen} onClose={() => setAddModalOpen(false)} onCreated={refetch} />
    </div>
  )
}
