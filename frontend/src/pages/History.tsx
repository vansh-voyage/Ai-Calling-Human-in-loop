import { useState } from 'react'
import { useHelpRequests } from '../hooks/useHelpRequests'
import { RequestList } from '../components/RequestList'
import type { RequestStatus } from '../types'

const TABS: { label: string; status: RequestStatus }[] = [
  { label: 'Resolved', status: 'resolved' },
  { label: 'Unresolved', status: 'unresolved' },
]

export function History() {
  const [activeTab, setActiveTab] = useState<RequestStatus>('resolved')
  const { requests, isLoading, total } = useHelpRequests(activeTab, 100)

  return (
    <div>
      <h1 style={{ margin: '0 0 20px', fontSize: 22, fontWeight: 700 }}>Request History</h1>

      <div style={{ display: 'flex', gap: 0, marginBottom: 20, borderBottom: '2px solid #e5e7eb' }}>
        {TABS.map((tab) => (
          <button
            key={tab.status}
            onClick={() => setActiveTab(tab.status)}
            style={{
              padding: '8px 20px',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              fontWeight: activeTab === tab.status ? 700 : 400,
              color: activeTab === tab.status ? '#1d4ed8' : '#374151',
              borderBottom:
                activeTab === tab.status ? '2px solid #1d4ed8' : '2px solid transparent',
              marginBottom: -2,
              fontSize: 14,
            }}
          >
            {tab.label}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', alignSelf: 'center', fontSize: 13, color: '#6b7280' }}>
          {total} total
        </span>
      </div>

      <RequestList
        requests={requests}
        isLoading={isLoading}
        emptyText={`No ${activeTab} requests yet.`}
      />
    </div>
  )
}
