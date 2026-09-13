// src/components/result/RiskCenterTab.jsx

import React from 'react'
import { Card, ProgressBar, decisionToVerdict } from './ui.jsx'

const VERDICTS = ['Safe', 'Suspicious', 'Danger', 'Manual Review']

const VERDICT_CLASS = {
  Safe: 'bg-safe text-ink border-safe',
  Suspicious: 'bg-amber text-ink border-amber',
  Danger: 'bg-danger text-ink border-danger',
  'Manual Review': 'bg-inktext text-ink border-inktext',
}

const CATEGORY_NOTES = {
  'Face match confidence': 'Contribution from how well the live photo matches the document photo.',
  'Document tampering signal': 'Contribution from localized image-manipulation detection.',
  'MRZ checksum integrity': 'Contribution from machine-readable-zone checksum validation.',
  'OCR field confidence': 'Contribution from extraction confidence on printed fields.',
}

export default function RiskCenterTab({ result }) {
  const verdict = decisionToVerdict(result.decision)

  // AI Confidence is deliberately a different number from Risk — it
  // reflects how sure the models are in their own readings (OCR +
  // authenticity signal quality), not whether the document itself is
  // trustworthy. Derived from real returned values, not invented.
  const aiConfidence = Math.round((result.ocr.confidence + result.authenticity.score) / 2)

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {VERDICTS.map((v) => (
          <div
            key={v}
            className={`rounded-sm border px-3 py-2.5 text-sm font-medium ${
              v === verdict ? VERDICT_CLASS[v] : 'border-line2 text-ink2'
            }`}
          >
            {v}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1.3fr]">
        <Card title="Confidence vs. Risk" subtitle="A confident reading can still be high-risk.">
          <div className="flex items-center justify-around py-2">
            <Gauge label="AI Confidence" value={aiConfidence} ringColor="#49D6C6" />
            <Gauge label="Risk Score" value={result.riskScore} ringColor="#E5484D" />
          </div>
        </Card>

        <Card title="Recommendation">
          <p className="text-sm text-ink2">
            {verdict === 'Safe'
              ? 'No adverse signals detected. Safe to approve automatically.'
              : verdict === 'Manual Review'
              ? 'Signals are mixed enough that a human reviewer should confirm before a final decision.'
              : verdict === 'Danger'
              ? 'Multiple strong adverse signals detected. Recommend rejection pending manual confirmation.'
              : 'Some signals warrant a closer look before approval.'}
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {result.riskContributors.map((c) => (
          <Card key={c.label}>
            <div className="mb-2 flex items-baseline justify-between">
              <span className="text-sm font-medium text-inktext">{c.label}</span>
              <span className="font-mono text-sm text-inktext">{c.weight} pts</span>
            </div>
            <ProgressBar value={c.weight} colorClass={c.weight >= 25 ? 'bg-danger' : c.weight >= 12 ? 'bg-amber' : 'bg-signal'} />
            <p className="mt-2 text-xs text-ink2">{CATEGORY_NOTES[c.label] ?? 'Contribution to the overall risk score.'}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}

function Gauge({ label, value, ringColor }) {
  const angle = Math.max(0, Math.min(100, value)) * 3.6
  return (
    <div className="flex flex-col items-center">
      <div
        className="relative flex h-24 w-24 items-center justify-center rounded-full"
        style={{
          background: `conic-gradient(${ringColor} ${angle}deg, #1A2740 ${angle}deg)`,
        }}
      >
        <div className="flex h-[72px] w-[72px] items-center justify-center rounded-full bg-panel">
          <span className="font-mono text-lg font-semibold text-inktext">{value}%</span>
        </div>
      </div>
      <p className="mt-2 text-xs text-ink2">{label}</p>
    </div>
  )
}
