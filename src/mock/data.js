// All data here is fabricated for prototyping the UI/UX flow.
// Replace generateAnalysis() with a real call to your verification
// backend once one exists (see README "What to extend first").

export const documentTypes = [
  { id: 'passport', label: 'Passport', hint: 'Machine-readable, MRZ on back page' },
  { id: 'national_id', label: 'National ID card', hint: 'Front and back required' },
  { id: 'drivers_license', label: "Driver's licence", hint: 'Front and back required' },
  { id: 'residence_permit', label: 'Residence permit', hint: 'Front and back required' },
]

export const systemHealth = [
  { label: 'OCR engine', status: 'operational' },
  { label: 'Face-match service', status: 'operational' },
  { label: 'MRZ parser', status: 'operational' },
  { label: 'Tamper-detection model', status: 'degraded' },
  { label: 'Audit ledger', status: 'operational' },
]

export const recentVerifications = [
  { id: 'BM-2026-08841', name: 'A. Kowalski', doc: 'Passport', trust: 96, risk: 4, decision: 'approved', time: '2m ago' },
  { id: 'BM-2026-08840', name: 'R. Fernandes', doc: "Driver's licence", trust: 41, risk: 78, decision: 'manual_review', time: '11m ago' },
  { id: 'BM-2026-08839', name: 'S. Okafor', doc: 'National ID card', trust: 88, risk: 15, decision: 'approved', time: '24m ago' },
  { id: 'BM-2026-08838', name: 'M. Lindqvist', doc: 'Passport', trust: 12, risk: 94, decision: 'rejected', time: '39m ago' },
  { id: 'BM-2026-08837', name: 'T. Nakamura', doc: 'Residence permit', trust: 91, risk: 9, decision: 'approved', time: '1h ago' },
]

export const statistics = {
  totalToday: 1284,
  approvalRate: 0.87,
  avgProcessingSeconds: 6.4,
  flaggedToday: 63,
  weeklyVolume: [180, 210, 195, 260, 240, 300, 275],
}

export const riskBuckets = [
  { key: 'safe', label: 'Safe', count: 1042, color: 'bg-safe' },
  { key: 'suspicious', label: 'Suspicious', count: 149, color: 'bg-amber' },
  { key: 'danger', label: 'Danger', count: 41, color: 'bg-danger' },
  { key: 'manual_review', label: 'Manual review', count: 52, color: 'bg-ink2' },
]

// Deterministic pseudo-random so a given "document" always analyses the same way
function seededRandom(seed) {
  let x = Math.sin(seed) * 10000
  return x - Math.floor(x)
}

export function generateAnalysis(fileName = 'document') {
  const seed = fileName.length * 37 + fileName.charCodeAt(0)
  const r = (n) => Math.round(seededRandom(seed + n) * 100)

  const ocrConfidence = 70 + (r(1) % 30)
  const mrzValid = r(2) > 20
  const faceMatch = 55 + (r(3) % 45)
  const authenticity = 60 + (r(4) % 40)
  const tamperScore = r(5) % 100

  const trustScore = Math.round((ocrConfidence + faceMatch + authenticity + (100 - tamperScore)) / 4)
  const riskScore = 100 - trustScore

  let decision = 'approved'
  if (riskScore >= 70) decision = 'rejected'
  else if (riskScore >= 40) decision = 'manual_review'
  else if (riskScore >= 20) decision = 'suspicious'

  return {
    id: `BM-2026-${String(9000 + (seed % 900)).padStart(5, '0')}`,
    timestamp: new Date().toISOString(),
    trustScore,
    riskScore,
    decision,
    ocr: {
      confidence: ocrConfidence,
      fields: {
        fullName: 'JORDAN A. MITCHELL',
        documentNumber: `X${1000000 + (seed % 8999999)}`,
        dateOfBirth: '1991-04-12',
        expiryDate: '2029-11-30',
        nationality: 'PRT',
      },
    },
    mrz: {
      valid: mrzValid,
      checksumsPassed: mrzValid ? 4 : 2,
      checksumsTotal: 4,
    },
    faceMatch: {
      score: faceMatch,
      livenessPassed: faceMatch > 60,
    },
    authenticity: {
      score: authenticity,
      securityFeaturesDetected: authenticity > 75 ? ['hologram', 'UV pattern', 'microprint'] : ['microprint'],
    },
    tampering: {
      score: tamperScore,
      suspiciousRegions:
        tamperScore > 55
          ? [
              { label: 'Photo boundary', x: 62, y: 18, w: 22, h: 26 },
              { label: 'Date of birth field', x: 20, y: 58, w: 30, h: 10 },
            ]
          : [],
    },
    riskContributors: [
      { label: 'Face match confidence', weight: Math.round((100 - faceMatch) * 0.3) },
      { label: 'Document tampering signal', weight: Math.round(tamperScore * 0.35) },
      { label: 'MRZ checksum integrity', weight: mrzValid ? 2 : 22 },
      { label: 'OCR field confidence', weight: Math.round((100 - ocrConfidence) * 0.25) },
    ],
    decisionTimeline: [
      { label: 'Document received', t: '+0.0s' },
      { label: 'OCR extraction complete', t: '+1.2s' },
      { label: 'MRZ parsed', t: '+1.6s' },
      { label: 'Face match complete', t: '+3.1s' },
      { label: 'Tamper-detection scan complete', t: '+4.8s' },
      { label: 'Final decision computed', t: '+5.3s' },
    ],
    hash: `sha256:${Array.from({ length: 8 }, (_, i) => (seed * (i + 3) % 65536).toString(16).padStart(4, '0')).join('')}`,
  }
}