import { useHelpRequests, useStats } from '../hooks/useHelpRequests'
import { RequestList } from '../components/RequestList'

export function Dashboard() {
  const { stats } = useStats()
  const { requests, isLoading, mutate } = useHelpRequests('pending')

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Pending Questions</h1>
        {stats && (
          <span
            style={{
              background: stats.pending > 0 ? '#fef9c3' : '#f3f4f6',
              color: stats.pending > 0 ? '#92400e' : '#6b7280',
              borderRadius: 12,
              padding: '2px 12px',
              fontWeight: 700,
              fontSize: 14,
            }}
          >
            {stats.pending} pending
          </span>
        )}
      </div>

      {stats && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          {(['pending', 'resolved', 'unresolved'] as const).map((s) => (
            <div
              key={s}
              style={{
                flex: 1,
                background: '#f9fafb',
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                padding: '12px 16px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: 24, fontWeight: 700 }}>{stats[s]}</div>
              <div style={{ fontSize: 12, color: '#6b7280', textTransform: 'capitalize' }}>{s}</div>
            </div>
          ))}
        </div>
      )}

      <RequestList
        requests={requests}
        isLoading={isLoading}
        showAnswerForm
        onResolved={mutate}
        emptyText="No pending questions — all caught up!"
      />
    </div>
  )
}
