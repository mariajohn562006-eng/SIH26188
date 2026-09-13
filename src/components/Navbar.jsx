import React from 'react'
import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <header className="border-b border-line2">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="font-display text-lg tracking-tight text-inktext">
          ByteMind
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-ink2">
          <a href="#how-it-works" className="hover:text-inktext transition-colors">How it works</a>
          <a href="#technology" className="hover:text-inktext transition-colors">Technology</a>
          <a href="#trust" className="hover:text-inktext transition-colors">Trust &amp; audit</a>
          <Link to="/about" className="hover:text-inktext transition-colors">About</Link>
        </nav>

        <Link
          to="/dashboard"
          className="text-sm px-4 py-2 rounded-sm bg-signal text-ink font-medium hover:bg-signal/90 transition-colors"
        >
          Open console
        </Link>
      </div>
    </header>
  )
}