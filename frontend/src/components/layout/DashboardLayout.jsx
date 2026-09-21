/**
 * components/layout/DashboardLayout.jsx
 * Shared wrapper for all authenticated pages: Navbar + Sidebar + content.
 */
import React from 'react'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function DashboardLayout({ children, sidebarItems = [], pageTitle }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar pageTitle={pageTitle} />
      <div className="page-layout">
        <Sidebar items={sidebarItems} />
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}
