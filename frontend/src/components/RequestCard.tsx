import { AnswerForm } from './AnswerForm'
import { StatusBadge } from './StatusBadge'
import type { HelpRequest } from '../types'

function formatRelative(isoString: string): string {
  const diff = Date.now() - new Date(isoString + 'Z').getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

interface Props {
  request: HelpRequest
  showAnswerForm?: boolean
  onResolved?: () => void
}

export function RequestCard({ request, showAnswerForm = false, onResolved }: Props) {
  const callerLabel = request.caller_name
    ? `${request.caller_name} (${request.caller_id})`
    : request.caller_id

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: 8,
        padding: '14px 16px',
        marginBottom: 12,
        background: '#fff',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <StatusBadge status={request.status} />
          <span style={{ marginLeft: 10, fontSize: 12, color: '#6b7280' }}>
            #{request.id} · {formatRelative(request.created_at)}
          </span>
        </div>
        {request.timeout_at && request.status === 'pending' && (
          <span style={{ fontSize: 11, color: '#9ca3af' }}>
            Timeout: {new Date(request.timeout_at + 'Z').toLocaleString()}
          </span>
        )}
      </div>

      <p style={{ margin: '10px 0 4px', fontWeight: 600, fontSize: 15 }}>
        &ldquo;{request.question}&rdquo;
      </p>
      <p style={{ margin: 0, fontSize: 13, color: '#374151' }}>
        <strong>Caller:</strong> {callerLabel}
      </p>

      {request.answer && (
        <div
          style={{
            marginTop: 10,
            padding: '8px 12px',
            background: '#f0fdf4',
            borderRadius: 6,
            fontSize: 13,
            color: '#166534',
          }}
        >
          <strong>Answer:</strong> {request.answer}
          {request.answered_by && (
            <span style={{ color: '#6b7280', marginLeft: 8 }}>— {request.answered_by}</span>
          )}
        </div>
      )}

      {showAnswerForm && request.status === 'pending' && onResolved && (
        <AnswerForm requestId={request.id} onResolved={onResolved} />
      )}
    </div>
  )
}
