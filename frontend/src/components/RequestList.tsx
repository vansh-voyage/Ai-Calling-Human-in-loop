import { RequestCard } from './RequestCard'
import type { HelpRequest } from '../types'

interface Props {
  requests: HelpRequest[]
  isLoading: boolean
  showAnswerForm?: boolean
  onResolved?: () => void
  emptyText?: string
}

export function RequestList({
  requests,
  isLoading,
  showAnswerForm = false,
  onResolved,
  emptyText = 'No requests found.',
}: Props) {
  if (isLoading) {
    return <p style={{ color: '#6b7280', padding: '20px 0' }}>Loading…</p>
  }

  if (requests.length === 0) {
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
        {emptyText}
      </div>
    )
  }

  return (
    <div>
      {requests.map((r) => (
        <RequestCard
          key={r.id}
          request={r}
          showAnswerForm={showAnswerForm}
          onResolved={onResolved}
        />
      ))}
    </div>
  )
}
