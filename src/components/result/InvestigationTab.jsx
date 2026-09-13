// src/components/result/InvestigationTab.jsx
//
// Note: the current Verification flow (module 3) only collects one
// document + one live photo, so there is no second document to run a
// real cross-document consistency check against yet. That section is
// left honest about that rather than fabricating a comparison.

import React, { useState } from 'react'
import {
  Card,
  StatusDot,
  ocrStatus,
  mrzStatus,
  faceStatus,
  tamperingStatus,
  decisionToVerdict,
} from './ui.jsx'

export default function InvestigationTab({ result, docType }) {
  const chain = [
    { label: 'Person', status: 'pass' },
    { label: 'Document', status: 'pass' },
    { label: 'OCR', status: ocrStatus(result.ocr.confidence) },
    { label: 'MRZ', status: mrzStatus(result.mrz.valid) },
    { label: 'Face', status: faceStatus(result.faceMatch.score) },
    { label: 'Liveness', status: result.faceMatch.livenessPassed ? 'pass' : 'fail' },
    { label: 'Risk Engine', status: tamperingStatus(result.tampering.score) },
    { label: 'Final Decision', status: decisionToVerdict(result.decision) === 'Safe' ? 'pass' : 'warning' },
  ]

  return (
    <div className="space-y-4">
      <Card title="Identity Consistency" subtitle="Cross-check across the full pipeline, person to final decision.">
        <div className="flex flex-wrap items-center gap-y-3">
          {chain.map((step, i) => (
            <div key={step.label} className="flex items-center">
              <div className="flex flex-col items-center gap-1 px-1">
                <StatusDot status={step.status} />
                <span className="text-center text-xs text-inktext">{step.label}</span>
              </div>
              {i < chain.length - 1 && <span className="mx-1 text-ink2">→</span>}
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Cross-Document Verification">
          <div className="mb-3 flex flex-wrap gap-3 text-sm">
            <span className="text-inktext">✓ {docType || 'Document'} submitted</span>
            <span className="text-inktext">✓ Live photo submitted</span>
          </div>
          <p className="text-xs text-ink2">
            This flow currently collects a single document plus a live photo. Cross-document
            consistency checks (e.g. passport vs. visa) will populate here once multi-document
            submission is supported.
          </p>
        </Card>

        <ReviewerDecisionPanel />
      </div>
    </div>
  )
}

const DECISIONS = [
  { value: 'approve', label: 'Approve', activeClass: 'bg-safe text-ink border-safe' },
  { value: 'reject', label: 'Reject', activeClass: 'bg-danger text-ink border-danger' },
  { value: 'request_new_document', label: 'Request New Document', activeClass: 'bg-amber text-ink border-amber' },
]

function ReviewerDecisionPanel() {
  const [decision, setDecision] = useState(null)
  const [notes, setNotes] = useState('')

  return (
    <Card title="Reviewer Decision" subtitle="Not yet connected to a backend — selection only, for demo purposes.">
      <div className="mb-3 flex flex-wrap gap-2">
        {DECISIONS.map((d) => (
          <button
            key={d.value}
            onClick={() => setDecision(d.value)}
            className={`rounded-sm border px-3 py-1.5 text-sm font-medium transition-colors ${
              decision === d.value ? d.activeClass : 'border-line2 text-ink2 hover:text-inktext'
            }`}
          >
            {d.label}
          </button>
        ))}
      </div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Add reviewer notes (optional)…"
        rows={3}
        className="w-full resize-none rounded-sm border border-line2 bg-panel2 p-2 text-sm text-inktext placeholder:text-ink2 focus:outline-none focus:ring-1 focus:ring-signal"
      />
      {decision && (
        <p className="mt-2 text-xs text-ink2">
          Decision selected: <span className="text-inktext">{DECISIONS.find((d) => d.value === decision)?.label}</span>
          {notes && ' — notes recorded'}
        </p>
      )}
    </Card>
  )
}
