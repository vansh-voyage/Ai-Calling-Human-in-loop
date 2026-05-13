import type { RequestStatus } from '../types'

const COLORS: Record<RequestStatus, string> = {
  pending: '#b45309',
  resolved: '#15803d',
  unresolved: '#b91c1c',
}

const BG: Record<RequestStatus, string> = {
  pending: '#fef9c3',
  resolved: '#dcfce7',
  unresolved: '#fee2e2',
}

export function StatusBadge({ status }: { status: RequestStatus }) {
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: COLORS[status],
        backgroundColor: BG[status],
        border: `1px solid ${COLORS[status]}40`,
      }}
    >
      {status}
    </span>
  )
}
