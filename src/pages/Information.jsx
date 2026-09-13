import React from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import Footer from '../components/Footer.jsx'

export default function Information() {
  return (
    <div className="bg-ink text-inktext font-body min-h-screen">
      <Navbar />

      <section className="max-w-6xl mx-auto px-6 pt-16 pb-10">
        <h1 className="font-display text-4xl tracking-tight">Information</h1>
        <p className="mt-4 text-ink2 max-w-2xl">
          What ByteMind is, how the verification pipeline fits together, and where to look
          when the console alone doesn't answer the question.
        </p>
      </section>

      {/* About */}
      <section id="about" className="border-t border-line2">
        <div className="max-w-6xl mx-auto px-6 py-16 grid md:grid-cols-2 gap-12 items-start">
          <div>
            <h2 className="font-display text-2xl mb-4">About</h2>
            <p className="text-ink2 max-w-md">
              ByteMind is an identity-document verification console. It checks a presented
              document against a live photo of the person holding it, and keeps the evidence
              behind every trust score visible rather than folded into a single opaque model.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <InfoStat value="6.4s" label="Median decision time" />
            <InfoStat value="99.1%" label="MRZ parse accuracy" />
            <InfoStat value="180+" label="Document templates" />
            <InfoStat value="6" label="Signals per verification" />
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="technology" className="border-t border-line2 bg-panel2">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="font-display text-2xl mb-4">Technology</h2>
          <p className="text-ink2 max-w-lg mb-10">
            Every verification runs the same four checks, and every check reports a real
            confidence value rather than a bare pass or fail.
          </p>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              ['OCR', 'Extracts printed fields — name, document number, dates, nationality — and scores its own confidence per field.'],
              ['MRZ parsing', 'Validates the machine-readable zone checksums against the printed fields to catch encoding mismatches.'],
              ['Face matching', 'Compares the live capture against the document photo and checks for liveness, not just similarity.'],
              ['Tamper detection', 'Scans the document image for localized signs of editing and reports the specific regions flagged.'],
            ].map(([title, body]) => (
              <div key={title} className="border border-line2 rounded-sm p-4">
                <div className="font-display text-base mb-1.5">{title}</div>
                <div className="text-sm text-ink2">{body}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="border-t border-line2">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="font-display text-2xl mb-4">Architecture</h2>
          <p className="text-ink2 max-w-lg mb-10">
            The console is one page per concern; the verification result is one workspace with
            many tabs, so a reviewer never has to piece a decision together across pages.
          </p>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <ArchBlock title="Capture" items={['Document selection', 'Document upload', 'Live photo', 'Preview']} />
            <ArchBlock
              title="Analysis pipeline"
              items={['OCR + MRZ', 'Face match + liveness', 'Authenticity + tampering', 'Decision scoring']}
            />
            <ArchBlock
              title="Record"
              items={['Result workspace', 'Audit & integrity', 'Reporting', 'Hash-chained ledger']}
            />
          </div>
        </div>
      </section>

      {/* System overview */}
      <section id="system-overview" className="border-t border-line2 bg-panel2">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="font-display text-2xl mb-10">System overview</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              ['01', 'Landing', 'Public entry point and product overview.'],
              ['02', 'Command dashboard', 'Live volume, risk mix and system health.'],
              ['03', 'Verification workspace', 'Five-step capture flow into the AI analysis pipeline.'],
              ['04', 'Result workspace', 'Overview, AI analysis, forensics, explainability, risk and investigation.'],
              ['05', 'Audit & integrity', 'Verification ID, record hash and audit timeline.'],
              ['06', 'Reporting', 'Verification summary, report generation and export.'],
              ['07', 'Information', 'This page — about, technology, architecture, system overview.'],
            ].map(([num, title, body]) => (
              <div key={num} className="border-t border-signal/40 pt-4">
                <div className="font-mono text-xs text-ink2 mb-2">{num}</div>
                <div className="font-display text-base mb-1.5">{title}</div>
                <div className="text-sm text-ink2">{body}</div>
              </div>
            ))}
          </div>

          <p className="mt-10 text-xs text-ink2 font-mono">
            Verification history, the ByteMind assistant and demo/simulation mode are planned next.
          </p>

          <Link
            to="/verify"
            className="mt-6 inline-block px-5 py-3 rounded-sm bg-signal text-ink font-medium hover:bg-signal/90 transition-colors"
          >
            Start a verification
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  )
}

function InfoStat({ value, label }) {
  return (
    <div className="border border-line2 rounded-sm p-4">
      <div className="font-display text-2xl">{value}</div>
      <div className="text-xs text-ink2 mt-1">{label}</div>
    </div>
  )
}

function ArchBlock({ title, items }) {
  return (
    <div className="border border-line2 rounded-sm p-4">
      <div className="font-display text-sm mb-3 text-ink2">{title}</div>
      <ul className="space-y-1.5 text-inktext">
        {items.map((it) => (
          <li key={it} className="flex items-center gap-2">
            <span className="w-1 h-1 rounded-full bg-signal inline-block" />
            {it}
          </li>
        ))}
      </ul>
    </div>
  )
}
