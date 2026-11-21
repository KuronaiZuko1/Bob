import React, { useRef, useContext, useState } from 'react'
import { useDocuments } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

const CATEGORY_ICONS = {
  id_document:     '🪪',
  matric:          '🎓',
  certificate:     '📜',
  transcript:      '📄',
  cv:              '📋',
  cover_letter:    '✉️',
  proof_of_residence: '🏠',
  other:           '📎',
}

function DocumentCard({ doc, onDelete }) {
  const addToast = useContext(ToastContext)

  async function handleDelete() {
    if (!window.confirm(`Delete "${doc.original_filename}"? This cannot be undone.`)) return
    try {
      await client.delete(`/api/documents/${doc.id}`)
      addToast('Document deleted', 'success')
      onDelete()
    } catch (e) {
      addToast(`Delete failed: ${e.message}`, 'error')
    }
  }

  return (
    <div className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', padding: 'var(--space-4)' }}>
      <div style={{ fontSize: 28, lineHeight: 1 }}>{CATEGORY_ICONS[doc.category] || '📎'}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 'var(--font-size-sm)', marginBottom: 2 }}>{doc.original_filename}</div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          {doc.category?.replace('_', ' ')} · {doc.mime_type} · {(doc.file_size / 1024).toFixed(1)} KB
        </div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
          Uploaded {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString('en-ZA') : '—'}
          {doc.is_verified && <span style={{ color: 'var(--success)', marginLeft: 8 }}>✓ Verified</span>}
        </div>
      </div>
      <button className="btn btn-secondary btn-sm" onClick={handleDelete} style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}>Delete</button>
    </div>
  )
}

export default function Documents() {
  const { data, loading, error, refetch } = useDocuments()
  const addToast = useContext(ToastContext)
  const fileRef  = useRef()
  const [uploading, setUploading] = useState(false)
  const [category, setCategory]   = useState('other')

  const documents = data?.documents || data || []

  async function handleUpload(e) {
    const files = [...e.target.files]
    if (!files.length) return
    setUploading(true)
    for (const file of files) {
      try {
        const form = new FormData()
        form.append('file', file)
        form.append('category', category)
        await client.post('/api/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        addToast(`"${file.name}" uploaded successfully`, 'success')
      } catch (err) {
        addToast(`Upload failed for "${file.name}": ${err.message}`, 'error')
      }
    }
    setUploading(false)
    fileRef.current.value = ''
    refetch()
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Document Vault</div>
          <div className="section-subtitle">Securely stored documents — encrypted at rest. BOB uses these for applications.</div>
        </div>
      </div>

      {/* Upload area */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Upload Document</div>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center', flexWrap: 'wrap' }}>
          <select className="form-select" value={category} onChange={e => setCategory(e.target.value)} style={{ width: 220 }}>
            <option value="id_document">South African ID</option>
            <option value="matric">Matric Certificate</option>
            <option value="certificate">College Certificate</option>
            <option value="transcript">Academic Transcript</option>
            <option value="cv">CV</option>
            <option value="cover_letter">Cover Letter</option>
            <option value="proof_of_residence">Proof of Residence</option>
            <option value="other">Other</option>
          </select>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" multiple style={{ display: 'none' }} onChange={handleUpload} />
          <button className="btn btn-primary" onClick={() => fileRef.current.click()} disabled={uploading}>
            {uploading ? 'Uploading…' : '↑ Upload File'}
          </button>
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>PDF, DOCX, JPG, PNG accepted</span>
        </div>
        <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          🔒 All files are encrypted before storage. Original files are never modified.
        </div>
      </div>

      {loading && <div className="loading-state"><div className="spinner" /><span>Loading documents…</span></div>}
      {error   && <div className="empty-state">⚠️ {error}</div>}

      {!loading && documents.length === 0 && (
        <div className="empty-state">
          <div style={{ fontSize: 32 }}>📁</div>
          <div>No documents uploaded. Upload your Matric certificate, ID, or other qualifications to get started.</div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {documents.map((doc) => (
          <DocumentCard key={doc.id} doc={doc} onDelete={refetch} />
        ))}
      </div>
    </div>
  )
}
