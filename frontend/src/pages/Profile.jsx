import React, { useState, useContext } from 'react'
import { useProfile } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

function Section({ title, actions, children }) {
  return (
    <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
        <div className="card-title" style={{ margin: 0 }}>{title}</div>
        {actions}
      </div>
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

  // Sub-items forms
  const [showAddQual, setShowAddQual] = useState(false)
  const [qualForm, setQualForm] = useState({ qualification_name: '', institution: '', end_year: '', field_of_study: 'Marketing / Business' })

  const [showAddSkill, setShowAddSkill] = useState(false)
  const [skillForm, setSkillForm] = useState({ name: '', category: 'Technical', proficiency: 'Intermediate' })

  function startEdit() {
    setForm({
      full_legal_name: profile.full_legal_name || profile.full_name || '',
      email: profile.email || '',
      phone_number: profile.phone_number || profile.phone || '',
      id_number: profile.id_number || '',
      province: profile.province || 'Gauteng',
      town_city: profile.town_city || profile.city || '',
      residential_address: profile.residential_address || profile.address || '',
      languages: profile.languages || 'English',
      drivers_licence: profile.drivers_licence || 'None',
      has_own_transport: profile.has_own_transport || false
    })
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

  async function handleAddQualification(e) {
    e.preventDefault()
    if (!qualForm.qualification_name.trim()) return
    try {
      await client.post('/api/profile/qualifications', qualForm)
      addToast(`Qualification "${qualForm.qualification_name}" added`, 'success')
      setQualForm({ qualification_name: '', institution: '', end_year: '', field_of_study: '' })
      setShowAddQual(false)
      refetch()
    } catch (err) {
      addToast(`Failed: ${err.message}`, 'error')
    }
  }

  async function handleDeleteQualification(id) {
    if (!window.confirm('Delete this qualification?')) return
    try {
      await client.delete(`/api/profile/qualifications/${id}`)
      addToast('Qualification deleted', 'success')
      refetch()
    } catch (err) {
      addToast(`Delete failed: ${err.message}`, 'error')
    }
  }

  async function handleAddSkill(e) {
    e.preventDefault()
    if (!skillForm.name.trim()) return
    try {
      await client.post('/api/profile/skills', skillForm)
      addToast(`Skill "${skillForm.name}" added`, 'success')
      setSkillForm({ name: '', category: 'Technical', proficiency: 'Intermediate' })
      setShowAddSkill(false)
      refetch()
    } catch (err) {
      addToast(`Failed: ${err.message}`, 'error')
    }
  }

  async function handleDeleteSkill(id) {
    try {
      await client.delete(`/api/profile/skills/${id}`)
      addToast('Skill deleted', 'success')
      refetch()
    } catch (err) {
      addToast(`Delete failed: ${err.message}`, 'error')
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
          <div className="section-subtitle">Your real verified employment profile. BOB strictly uses this data — zero hallucinated facts.</div>
        </div>
        <div className="topbar-actions">
          {!editing
            ? <button className="btn btn-primary" onClick={startEdit}>Edit Personal Info</button>
            : <>
                <button className="btn btn-secondary" onClick={cancelEdit} disabled={saving}>Cancel</button>
                <button className="btn btn-primary" onClick={saveProfile} disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button>
              </>
          }
        </div>
      </div>

      {/* Personal Information */}
      <Section title="Personal Information">
        {editing ? (
          <div className="two-col" style={{ gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Full Legal Name *</label>
              <input className="form-input" value={form.full_legal_name} onChange={e => set('full_legal_name', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Email Address *</label>
              <input className="form-input" type="email" value={form.email} onChange={e => set('email', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input className="form-input" value={form.phone_number} onChange={e => set('phone_number', e.target.value)} placeholder="+27 82 123 4567" />
            </div>
            <div className="form-group">
              <label className="form-label">South African ID Number</label>
              <input className="form-input" value={form.id_number} onChange={e => set('id_number', e.target.value)} placeholder="13-digit SA ID" />
            </div>
            <div className="form-group">
              <label className="form-label">Province</label>
              <select className="form-select" value={form.province} onChange={e => set('province', e.target.value)}>
                {['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Free State', 'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape'].map(prov => (
                  <option key={prov} value={prov}>{prov}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">City / Town</label>
              <input className="form-input" value={form.town_city} onChange={e => set('town_city', e.target.value)} placeholder="e.g. Johannesburg" />
            </div>
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label">Residential Address</label>
              <input className="form-input" value={form.residential_address} onChange={e => set('residential_address', e.target.value)} placeholder="Street address, suburb" />
            </div>
            <div className="form-group">
              <label className="form-label">Languages</label>
              <input className="form-input" value={form.languages} onChange={e => set('languages', e.target.value)} placeholder="English, isiZulu, etc." />
            </div>
            <div className="form-group">
              <label className="form-label">Driver's Licence</label>
              <select className="form-select" value={form.drivers_licence} onChange={e => set('drivers_licence', e.target.value)}>
                <option value="None">None</option>
                <option value="Code B">Code B / Code 08 (Light vehicle)</option>
                <option value="Code C">Code C / Code 10 (Heavy vehicle)</option>
                <option value="Code EC">Code EC / Code 14 (Extra heavy)</option>
              </select>
            </div>
          </div>
        ) : (
          <div className="two-col">
            <Field label="Full Legal Name"     value={p.full_legal_name || p.full_name} />
            <Field label="Email Address"       value={p.email} />
            <Field label="Phone Number"        value={p.phone_number || p.phone} />
            <Field label="SA ID Number"        value={p.id_number ? (p.id_number.length === 13 ? '••••••••••' + p.id_number.slice(-3) : p.id_number) : null} hint="Encrypted at rest" />
            <Field label="Province"            value={p.province} />
            <Field label="City / Town"         value={p.town_city || p.city} />
            <Field label="Residential Address" value={p.residential_address || p.address} />
            <Field label="Languages"           value={p.languages} />
            <Field label="Driver's Licence"    value={p.drivers_licence} />
          </div>
        )}
      </Section>

      {/* Qualifications */}
      <Section
        title="Qualifications &amp; Education"
        actions={
          <button className="btn btn-secondary btn-sm" onClick={() => setShowAddQual(v => !v)}>
            {showAddQual ? 'Cancel' : '+ Add Qualification'}
          </button>
        }
      >
        {showAddQual && (
          <form onSubmit={handleAddQualification} style={{ marginBottom: 16, padding: 12, background: 'var(--bg-active)', borderRadius: 'var(--radius-md)' }}>
            <div className="two-col" style={{ gap: 10 }}>
              <div className="form-group">
                <label className="form-label">Qualification Name *</label>
                <input className="form-input" required value={qualForm.qualification_name} onChange={e => setQualForm(f => ({ ...f, qualification_name: e.target.value }))} placeholder="e.g. Marketing Management N5" />
              </div>
              <div className="form-group">
                <label className="form-label">Institution</label>
                <input className="form-input" value={qualForm.institution} onChange={e => setQualForm(f => ({ ...f, institution: e.target.value }))} placeholder="e.g. TVET College / High School" />
              </div>
              <div className="form-group">
                <label className="form-label">Year Completed</label>
                <input className="form-input" value={qualForm.end_year} onChange={e => setQualForm(f => ({ ...f, end_year: e.target.value }))} placeholder="e.g. 2024" />
              </div>
              <div className="form-group">
                <label className="form-label">Field of Study</label>
                <input className="form-input" value={qualForm.field_of_study} onChange={e => setQualForm(f => ({ ...f, field_of_study: e.target.value }))} placeholder="e.g. Marketing Management" />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-sm" style={{ marginTop: 8 }}>Save Qualification</button>
          </form>
        )}

        {p.qualifications && p.qualifications.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Qualification</th><th>Institution</th><th>Year</th><th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>
              {p.qualifications.map((q) => (
                <tr key={q.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{q.qualification_name || q.name}</td>
                  <td>{q.institution || '—'}</td>
                  <td>{q.end_year || q.year_obtained || '—'}</td>
                  <td><span className="badge badge-eligible">{q.is_verified ? 'Verified' : 'Active'}</span></td>
                  <td style={{ textAlign: 'right' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => handleDeleteQualification(q.id)} style={{ color: 'var(--danger)' }}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-4)' }}>No qualifications listed. Add your Matric and N-Level certificates above.</div>
        )}
      </Section>

      {/* Skills */}
      <Section
        title="Skills &amp; Competencies"
        actions={
          <button className="btn btn-secondary btn-sm" onClick={() => setShowAddSkill(v => !v)}>
            {showAddSkill ? 'Cancel' : '+ Add Skill'}
          </button>
        }
      >
        {showAddSkill && (
          <form onSubmit={handleAddSkill} style={{ marginBottom: 16, padding: 12, background: 'var(--bg-active)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div className="form-group" style={{ flex: 1, minWidth: 180 }}>
                <label className="form-label">Skill Name *</label>
                <input className="form-input" required value={skillForm.name} onChange={e => setSkillForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. MS Excel, Copywriting" />
              </div>
              <div className="form-group" style={{ width: 140 }}>
                <label className="form-label">Proficiency</label>
                <select className="form-select" value={skillForm.proficiency} onChange={e => setSkillForm(f => ({ ...f, proficiency: e.target.value }))}>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Proficient">Proficient</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary btn-sm" style={{ height: 38 }}>Add Skill</button>
            </div>
          </form>
        )}

        {p.skills && p.skills.length > 0 ? (
          <div className="tag-list">
            {p.skills.map((s) => (
              <span key={s.id} className="tag" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                {s.name} ({s.proficiency || s.proficiency_level})
                <button
                  onClick={() => handleDeleteSkill(s.id)}
                  style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: 0, fontSize: 12 }}
                  title="Remove skill"
                >
                  ✕
                </button>
              </span>
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
              {e.responsibilities && <div style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{e.responsibilities}</div>}
            </div>
          ))
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-3)' }}>
            No formal employment history recorded. BOB will highlight your academic training and practical coursework truthfully.
          </div>
        )}
      </Section>
    </div>
  )
}
