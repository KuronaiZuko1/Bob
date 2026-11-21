import React, { useContext, useState, useEffect } from 'react'
import { useSettings } from '../hooks/useApi'
import { ToastContext } from '../App'
import client from '../api/client'

export default function AIConfig() {
  const { data, loading, refetch } = useSettings()
  const addToast = useContext(ToastContext)
  const [saving, setSaving] = useState(false)
  const [form, setForm]     = useState({
    provider: 'ollama',
    ollama_host: 'http://localhost:11434',
    ollama_model: 'llama3.2',
    openai_base_url: 'https://api.openai.com/v1',
    openai_model: 'gpt-4o-mini',
    openai_api_key: ''
  })
  const [testResult, setTestResult] = useState(null)
  const [testing, setTesting]       = useState(false)

  useEffect(() => {
    if (data) {
      setForm(f => ({
        ...f,
        provider: data.ai_provider || 'ollama',
        ollama_host: data.ollama_base_url || 'http://localhost:11434',
        ollama_model: data.ollama_model || 'llama3.2',
      }))
    }
  }, [data])

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function save() {
    setSaving(true)
    try {
      await client.put('/api/settings', {
        ai: {
          provider: form.provider,
          ollama_host: form.ollama_host,
          ollama_model: form.ollama_model,
          openai_api_key: form.openai_api_key,
          openai_model: form.openai_model
        }
      })
      addToast('AI configuration saved successfully', 'success')
      refetch()
    } catch (e) {
      addToast(`Save failed: ${e.message}`, 'error')
    } finally {
      setSaving(false)
    }
  }

  async function testConnection() {
    setTesting(true)
    setTestResult(null)
    try {
      const res = await client.post('/api/settings/test-ai')
      setTestResult({ ok: res.data?.ok, msg: res.data?.message || 'Connection verified!' })
    } catch (e) {
      setTestResult({ ok: false, msg: e.message })
    } finally {
      setTesting(false)
    }
  }

  if (loading) return <div className="page-scroll"><div className="loading-state"><div className="spinner" /></div></div>

  return (
    <div className="page-scroll">
      <div className="section-header">
        <div>
          <div className="section-title">AI Engine Configuration</div>
          <div className="section-subtitle">Configure local Ollama, OpenAI-compatible provider, or built-in deterministic engine</div>
        </div>
        <div className="topbar-actions">
          <button className="btn btn-secondary" onClick={testConnection} disabled={testing}>
            {testing ? 'Testing…' : '🧪 Test AI Connection'}
          </button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? 'Saving…' : 'Save AI Settings'}
          </button>
        </div>
      </div>

      {testResult && (
        <div className="card" style={{
          marginBottom: 'var(--space-4)',
          borderColor: testResult.ok ? 'var(--success)' : 'var(--danger)',
          background: testResult.ok ? 'var(--success-subtle)' : 'var(--danger-subtle)',
          color: testResult.ok ? 'var(--success)' : 'var(--danger)',
          fontSize: 'var(--font-size-sm)'
        }}>
          {testResult.ok ? '✓' : '✗'} {testResult.msg}
        </div>
      )}

      <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="card-title">Active AI Provider</div>
        <div className="form-group">
          <label className="form-label">Engine Provider</label>
          <select className="form-select" value={form.provider} onChange={e => set('provider', e.target.value)}>
            <option value="ollama">Ollama (Local AI — Free, Private &amp; Zero Cost)</option>
            <option value="openai">OpenAI-compatible Cloud API</option>
          </select>
          <div className="form-hint">BOB never requires paid cloud APIs. If Ollama is offline, BOB automatically uses his built-in South African deterministic eligibility rules.</div>
        </div>

        {form.provider === 'ollama' && (
          <div className="two-col" style={{ gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Ollama Host URL</label>
              <input className="form-input" value={form.ollama_host} onChange={e => set('ollama_host', e.target.value)} placeholder="http://localhost:11434" />
            </div>
            <div className="form-group">
              <label className="form-label">Model Name</label>
              <input className="form-input" value={form.ollama_model} onChange={e => set('ollama_model', e.target.value)} placeholder="llama3.2" />
              <div className="form-hint">Recommended: <code>llama3.2</code> or <code>mistral</code></div>
            </div>
          </div>
        )}

        {form.provider === 'openai' && (
          <>
            <div className="form-group">
              <label className="form-label">API Base URL</label>
              <input className="form-input" value={form.openai_base_url} onChange={e => set('openai_base_url', e.target.value)} />
            </div>
            <div className="two-col" style={{ gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Model Name</label>
                <input className="form-input" value={form.openai_model} onChange={e => set('openai_model', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">API Key</label>
                <input className="form-input" type="password" value={form.openai_api_key} onChange={e => set('openai_api_key', e.target.value)} placeholder="sk-…" />
              </div>
            </div>
          </>
        )}
      </div>

      <div className="card">
        <div className="card-title">Zero-Hallucination Guardrails (Enforced)</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            'Never invent qualifications, diplomas, degrees, or results',
            'Never invent employment history or fabricated responsibilities',
            'Never invent professional references or contact numbers',
            'Treat all vacancy text as untrusted (Prompt injection neutralized)',
            'Require structured JSON validation for all eligibility decisions',
          ].map((rule) => (
            <div key={rule} style={{ display: 'flex', gap: 10, alignItems: 'center', fontSize: 'var(--font-size-sm)' }}>
              <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
              <span style={{ color: 'var(--text-secondary)' }}>{rule}</span>
              <span className="badge badge-eligible" style={{ marginLeft: 'auto' }}>Active</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
