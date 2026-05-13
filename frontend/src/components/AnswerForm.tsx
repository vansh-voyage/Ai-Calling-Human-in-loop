import { useState } from 'react'
import { api } from '../api/client'

interface Props {
  requestId: number
  onResolved: () => void
}

export function AnswerForm({ requestId, onResolved }: Props) {
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const MIN = 5
  const canSubmit = answer.trim().length >= MIN && !submitting

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await api.patch(`/help-requests/${requestId}/resolve`, { answer: answer.trim() })
      setSuccess(true)
      setTimeout(onResolved, 800)
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to submit answer. Please try again.'
      setError(msg)
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <p style={{ color: '#15803d', fontWeight: 600, margin: '8px 0 0' }}>
        Answer sent and caller notified.
      </p>
    )
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 10 }}>
      <textarea
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer here…"
        rows={3}
        disabled={submitting}
        style={{
          width: '100%',
          boxSizing: 'border-box',
          padding: '8px 10px',
          fontFamily: 'inherit',
          fontSize: 14,
          border: '1px solid #d1d5db',
          borderRadius: 6,
          resize: 'vertical',
        }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
        <span style={{ fontSize: 12, color: '#6b7280' }}>
          {answer.trim().length} chars (min {MIN})
        </span>
        <button
          type="submit"
          disabled={!canSubmit}
          style={{
            padding: '6px 16px',
            background: canSubmit ? '#1d4ed8' : '#9ca3af',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            cursor: canSubmit ? 'pointer' : 'not-allowed',
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          {submitting ? 'Sending…' : 'Submit Answer'}
        </button>
      </div>
      {error && <p style={{ color: '#b91c1c', fontSize: 13, marginTop: 4 }}>{error}</p>}
    </form>
  )
}
