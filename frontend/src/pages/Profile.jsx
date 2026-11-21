import React, { useState, useContext } from 'react'
import { useProfile } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

function Section({ title, children }) {
  return (
    <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
      <div className="card-title">{title}</div>
      {children}
    </div>
  )
}

function Field({ label, value, hint }) {
  return (
    <div className="form-group">
      <div className="form-label">{label}</div>
      <div style={{ color: value ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: value ? 'normal' : 'italic', fontSize: 'var(--font-size-sm)' }}>
        {value || 'Not provided'}
      </div>
      {hint && <div className="form-hint">{hint}</div>}
    </div>
  )
}

export default function Profile() {
  const { data: profile, loading, error, refetch } = useProfile()
  const addToast = useContext(ToastContext)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [saving, setSaving] = useState(false)

  function startEdit() {
    setForm({ ...profile })
    setEditing(true)
  }

  function cancelEdit() {
    setForm({})
    setEditing(false)
  }

  async function saveProfile() {
    setSaving(true)
    try {
      await client.put('/api/profile', form)
      addToast('Profile saved successfully', 'success')
      setEditing(false)
      refetch()
    } catch (e) {
      addToast(`Save failed: ${e.message}`, 'error')
    } finally {
      setSaving(false)
    }
  }

  function set(key, val) { setForm((f) => ({ ...f, [key]: val })) }

  if (loading) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /><span>Loading profile…</span></div></div>
  if (error)   return <div className="page-scroll"><div className="empty-state">⚠️ {error}</div></div>

  const p = profile || {}

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">My Profile</div>
          <div className="section-subtitle">Your verified employment profile. BOB uses this to evaluate eligibility — no information is invented.</div>
        </div>
        <div className="topbar-actions">
          {!editing
            ? <button className="btn btn-primary" onClick={startEdit}>Edit Profile</button>
            : <>
                <button className="btn btn-secondary" onClick={cancelEdit} disabled={saving}>Cancel</button>
                <button className="btn btn-primary" onClick={saveProfile} disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button>
              </>
          }
        </div>
      </div>

      {/* Personal */}
      <Section title="Personal Information">
        {editing ? (
          <div className="two-col">
            {[
              ['full_name','Full Legal Name'],['email','Email Address'],['phone','Phone Number'],
              ['id_number','SA ID Number'],['date_of_birth','Date of Birth'],['gender','Gender'],
              ['nationality','Nationality'],['province','Province'],['city','City / Town'],
              ['address','Residential Address'],
            ].map(([k, label]) => (
              <div className="form-group" key={k}>
                <label className="form-label">{label}</label>
                <input className="form-input" value={form[k] || ''} onChange={e => set(k, e.target.value)} />
              </div>
            ))}
          </div>
        ) : (
          <div className="two-col">
            <Field label="Full Legal Name"     value={p.full_name} />
            <Field label="Email Address"       value={p.email} />
            <Field label="Phone Number"        value={p.phone} />
            <Field label="SA ID Number"        value={p.id_number ? '•••••••••••' : null} hint="Hidden for security" />
            <Field label="Date of Birth"       value={p.date_of_birth} />
            <Field label="Gender"              value={p.gender} />
            <Field label="Nationality"         value={p.nationality} />
            <Field label="Province"            value={p.province} />
            <Field label="City / Town"         value={p.city} />
            <Field label="Address"             value={p.address} />
          </div>
        )}
      </Section>

      {/* Qualifications */}
      <Section title="Qualifications">
        {p.qualifications && p.qualifications.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Qualification</th><th>Institution</th><th>Year</th><th>Verified</th>
              </tr>
            </thead>
            <tbody>
              {p.qualifications.map((q) => (
                <tr key={q.id}>
                  <td>{q.name}</td>
                  <td>{q.institution || '—'}</td>
                  <td>{q.year_obtained || '—'}</td>
                  <td><span className={`badge ${q.is_verified ? 'badge-eligible' : 'badge-pending'}`}>{q.is_verified ? 'Verified' : 'Pending'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-4)' }}>No qualifications added. Upload your certificates in Documents to verify them.</div>
        )}
      </Section>

      {/* Skills */}
      <Section title="Skills">
        {p.skills && p.skills.length > 0 ? (
          <div className="tag-list">
            {p.skills.map((s) => (
              <span key={s.id} className="tag" title={s.proficiency_level}>{s.name}</span>
            ))}
          </div>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-3)' }}>No skills added yet.</div>
        )}
      </Section>

      {/* Experience */}
      <Section title="Employment History">
        {p.experiences && p.experiences.length > 0 ? (
          p.experiences.map((e) => (
            <div key={e.id} style={{ marginBottom: 'var(--space-4)', paddingBottom: 'var(--space-4)', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{e.job_title}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>{e.employer} · {e.start_date} – {e.end_date || 'Present'}</div>
              {e.description && <div style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{e.description}</div>}
            </div>
          ))
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-3)' }}>
            No formal employment experience recorded. BOB will not invent any.
          </div>
        )}
      </Section>

      {/* Languages + Licence */}
      <Section title="Languages &amp; Licences">
        <div className="two-col">
          <div>
            <div className="form-label" style={{ marginBottom: 8 }}>Languages</div>
            {editing ? (
              <input className="form-input" value={form.languages || ''} onChange={e => set('languages', e.target.value)} placeholder="e.g. English, Zulu, Afrikaans" />
            ) : (
              <div style={{ color: p.languages ? 'var(--text-primary)' : 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{p.languages || 'Not specified'}</div>
            )}
          </div>
          <div>
            <div className="form-label" style={{ marginBottom: 8 }}>Driver's Licence</div>
            {editing ? (
              <select className="form-select" value={form.drivers_licence || ''} onChange={e => set('drivers_licence', e.target.value)}>
                <option value="">Unknown / None</option>
                <option value="Code B">Code B (Light motor vehicle)</option>
                <option value="Code C">Code C (Heavy motor vehicle)</option>
                <option value="Code EC">Code EC (Extra heavy)</option>
              </select>
            ) : (
              <div style={{ color: p.drivers_licence ? 'var(--text-primary)' : 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{p.drivers_licence || 'Not verified'}</div>
            )}
          </div>
        </div>
      </Section>

      <div style={{ padding: 'var(--space-3)', background: 'var(--accent-subtle)', border: '1px solid var(--border-muted)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-xs)', color: 'var(--accent-fg)' }}>
        🔒 BOB never invents qualifications, experience, results, references, licences, skills, or personal information. All profile data is sourced directly from you and your verified documents.
      </div>
    </div>
  )
}
