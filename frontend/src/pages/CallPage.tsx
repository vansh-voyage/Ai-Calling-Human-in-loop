import {
  LiveKitRoom,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
} from '@livekit/components-react'
import '@livekit/components-styles'
import axios from 'axios'
import { useState } from 'react'

interface TokenResponse {
  token: string
  url: string
}

export function CallPage() {
  const [session, setSession] = useState<TokenResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startCall = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.get<TokenResponse>('/api/v1/livekit/token')
      setSession(data)
    } catch {
      setError('Could not connect — is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const endCall = () => setSession(null)

  if (session) {
    return (
      <LiveKitRoom
        token={session.token}
        serverUrl={session.url}
        connect
        audio
        video={false}
        onDisconnected={endCall}
        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24, paddingTop: 60 }}
      >
        <RoomAudioRenderer />
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              background: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 32,
              margin: '0 auto 12px',
            }}
          >
            🎙️
          </div>
          <p style={{ color: '#374151', fontSize: 15, margin: 0 }}>
            Connected to <strong>Maya</strong> — speak now
          </p>
        </div>
        <VoiceAssistantControlBar />
      </LiveKitRoom>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 80, gap: 16 }}>
      <div
        style={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: '#eff6ff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 36,
        }}
      >
        📞
      </div>
      <h2 style={{ margin: 0, fontSize: 22, color: '#111827' }}>Call Maya</h2>
      <p style={{ margin: 0, color: '#6b7280', fontSize: 14, textAlign: 'center', maxWidth: 340 }}>
        Talk directly with the AI receptionist. Maya will answer your questions
        and escalate anything she doesn't know.
      </p>
      {error && (
        <p style={{ color: '#dc2626', fontSize: 13 }}>{error}</p>
      )}
      <button
        onClick={startCall}
        disabled={loading}
        style={{
          marginTop: 8,
          padding: '10px 28px',
          background: loading ? '#93c5fd' : '#1d4ed8',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          fontSize: 15,
          fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Connecting…' : 'Start Call'}
      </button>
      <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>
        Make sure the agent is running with <code>python -m agent.main start</code>
      </p>
    </div>
  )
}
