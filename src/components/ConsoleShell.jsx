import React from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Command dashboard', glyph: '01' },
  { to: '/verify', label: 'New verification', glyph: '02' },
]

export default function ConsoleShell() {
  return (
    <div className="min-h-screen flex bg-ink text-inktext font-body">
      <aside className="w-60 shrink-0 border-r border-line flex flex-col">
        <div className="h-16 flex items-center px-5 border-b border-line">
          <span className="font-display text-lg tracking-tight">ByteMind</span>
        </div>

        <nav className="flex-1 py-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-5 py-3 text-sm border-l-2 transition-colors ${
                  isActive
                    ? 'border-signal text-inktext bg-panel'
                    : 'border-transparent text-ink2 hover:text-inktext hover:bg-panel/60'
                }`
              }
            >
              <span className="font-mono text-xs text-ink2">{item.glyph}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-5 border-t border-line text-xs text-ink2 space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-safe inline-block" />
            All systems reporting
          </div>
          <div className="font-mono">operator: r.dias@bytemind</div>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  )
}