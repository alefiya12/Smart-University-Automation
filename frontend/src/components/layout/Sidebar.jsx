import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

/**
 * Sidebar — role-specific navigation links.
 * Active link is highlighted via .sidebar-item.active.
 *
 * Props:
 *   items: Array<{ to, label, icon, section? }>
 */
export default function Sidebar({ items = [] }) {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  // Group items by section
  const sections = []
  let currentSection = null
  for (const item of items) {
    if (item.section && item.section !== currentSection) {
      sections.push({ label: item.section, items: [] })
      currentSection = item.section
    }
    if (sections.length === 0) sections.push({ label: null, items: [] })
    sections[sections.length - 1].items.push(item)
  }

  return (
    <aside className="sidebar" aria-label="Sidebar navigation">
      {sections.map((sec, si) => (
        <React.Fragment key={si}>
          {sec.label && (
            <div className="sidebar-section-label">{sec.label}</div>
          )}
          {sec.items.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-item${isActive ? ' active' : ''}`
              }
              end={item.exact}
            >
              {item.icon && (
                <span className="sidebar-item-icon" aria-hidden="true">
                  {item.icon}
                </span>
              )}
              {item.label}
            </NavLink>
          ))}
        </React.Fragment>
      ))}

      <div className="sidebar-spacer" />
      <div className="sidebar-divider" />

      {/* Logout */}
      <button className="sidebar-item" onClick={handleLogout} style={{ color: 'var(--color-danger)' }}>
        <span className="sidebar-item-icon" aria-hidden="true">↩</span>
        Logout
      </button>
    </aside>
  )
}
