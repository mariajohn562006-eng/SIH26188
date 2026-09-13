import React from 'react'
import { Link } from 'react-router-dom'
import { statistics, riskBuckets, recentVerifications, systemHealth } from '../mock/data.js'

const decisionStyle = {
  approved: 'text-safe',
  rejected: 'text-danger',
  manual_review: 'text-ink2',
  suspicious: 'text-amber',
}

const decisionLabel = {
  approved: 'Approved',
  rejected: 'Rejected',
  manual_review: 'Manual review',
  suspicious: 'Suspicious',
}

export default function Dashboard() {
  const maxWeekly = Math.max(...statistics.weeklyVolume)

  return (
    <div className="p-8 max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-2xl">Command dashboard</h1>
          <p className="text-ink2 text-sm mt-1">Live overview of verification volume, risk, and system status.</p>
        </div>
        <Link
          to="/verify"
          className="px-4 py-2.5 rounded-sm bg-signal text-ink text-sm font-medium hover:bg-signal/90 transition-colors"
        >
          New verification
        </Link>
      </div>

      {/* Overview stat cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Verifications today" value={statistics.totalToday.toLocaleString()} />
        <StatCard label="Approval rate" value={`${Math.round(statistics.approvalRate * 100)}%`} accent="text-safe" />
        <StatCard label="Avg. processing time" value={`${statistics.avgProcessingSeconds}s`} />
        <StatCard label="Flagged today" value={statistics.flaggedToday} accent="text-amber" />
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Statistics: weekly volume */}
        <div className="col-span-2 border border-line rounded-sm p-5">
          <h2 className="font-display text-sm mb-4 text-ink2">Weekly volume</h2>
          <div className="flex items-end gap-3 h-32">
            {statistics.weeklyVolume.map((v, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div
                  className="w-full bg-signal/70 rounded-sm"
                  style={{ height: `${(v / maxWeekly) * 100}%` }}
                  title={`${v} verifications`}
                />
                <span className="text-[10px] text-ink2 font-mono">
                  {['M', 'T', 'W', 'T', 'F', 'S', 'S'][i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Risk analytics */}
        <div className="border border-line rounded-sm p-5">
          <h2 className="font-display text-sm mb-4 text-ink2">Risk analytics</h2>
          <div className="space-y-3">
            {riskBuckets.map((b) => {
              const total = riskBuckets.reduce((s, x) => s + x.count, 0)
              const pct = Math.round((b.count / total) * 100)
              return (
                <div key={b.key}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-ink2">{b.label}</span>
                    <span className="font-mono">{b.count}</span>
                  </div>
                  <div className="h-1.5 bg-panel rounded-full overflow-hidden">
                    <div className={`h-full ${b.color}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Recent verifications */}
        <div className="col-span-2 border border-line rounded-sm">
          <div className="p-5 pb-3 flex items-center justify-between">
            <h2 className="font-display text-sm text-ink2">Recent verifications</h2>
            <span className="text-xs text-ink2 font-mono">{recentVerifications.length} shown</span>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-ink2 text-xs border-y border-line">
                <th className="font-normal py-2 px-5">ID</th>
                <th className="font-normal py-2">Applicant</th>
                <th className="font-normal py-2">Document</th>
                <th className="font-normal py-2">Trust</th>
                <th className="font-normal py-2">Decision</th>
                <th className="font-normal py-2 pr-5 text-right">When</th>
              </tr>
            </thead>
            <tbody>
              {recentVerifications.map((v) => (
                <tr key={v.id} className="border-b border-line last:border-0 hover:bg-panel/60">
                  <td className="py-2.5 px-5 font-mono text-xs text-ink2">{v.id}</td>
                  <td className="py-2.5">{v.name}</td>
                  <td className="py-2.5 text-ink2">{v.doc}</td>
                  <td className="py-2.5 font-mono">{v.trust}</td>
                  <td className={`py-2.5 ${decisionStyle[v.decision]}`}>{decisionLabel[v.decision]}</td>
                  <td className="py-2.5 pr-5 text-right text-ink2">{v.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* System health */}
        <div className="border border-line rounded-sm p-5">
          <h2 className="font-display text-sm mb-4 text-ink2">System health</h2>
          <div className="space-y-3">
            {systemHealth.map((s) => (
              <div key={s.label} className="flex items-center justify-between text-sm">
                <span>{s.label}</span>
                <span
                  className={`text-xs flex items-center gap-1.5 ${
                    s.status === 'operational' ? 'text-safe' : 'text-amber'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      s.status === 'operational' ? 'bg-safe' : 'bg-amber'
                    }`}
                  />
                  {s.status === 'operational' ? 'Operational' : 'Degraded'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, accent }) {
  return (
    <div className="border border-line rounded-sm p-5">
      <div className={`font-display text-2xl ${accent || ''}`}>{value}</div>
      <div className="text-xs text-ink2 mt-1">{label}</div>
    </div>
  )
}