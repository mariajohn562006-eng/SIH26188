// src/components/result/ExplainableAITab.jsx

import React from 'react'
import {
  Card,
  Accordion,
  StatusDot,
  StatusBadge,
  ProgressBar,
  ocrStatus,
  mrzStatus,
  faceStatus,
  authenticityStatus,
} from './ui.jsx'

// Build the "why flagged" reasons from the actual result — never invent
// a reason that isn't backed by a real field.
function buildReasons(result) {
  const reasons = []

  if (!result.mrz.valid) {
    reasons.push({
      id: 'mrz',
      status: 'fail',
      summary: 'MRZ checksum validation failed',
      detail: `${result.mrz.checksumsPassed}/${result.mrz.checksumsTotal} checksums passed — one or more encoded fields do not match the printed document.`,
    })
  }

  if (result.tampering.suspiciousRegions.length > 0) {
    reasons.push({
      id: 'tampering',
      status: 'fail',
      summary: `${result.tampering.suspiciousRegions.length} region(s) show signs of tampering`,
      detail: `Flagged regions: ${result.tampering.suspiciousRegions.map((r) => r.label).join(', ')}.`,
    })
  }

  const fStatus = faceStatus(result.faceMatch.score)
  if (fStatus !== 'pass') {
    reasons.push({
      id: 'face',
      status: fStatus,
      summary: `Face similarity at ${result.faceMatch.score}%`,
      detail: 'Below the threshold typically expected for a confident automatic match.',
    })
  }

  const aStatus = authenticityStatus(result.authenticity.score)
  if (aStatus !== 'pass') {
    reasons.push({
      id: 'authenticity',
      status: aStatus,
      summary: `Authenticity score at ${result.authenticity.score}/100`,
      detail: `Security features detected: ${result.authenticity.securityFeaturesDetected.join(', ')}.`,
    })
  }

  const oStatus = ocrStatus(result.ocr.confidence)
  if (oStatus !== 'pass') {
    reasons.push({
      id: 'ocr',
      status: oStatus,
      summary: `OCR extraction confidence at ${result.ocr.confidence}%`,
      detail: 'One or more fields were extracted with lower-than-ideal confidence.',
    })
  }

  if (reasons.length === 0) {
    reasons.push({ id: 'clean', status: 'pass', summary: 'No adverse signals detected', detail: 'All checks passed within expected thresholds.' })
  }

  return reasons
}

export default function ExplainableAITab({ result }) {
  const reasons = buildReasons(result)
  const maxWeight = Math.max(...result.riskContributors.map((c) => c.weight), 1)

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card title="Why Flagged?">
        <Accordion
          items={reasons.map((r) => ({
            id: r.id,
            trigger: (
              <>
                <StatusDot status={r.status} />
                {r.summary}
              </>
            ),
            content: r.detail,
          }))}
        />
      </Card>

      <Card title="Risk Contributors" right={<span className="font-mono text-lg font-semibold text-inktext">{result.riskScore}<span className="text-xs font-normal text-ink2">/100</span></span>}>
        <div className="space-y-3">
          {result.riskContributors.map((c) => (
            <div key={c.label}>
              <div className="mb-1 flex items-baseline justify-between text-xs">
                <span className="text-ink2">{c.label}</span>
                <span className="font-mono text-inktext">{c.weight} pts</span>
              </div>
              <ProgressBar
                value={(c.weight / maxWeight) * 100}
                colorClass={c.weight >= maxWeight * 0.66 ? 'bg-danger' : c.weight >= maxWeight * 0.33 ? 'bg-amber' : 'bg-signal'}
              />
            </div>
          ))}
        </div>
      </Card>

      <Card title="Evidence Summary">
        <div className="space-y-3">
          {reasons.map((r) => (
            <div key={r.id} className="space-y-1 border-b border-line2 pb-3 last:border-b-0 last:pb-0">
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-medium text-inktext">{r.summary}</span>
                <StatusBadge status={r.status} />
              </div>
              <p className="text-xs text-ink2">{r.detail}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Decision Timeline">
        <ol className="relative">
          {result.decisionTimeline.map((event, i) => (
            <li key={event.label} className="relative flex gap-3 pb-4 last:pb-0">
              <div className="flex flex-col items-center">
                <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-signal" />
                {i < result.decisionTimeline.length - 1 && <span className="mt-1 w-px flex-1 bg-line2" />}
              </div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-xs text-ink2">{event.t}</span>
                  <span className="text-sm text-inktext">{event.label}</span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  )
}
