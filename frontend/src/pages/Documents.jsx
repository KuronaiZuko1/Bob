import React, { useRef, useContext, useState } from 'react'
import { useDocuments } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

const CATEGORY_ICONS = {
  id_document:        '🪪',
  matric:             '🎓',
  certificate:        '📜',
  transcript:         '📄',
  cv:                 '📋',
  cover_letter:       '✉️',
  proof_of_residence: '🏠',
  other:              '📎',
}

function DocumentCard({ doc, onDelete }) {
  const addToast = useContext(ToastContext)

  async function handleDelete() {
    if (!window.confirm(`Permanently delete "${doc.original_filename}"? This will securely wipe the encrypted file.`)) return
    try {
      await client.delete(`/api/documents/${doc.id}`)
      addToast('Document securely deleted', 'success')
      onDelete()
    } catch (e) {
      addToast(`Delete failed: ${e.message}`, 'error')
    }
  }

  function handlePreview() {
    window.open(`http://localhost:8000/api/documents/${doc.id}/preview`, '_blank')
  }

  return (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', padding: 'var(--space-4)' }}>
      <div style={{ fontSize: 32, lineHeight: 1 }}>{CATEGORY_ICONS[doc.category] || '📎'}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 'var(--font-size-sm)', marginBottom: 2 }}>
          {doc.original_filename}
        </div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          {doc.category?.replace('_', ' ').toUpperCase()} · {doc.mime_type} · {(doc.file_size / 1024).toFixed(1)} KB
        </div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: 2 }}>
          Uploaded {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString('en-ZA') : '—'}
          {doc.is_verified && <span style={{ color: 'var(--success)', marginLeft: 8 }}>✓ Verified</span>}
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button className="btn btn-secondary btn-sm" onClick={handlePreview}>
          Preview / Download
        </button>
        <button
          className="btn btn-secondary btn-sm"
          onClick={handleDelete}
          style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}
        >
          Delete
        </button>
      </div>
    </div>
  )
}

export default function Documents() {
  const { data, loading, error, refetch } = useDocuments()
  const addToast = useContext(ToastContext)
  const fileRef  = useRef()
  const [uploading, setUploading] = useState(false)
  const [category, setCategory]   = useState('matric')

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
        addToast(`"${file.name}" encrypted and stored in vault`, 'success')
      } catch (err) {
        addToast(`Upload failed for "${file.name}": ${err.message}`, 'error')
      }
    }
    setUploading(false)
    if (fileRef.current) fileRef.current.value = ''
    refetch()
  }

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">Document Vault</div>
          <div className="section-subtitle">Real document storage — encrypted at rest using AES-128 Fernet encryption.</div>
        </div>
      </div>

      {/* Upload area */}
      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Upload Real Supporting Document</div>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center', flexWrap: 'wrap' }}>
          <select className="form-select" value={category} onChange={e => setCategory(e.target.value)} style={{ width: 220 }}>
            <option value="matric">Matric Certificate</option>
            <option value="certificate">College / N5 Certificate</option>
            <option value="id_document">South African ID Document</option>
            <option value="transcript">Academic Transcript</option>
            <option value="cv">Master CV</option>
            <option value="proof_of_residence">Proof of Residence</option>
            <option value="other">Other Supporting Document</option>
          </select>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" multiple style={{ display: 'none' }} onChange={handleUpload} />
          <button className="btn btn-primary" onClick={() => fileRef.current.click()} disabled={uploading}>
            {uploading ? 'Encrypting & Storing…' : '↑ Upload Document'}
          </button>
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>PDF, DOCX, JPG, PNG accepted (Max 15MB)</span>
        </div>
        <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
          🔒 Files are encrypted with Fernet AES-128 before writing to disk. South African ID numbers are automatically masked in all notification logs.
        </div>
      </div>

      {loading && <div className="loading-state"><div className="spinner" /><span>Loading document vault…</span></div>}
      {error   && <div className="empty-state">⚠️ {error}</div>}

      {!loading && documents.length === 0 && (
        <div className="empty-state">
          <div style={{ fontSize: 32 }}>📁</div>
          <div>Vault is currently empty. Upload your Matric Certificate and Marketing N5 Certificate above.</div>
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
