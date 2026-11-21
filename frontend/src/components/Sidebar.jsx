import React from 'react'
import { NavLink } from 'react-router-dom'
import { useHealth } from '../hooks/useApi'

/* ── Inline SVG icons (no external dep) ── */
const Icon = ({ d, size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    className="nav-icon">
    <path d={d} />
  </svg>
)

const ICONS = {
  overview:     'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
  profile:      'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z',
  discovery:    'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  applications: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  documents:    'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6',
  ai:           'M12 2a10 10 0 100 20 10 10 0 000-20zm0 6v6l4 2',
  email:        'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm0 0l8 8 8-8',
  telegram:     'M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z',
  settings:     'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
}

const NAV = [
  { section: 'Dashboard', items: [
    { to: '/',             label: 'Overview',     icon: 'overview'     },
    { to: '/profile',      label: 'My Profile',   icon: 'profile'      },
  ]},
  { section: 'Job Hunting', items: [
    { to: '/discovery',    label: 'Job Discovery',icon: 'discovery'    },
    { to: '/applications', label: 'Applications', icon: 'applications' },
    { to: '/documents',    label: 'Documents',    icon: 'documents'    },
  ]},
  { section: 'AI & Config', items: [
    { to: '/ai',           label: 'AI Config',    icon: 'ai'           },
    { to: '/email',        label: 'Email (Gmail)',icon: 'email'        },
    { to: '/telegram',     label: 'Telegram',     icon: 'telegram'     },
    { to: '/settings',     label: 'Settings',     icon: 'settings'     },
  ]},
]

export default function Sidebar() {
  const { data: health } = useHealth()
  const online = health?.status === 'online'

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="bob-logo">B</div>
        <div>
          <div className="bob-title">BOB</div>
          <div className="bob-subtitle">Job Agent</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV.map(({ section, items }) => (
          <div key={section}>
            <div className="nav-section-label">{section}</div>
            {items.map(({ to, label, icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
              >
                <Icon d={ICONS[icon]} />
                {label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Backend status */}
      <div className="sidebar-status">
        <div className="status-pill">
          <div className={`status-dot${online ? '' : ' offline'}`} />
          <span>{online ? `Backend v${health?.version || '1.0'} online` : 'Backend offline'}</span>
        </div>
      </div>
    </aside>
  )
}
