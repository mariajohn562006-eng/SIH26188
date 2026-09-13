import React from 'react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-line2 mt-24">
      <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row justify-between gap-6 text-sm text-ink2">
        <div>
          <div className="font-display text-inktext mb-2">ByteMind</div>
          <p className="max-w-xs">
            Document and identity verification, with every decision traced back to the evidence that produced it.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-8 text-sm">
          <div>
            <div className="text-inktext mb-2">Product</div>
            <ul className="space-y-1.5">
              <li><Link to="/dashboard" className="hover:text-inktext transition-colors">Command dashboard</Link></li>
              <li><Link to="/verify" className="hover:text-inktext transition-colors">Verification workspace</Link></li>
              <li><Link to="/verify" className="hover:text-inktext transition-colors">Audit &amp; integrity</Link></li>
              <li><Link to="/verify" className="hover:text-inktext transition-colors">Reporting</Link></li>
            </ul>
          </div>
          <div>
            <div className="text-inktext mb-2">Company</div>
            <ul className="space-y-1.5">
              <li><Link to="/about#about" className="hover:text-inktext transition-colors">About</Link></li>
              <li><Link to="/about#system-overview" className="hover:text-inktext transition-colors">System overview</Link></li>
              <li><Link to="/about#architecture" className="hover:text-inktext transition-colors">Architecture</Link></li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t border-line2 py-4 text-center text-xs text-ink2 font-mono">
        prototype build — not connected to production verification services
      </div>
    </footer>
  )
}