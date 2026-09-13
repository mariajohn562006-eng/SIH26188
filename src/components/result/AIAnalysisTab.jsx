// src/components/result/AIAnalysisTab.jsx

import React from 'react'
import {
  Card,
  ProgressBar,
  StatusBadge,
  ocrStatus,
  mrzStatus,
  faceStatus,
  authenticityStatus,
  tamperingStatus,
} from './ui.jsx'

export default function AIAnalysisTab({ result, docImageUrl, livePhotoUrl }) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <OCRCard result={result} />
      <MRZCard result={result} />
      <FaceMatchCard result={result} docImageUrl={docImageUrl} livePhotoUrl={livePhotoUrl} />
      <AuthenticityTamperingCard result={result} />
    </div>
  )
}

function OCRCard({ result }) {
  const status = ocrStatus(result.ocr.confidence)
  const fields = [
    { label: 'Full Name', value: result.ocr.fields.fullName },
    { label: 'Document Number', value: result.ocr.fields.documentNumber },
    { label: 'Date of Birth', value: result.ocr.fields.dateOfBirth },
    { label: 'Expiry Date', value: result.ocr.fields.expiryDate },
    { label: 'Nationality', value: result.ocr.fields.nationality },
  ]

  return (
    <Card title="Optical Character Recognition" right={<StatusBadge status={status} />}>
      <div className="mb-3 flex items-baseline justify-between text-xs text-ink2">
        <span>Extraction confidence</span>
        <span className="font-mono text-inktext">{result.ocr.confidence}%</span>
      </div>
      <dl className="space-y-2">
        {fields.map((f) => (
          <div key={f.label} className="flex items-baseline justify-between gap-3 text-sm">
            <dt className="text-ink2">{f.label}</dt>
            <dd className="font-mono text-inktext">{f.value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  )
}

function MRZCard({ result }) {
  const status = mrzStatus(result.mrz.valid)
  return (
    <Card title="Machine-Readable Zone" right={<StatusBadge status={status} />}>
      <div className="mb-3 flex items-baseline justify-between text-xs text-ink2">
        <span>Checksum validation</span>
        <span className="font-mono text-inktext">
          {result.mrz.checksumsPassed}/{result.mrz.checksumsTotal} passed
        </span>
      </div>
      <p className="text-xs text-ink2">
        {result.mrz.valid
          ? 'All MRZ checksums validated against the printed fields.'
          : 'One or more MRZ checksums did not match the printed fields — possible alteration.'}
      </p>
    </Card>
  )
}

function FaceMatchCard({ result, docImageUrl, livePhotoUrl }) {
  const status = faceStatus(result.faceMatch.score)
  return (
    <Card title="Face Match" right={<StatusBadge status={status} />}>
      <div className="mb-3 grid grid-cols-2 gap-3">
        <div>
          <p className="mb-1.5 text-xs text-ink2">Document photo</p>
          <div className="aspect-square overflow-hidden rounded-sm border border-line2 bg-panel2">
            {docImageUrl && <img src={docImageUrl} alt="Document" className="h-full w-full object-cover" />}
          </div>
        </div>
        <div>
          <p className="mb-1.5 text-xs text-ink2">Live capture</p>
          <div className="aspect-square overflow-hidden rounded-sm border border-line2 bg-panel2">
            {livePhotoUrl && <img src={livePhotoUrl} alt="Live capture" className="h-full w-full object-cover" />}
          </div>
        </div>
      </div>
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-xs text-ink2">Similarity score</span>
        <span className="font-mono text-lg font-semibold text-inktext">{result.faceMatch.score}%</span>
      </div>
      <ProgressBar value={result.faceMatch.score} colorClass="bg-signal" />
      <p className="mt-2 text-xs text-ink2">
        {result.faceMatch.livenessPassed ? 'Liveness check passed.' : 'Liveness check did not pass.'}
      </p>
    </Card>
  )
}

function AuthenticityTamperingCard({ result }) {
  const authStatus = authenticityStatus(result.authenticity.score)
  const tamperStatus = tamperingStatus(result.tampering.score)

  return (
    <Card title="Document Authenticity & Tampering">
      <div className="mb-4 space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-ink2">Authenticity</p>
          <StatusBadge status={authStatus} />
        </div>
        <div className="flex items-baseline justify-between text-xs text-ink2">
          <span>Authenticity score</span>
          <span className="font-mono text-inktext">{result.authenticity.score}/100</span>
        </div>
        <p className="text-xs text-ink2">
          Security features detected: {result.authenticity.securityFeaturesDetected.join(', ')}
        </p>
      </div>

      <div className="border-t border-line2 pt-3">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-ink2">Tampering Detection</p>
          <StatusBadge status={tamperStatus} />
        </div>
        <p className="text-xs text-ink2">
          {result.tampering.suspiciousRegions.length === 0
            ? 'No regions flagged.'
            : `${result.tampering.suspiciousRegions.length} region(s) flagged for review — see the Forensics tab.`}
        </p>
      </div>
    </Card>
  )
}
