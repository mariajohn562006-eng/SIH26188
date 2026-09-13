// src/components/result/ui.jsx
//
// Shared building blocks for the Verification Result Workspace (module
// 4-9). Written the same way the rest of the app is written: plain
// JSX, hand-styled with Tailwind utility classes, no component
// library. Colors reference the theme tokens defined in index.html's
// Tailwind config (ink, panel, line, signal, amber, danger, safe,
// ink2, inktext) so this stays visually consistent with modules 1-3.

import React, { useState } from 'react'

// ---------- Status helpers ----------
// Central place that turns raw numbers from generateAnalysis() into a
// pass / warning / fail verdict, so every card in the workspace agrees
// on what "suspicious" means.

export function statusColor(status) {
  if (status === 'pass') return 'text-safe'
  if (status === 'warning') return 'text-amber'
  return 'text-danger'
}

export function statusMark(status) {
  if (status === 'pass') return '✓'
  if (status === 'warning') return '!'
  return '✕'
}

export function ocrStatus(confidence) {
  if (confidence >= 85) return 'pass'
  if (confidence >= 65) return 'warning'
  return 'fail'
}

export function mrzStatus(valid) {
  return valid ? 'pass' : 'fail'
}

export function faceStatus(score) {
  if (score >= 85) return 'pass'
  if (score >= 60) return 'warning'
  return 'fail'
}

export function authenticityStatus(score) {
  if (score >= 80) return 'pass'
  if (score >= 55) return 'warning'
  return 'fail'
}

export function tamperingStatus(tamperScore) {
  if (tamperScore < 30) return 'pass'
  if (tamperScore < 55) return 'warning'
  return 'fail'
}

// decision from generateAnalysis() -> the four Risk Center verdict states
export function decisionToVerdict(decision) {
  if (decision === 'approved') return 'Safe'
  if (decision === 'suspicious') return 'Suspicious'
  if (decision === 'manual_review') return 'Manual Review'
  return 'Danger' // 'rejected'
}

// ---------- StatusDot ----------

export function StatusDot({ status }) {
  return (
    <span className={`inline-flex h-5 w-5 items-center justify-center rounded-full border border-line2 font-mono text-xs ${statusColor(status)}`}>
      {statusMark(status)}
    </span>
  )
}

export function StatusBadge({ status, children }) {
  const label = children ?? (status === 'pass' ? 'Pass' : status === 'warning' ? 'Review' : 'Failed')
  return (
    <span className={`inline-flex items-center gap-1 rounded-sm border border-line2 px-2 py-1 text-xs font-medium ${statusColor(status)}`}>
      <span className="font-mono">{statusMark(status)}</span>
      {label}
    </span>
  )
}

// ---------- Card ----------

export function Card({ title, subtitle, right, children, className = '' }) {
  return (
    <div className={`rounded-sm border border-line bg-panel p-4 ${className}`}>
      {(title || right) && (
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="font-display text-sm font-medium text-inktext">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-ink2">{subtitle}</p>}
          </div>
          {right}
        </div>
      )}
      {children}
    </div>
  )
}

// ---------- ProgressBar ----------

export function ProgressBar({ value, colorClass = 'bg-signal' }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-line2">
      <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  )
}

// ---------- Tabs ----------
// Simple controlled tab switcher, styled after the existing Stepper
// component's active-state pattern (teal underline + text-inktext).

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="flex flex-wrap items-center gap-1 border-b border-line2">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={`relative px-3 py-2 text-sm font-medium transition-colors ${
            active === tab.value ? 'text-signal' : 'text-ink2 hover:text-inktext'
          }`}
        >
          {tab.label}
          {active === tab.value && (
            <span className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-signal" />
          )}
        </button>
      ))}
    </div>
  )
}

// ---------- Accordion ----------
// Single-open accordion, no library — just local state per item.

export function Accordion({ items }) {
  const [openId, setOpenId] = useState(null)
  return (
    <div className="divide-y divide-line2">
      {items.map((item) => {
        const isOpen = openId === item.id
        return (
          <div key={item.id}>
            <button
              onClick={() => setOpenId(isOpen ? null : item.id)}
              className="flex w-full items-center justify-between gap-2 py-3 text-left text-sm text-inktext"
            >
              <span className="flex items-center gap-2">{item.trigger}</span>
              <span className={`font-mono text-xs text-ink2 transition-transform ${isOpen ? 'rotate-180' : ''}`}>▾</span>
            </button>
            {isOpen && item.content && (
              <div className="pb-3 text-xs text-ink2">{item.content}</div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ---------- ToggleGroup ----------

export function ToggleGroup({ options, value, onChange }) {
  return (
    <div className="inline-flex flex-wrap items-center gap-1 rounded-sm border border-line2 p-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`rounded-sm px-3 py-1.5 text-xs font-medium transition-colors ${
            value === opt.value ? 'bg-signal text-ink' : 'text-ink2 hover:text-inktext'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

// ---------- CopyButton ----------
// Used by Audit & Integrity to let a reviewer copy the record hash.

export function CopyButton({ value, label = 'Copy' }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // Clipboard permission can be unavailable in a sandboxed preview —
      // fail quietly rather than throw, same tolerance as the camera
      // fallback in Verification.jsx.
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="rounded-sm border border-line2 px-2.5 py-1 text-xs text-ink2 transition-colors hover:border-ink2 hover:text-inktext"
    >
      {copied ? 'Copied' : label}
    </button>
  )
}

// ---------- downloadTextFile ----------
// Everything in this prototype runs client-side — no backend to send a
// report to — so "generate a report" / "export" just means build the
// text in memory and hand it to the browser as a download, the same
// way Verification.jsx never uploads the captured photo anywhere.

export function downloadTextFile(filename, content, mime = 'text/plain') {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
