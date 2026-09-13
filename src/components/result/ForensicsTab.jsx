// src/components/result/ForensicsTab.jsx
//
// Note on honesty: generateAnalysis() only returns bounding-box
// coordinates for tampering.suspiciousRegions. It does NOT return
// per-field coordinates for OCR/MRZ/Face regions, so those views show
// the plain document with a note rather than invented boxes. Once the
// real backend returns field-level coordinates, swap them in here.

import React, { useState } from 'react'
import { Card, ToggleGroup, StatusDot, ocrStatus, mrzStatus, faceStatus } from './ui.jsx'

const VIEWS = [
  { value: 'original', label: 'Original' },
  { value: 'ocr', label: 'OCR' },
  { value: 'mrz', label: 'MRZ' },
  { value: 'face', label: 'Face' },
  { value: 'suspicious', label: 'Suspicious Regions' },
]

export default function ForensicsTab({ result, docImageUrl }) {
  const [view, setView] = useState('original')
  const regions = view === 'suspicious' ? result.tampering.suspiciousRegions : []

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
      <div className="space-y-3">
        <ToggleGroup options={VIEWS} value={view} onChange={setView} />

        <div className="relative aspect-[3/2] w-full overflow-hidden rounded-sm border border-line2 bg-panel2">
          {docImageUrl ? (
            <img src={docImageUrl} alt="Document" className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-xs text-ink2">
              No document image available in this preview
            </div>
          )}

          {regions.map((region) => (
            <div
              key={region.label}
              className="absolute animate-pulse rounded-sm border-2 border-danger"
              style={{
                left: `${region.x}%`,
                top: `${region.y}%`,
                width: `${region.w}%`,
                height: `${region.h}%`,
              }}
            >
              <span className="absolute -top-5 left-0 whitespace-nowrap rounded-sm bg-danger px-1 text-[10px] font-medium text-ink">
                {region.label}
              </span>
            </div>
          ))}

          {view !== 'original' && view !== 'suspicious' && (
            <div className="absolute bottom-2 left-2 rounded-sm bg-panel/90 px-2 py-1 text-[10px] text-ink2">
              Field-level {view.toUpperCase()} coordinates not yet returned by the backend — overlay
              pending real bounding-box data.
            </div>
          )}
        </div>
      </div>

      <RiskHeatmap result={result} />
    </div>
  )
}

function RiskHeatmap({ result }) {
  const ocrSt = ocrStatus(result.ocr.confidence)
  const rows = [
    { label: 'Full Name', status: ocrSt },
    { label: 'Date of Birth', status: ocrSt },
    { label: 'Document Number', status: ocrSt },
    { label: 'Expiry Date', status: ocrSt },
    { label: 'Photo', status: faceStatus(result.faceMatch.score) },
    { label: 'MRZ', status: mrzStatus(result.mrz.valid) },
    ...result.tampering.suspiciousRegions.map((r) => ({ label: r.label, status: 'fail' })),
  ]

  return (
    <Card title="Risk Heatmap" subtitle="Where suspicious elements were detected across the document.">
      <ul className="divide-y divide-line2">
        {rows.map((row, i) => (
          <li key={`${row.label}-${i}`} className="flex items-center justify-between gap-3 py-2">
            <span className="text-sm text-inktext">{row.label}</span>
            <StatusDot status={row.status} />
          </li>
        ))}
      </ul>
    </Card>
  )
}
