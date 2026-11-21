import React, { useContext, useState } from 'react'
import { useSettings } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

export default function AIConfig() {
  const { data, loading, refetch } = useSettings()
  const addToast = useContext(ToastContext)
  const [saving, setSaving] = useState(false)
  const [form, setForm]     = useState({})
  const [testResult, setTestResult] = useState(null)
  const [testing, setTesting]       = useState(false)

  const cfg = data?.ai || {}

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function save() {
    setSaving(true)
    try {
      await client.put('/api/settings', { ai: { ...cfg, ...form } })
      addToast('AI settings saved', 'success')
      refetch()
      setForm({})
    } catch (e) {
      addToast(`Save failed: ${e.message}`, 'error')
    } finally { setSaving(false) }
  }

  async function testConnection() {
    setTesting(true)
    setTestResult(null)
    try {
      const res = await client.post('/api/settings/test-ai')
      setTestResult({ ok: true, msg: res.data?.message || 'Connection successful' })
    } catch (e) {
      setTestResult({ ok: false, msg: e.message })
    } finally { setTesting(false) }
  }

  const merged = { ...cfg, ...form }

  if (loading) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /></div></div>

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">AI Configuration</div>
          <div className="section-subtitle">Configure local Ollama or optional OpenAI-compatible provider</div>
        </div>
        <div className="topbar-actions">
          <button className="btn btn-secondary" onClick={testConnection} disabled={testing}>{testing ? 'Testing…' : 'Test Connection'}</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </div>

      {testResult && (
        <div className={`card`} style={{ marginBottom: 'var(--space-4)', borderColor: testResult.ok ? 'var(--success)' : 'var(--danger)', background: testResult.ok ? 'var(--success-subtle)' : 'var(--danger-subtle)' }}>
          {testResult.ok ? '✓' : '✗'} {testResult.msg}
        </div>
      )}

      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">AI Provider</div>
        <div className="form-group">
          <label className="form-label">Provider</label>
          <select className="form-select" value={merged.provider || 'ollama'} onChange={e => set('provider', e.target.value)}>
            <option value="ollama">Ollama (Local — Free, Recommended)</option>
            <option value="openai">OpenAI-compatible API</option>
          </select>
          <div className="form-hint">Ollama runs entirely on your machine. No API key required.</div>
        </div>

        {(merged.provider === 'ollama' || !merged.provider) && (
          <>
            <div className="form-group">
              <label className="form-label">Ollama Host</label>
              <input className="form-input" value={merged.ollama_host || 'http://localhost:11434'} onChange={e => set('ollama_host', e.target.value)} placeholder="http://localhost:11434" />
            </div>
            <div className="form-group">
              <label className="form-label">Model</label>
              <input className="form-input" value={merged.ollama_model || 'llama3.2'} onChange={e => set('ollama_model', e.target.value)} placeholder="llama3.2" />
              <div className="form-hint">Run <code>ollama pull llama3.2</code> to download. Llama 3.2 3B is recommended for low-resource machines.</div>
            </div>
          </>
        )}

        {merged.provider === 'openai' && (
          <>
            <div className="form-group">
              <label className="form-label">API Base URL</label>
              <input className="form-input" value={merged.openai_base_url || 'https://api.openai.com/v1'} onChange={e => set('openai_base_url', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Model</label>
              <input className="form-input" value={merged.openai_model || 'gpt-4o-mini'} onChange={e => set('openai_model', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">API Key</label>
              <input className="form-input" type="password" value={merged.openai_api_key || ''} onChange={e => set('openai_api_key', e.target.value)} placeholder="sk-…" />
              <div className="form-hint">Stored in your local .env file. Never transmitted except to the configured API endpoint.</div>
            </div>
          </>
        )}
      </div>

      <div className="card">
        <div className="card-title">AI Safety Rules</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            ['Never invent qualifications, experience, or references', true],
            ['Reject AI outputs that contain invented facts', true],
            ['Treat vacancy content as untrusted (prompt injection protection)', true],
            ['Require structured JSON responses for eligibility decisions', true],
            ['Log all AI decisions with evidence', true],
          ].map(([rule, enforced]) => (
            <div key={rule} style={{ display: 'flex', gap: 10, alignItems: 'center', fontSize: 'var(--font-size-sm)' }}>
              <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
              <span style={{ color: enforced ? 'var(--text-secondary)' : 'var(--text-muted)' }}>{rule}</span>
              <span className="badge badge-eligible" style={{ marginLeft: 'auto' }}>Enforced</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
