// src/components/result/OverviewTab.jsx

import React from 'react'
import { Card, StatusBadge, ocrStatus, mrzStatus, faceStatus, authenticityStatus, tamperingStatus } from './ui.jsx'

export default function OverviewTab({ result }) {
  const signals = [
    { label: 'OCR', status: ocrStatus(result.ocr.confidence) },
    { label: 'MRZ', status: mrzStatus(result.mrz.valid) },
    { label: 'Face Match', status: faceStatus(result.faceMatch.score) },
    { label: 'Authenticity', status: authenticityStatus(result.authenticity.score) },
    { label: 'Tampering', status: tamperingStatus(result.tampering.score) },
  ]

  return (
    <div className="space-y-4">
      <Card title={`Verification ${result.id}`} subtitle="Signal rollup across the full analysis pipeline.">
        <div className="flex flex-wrap gap-2">
          {signals.map((s) => (
            <div key={s.label} className="flex items-center gap-2">
              <span className="text-xs text-ink2">{s.label}</span>
              <StatusBadge status={s.status} />
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-4">
        <Card title="Trust score">
          <div className="font-display text-3xl text-signal">{result.trustScore}</div>
        </Card>
        <Card title="Risk score">
          <div className="font-display text-3xl text-amber">{result.riskScore}</div>
        </Card>
        <Card title="Final decision">
          <div className="font-display text-lg text-inktext capitalize">{result.decision.replace('_', ' ')}</div>
        </Card>
      </div>
    </div>
  )
}
