import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { History } from './pages/History'
import { KnowledgePage } from './pages/KnowledgePage'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/history', label: 'History' },
  { to: '/knowledge', label: 'Knowledge Base' },
]

function Layout() {
  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb', fontFamily: 'system-ui, sans-serif' }}>
      <nav
        style={{
          background: '#fff',
          borderBottom: '1px solid #e5e7eb',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          height: 52,
          gap: 24,
        }}
      >
        <Link
          to="/dashboard"
          style={{ fontWeight: 700, color: '#111827', textDecoration: 'none', fontSize: 15 }}
        >
          Frontdesk AI
        </Link>
        {NAV_LINKS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              color: isActive ? '#1d4ed8' : '#374151',
              textDecoration: 'none',
              fontWeight: isActive ? 600 : 400,
              fontSize: 14,
              borderBottom: isActive ? '2px solid #1d4ed8' : '2px solid transparent',
              paddingBottom: 2,
            })}
          >
            {label}
          </NavLink>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 12, color: '#9ca3af' }}>
          Luxe Salon &amp; Spa — Supervisor Panel
        </span>
      </nav>

      <main style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
