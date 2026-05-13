import { useState } from 'react'
import { api } from '../api/client'
import type { KnowledgeEntry } from '../types'

interface Props {
  entries: KnowledgeEntry[]
  onChanged: () => void
}

export function KnowledgeTable({ entries, onChanged }: Props) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const [saving, setSaving] = useState(false)

  function startEdit(entry: KnowledgeEntry) {
    setEditingId(entry.id)
    setEditValue(entry.answer)
  }

  async function saveEdit(id: number) {
    setSaving(true)
    try {
      await api.put(`/knowledge/${id}`, { answer: editValue.trim() })
      setEditingId(null)
      onChanged()
    } finally {
      setSaving(false)
    }
  }

  async function deleteEntry(id: number) {
    if (!confirm('Remove this knowledge entry?')) return
    await api.delete(`/knowledge/${id}`)
    onChanged()
  }

  if (entries.length === 0) {
    return (
      <div
        style={{
          padding: '32px 0',
          textAlign: 'center',
          color: '#9ca3af',
          border: '1px dashed #d1d5db',
          borderRadius: 8,
        }}
      >
        No learned answers yet. Resolve a pending request to add the first one.
      </div>
    )
  }

  const tdStyle: React.CSSProperties = {
    padding: '10px 12px',
    borderBottom: '1px solid #f3f4f6',
    verticalAlign: 'top',
    fontSize: 13,
  }

  const thStyle: React.CSSProperties = {
    ...tdStyle,
    fontWeight: 600,
    background: '#f9fafb',
    color: '#374151',
    textAlign: 'left',
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={{ ...thStyle, width: '28%' }}>Question</th>
            <th style={{ ...thStyle, width: '36%' }}>Answer</th>
            <th style={{ ...thStyle, width: '10%' }}>Source</th>
            <th style={{ ...thStyle, width: '8%', textAlign: 'center' }}>Served</th>
            <th style={{ ...thStyle, width: '12%' }}>Saved</th>
            <th style={{ ...thStyle, width: '6%' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id} style={{ background: '#fff' }}>
              <td style={tdStyle}>{entry.question_display}</td>
              <td style={tdStyle}>
                {editingId === entry.id ? (
                  <div>
                    <textarea
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      rows={3}
                      style={{ width: '100%', boxSizing: 'border-box', fontSize: 13, padding: 6 }}
                    />
                    <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                      <button
                        onClick={() => saveEdit(entry.id)}
                        disabled={saving}
                        style={{ fontSize: 12, padding: '3px 10px', cursor: 'pointer' }}
                      >
                        {saving ? 'Saving…' : 'Save'}
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        style={{ fontSize: 12, padding: '3px 10px', cursor: 'pointer' }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  entry.answer
                )}
              </td>
              <td style={{ ...tdStyle, color: entry.source === 'supervisor' ? '#1d4ed8' : '#6b7280' }}>
                {entry.source}
              </td>
              <td style={{ ...tdStyle, textAlign: 'center' }}>{entry.lookup_count}</td>
              <td style={{ ...tdStyle, color: '#6b7280' }}>
                {new Date(entry.created_at + 'Z').toLocaleDateString()}
              </td>
              <td style={tdStyle}>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button
                    onClick={() => startEdit(entry)}
                    style={{ fontSize: 11, padding: '2px 8px', cursor: 'pointer' }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteEntry(entry.id)}
                    style={{
                      fontSize: 11,
                      padding: '2px 8px',
                      cursor: 'pointer',
                      color: '#b91c1c',
                      background: 'none',
                      border: '1px solid #fca5a5',
                      borderRadius: 4,
                    }}
                  >
                    Del
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
