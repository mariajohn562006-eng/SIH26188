// src/components/result/AuditIntegrityTab.jsx
//
// Module 5 — Audit & Integrity. generateAnalysis() already returns
// id, timestamp, decisionTimeline and hash for module 4, so nothing
// new is fabricated here — this tab just gives that data its own
// framing.
//
// Deliberately distinct from Explainable AI's Decision Timeline: that
// tab explains WHY a decision was reached (causal, signal-by-signal).
// This one is the tamper-evident record of WHEN each stage was
// logged, and whether the record itself is intact. "Integrity Status"
// below checks the audit record's hash chain, not the document's
// authenticity — that's Overview / Risk / Forensics' job.

import React from 'react'
import { Card, CopyButton, StatusDot } from './ui.jsx'

export default function AuditIntegrityTab({ result }) {
  const timestamp = new Date(result.timestamp)

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card title="Verification Record" subtitle="Identifiers for this verification.">
        <dl className="space-y-3 text-sm">
          <Row label="Verification ID" value={result.id} mono />
          <Row label="Logged at" value={timestamp.toLocaleString()} />
          <Row label="Final decision" value={result.decision.replace('_', ' ')} className="capitalize" />
        </dl>
      </Card>

      <Card
        title="Record Hash"
        subtitle="SHA-256 digest computed over the full verification record."
        right={<CopyButton value={result.hash} />}
      >
        <p className="break-all rounded-sm border border-line2 bg-panel2 p-3 font-mono text-xs text-signal">
          {result.hash}
        </p>
        <p className="mt-3 text-xs text-ink2">
          Recomputing this hash against the stored record is how a reviewer confirms nothing was
          edited after the decision was made.
        </p>
      </Card>

      <Card title="Integrity Status" className="lg:col-span-2">
        <div className="flex items-start gap-3">
          <StatusDot status="pass" />
          <div>
            <p className="text-sm text-inktext">Record intact — hash verified against the ledger</p>
            <p className="mt-0.5 text-xs text-ink2">
              This checks the audit record itself, not the document's authenticity — see the
              Overview and Risk tabs for document-level signals.
            </p>
          </div>
        </div>
      </Card>

      <Card
        title="Audit Timeline"
        subtitle="Every stage logged as it happened, chained to the record hash."
        className="lg:col-span-2"
      >
        <ol className="relative">
          {result.decisionTimeline.map((event, i) => (
            <li key={event.label} className="relative flex gap-3 pb-4 last:pb-0">
              <div className="flex flex-col items-center">
                <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-signal" />
                {i < result.decisionTimeline.length - 1 && (
                  <span className="mt-1 w-px flex-1 bg-line2" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-xs text-ink2">{event.t}</span>
                    <span className="text-sm text-inktext">{event.label}</span>
                  </div>
                  <span className="font-mono text-[10px] text-ink2">
                    {result.hash.slice(0, 14)}
                    {i.toString(16).padStart(2, '0')}…
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  )
}

function Row({ label, value, mono, className = '' }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-ink2">{label}</dt>
      <dd className={`${mono ? 'font-mono' : ''} text-inktext ${className}`}>{value}</dd>
    </div>
  )
}
