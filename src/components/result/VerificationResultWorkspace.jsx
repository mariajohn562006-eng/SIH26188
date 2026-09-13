// src/components/result/VerificationResultWorkspace.jsx
//
// The core architecture decision from the project brief: one
// workspace, six tabs, never separate pages. Drop this into
// Verification.jsx's result view.

import React, { useState } from 'react'
import { Tabs } from './ui.jsx'
import OverviewTab from './OverviewTab.jsx'
import AIAnalysisTab from './AIAnalysisTab.jsx'
import ForensicsTab from './ForensicsTab.jsx'
import ExplainableAITab from './ExplainableAITab.jsx'
import RiskCenterTab from './RiskCenterTab.jsx'
import InvestigationTab from './InvestigationTab.jsx'
import AuditIntegrityTab from './AuditIntegrityTab.jsx'
import ReportingTab from './ReportingTab.jsx'

const TABS = [
  { value: 'overview', label: 'Overview' },
  { value: 'ai-analysis', label: 'AI Analysis' },
  { value: 'forensics', label: 'Forensics' },
  { value: 'explainable', label: 'Explainable AI' },
  { value: 'risk', label: 'Risk' },
  { value: 'investigation', label: 'Investigation' },
  { value: 'audit', label: 'Audit & Integrity' },
  { value: 'reporting', label: 'Reporting' },
]

export default function VerificationResultWorkspace({ result, docType, docImageUrl, livePhotoUrl }) {
  const [tab, setTab] = useState('overview')

  return (
    <div>
      <Tabs tabs={TABS} active={tab} onChange={setTab} />
      <div className="pt-4">
        {tab === 'overview' && <OverviewTab result={result} />}
        {tab === 'ai-analysis' && (
          <AIAnalysisTab result={result} docImageUrl={docImageUrl} livePhotoUrl={livePhotoUrl} />
        )}
        {tab === 'forensics' && <ForensicsTab result={result} docImageUrl={docImageUrl} />}
        {tab === 'explainable' && <ExplainableAITab result={result} />}
        {tab === 'risk' && <RiskCenterTab result={result} />}
        {tab === 'investigation' && (
          <InvestigationTab result={result} docType={docType} />
        )}
        {tab === 'audit' && <AuditIntegrityTab result={result} />}
        {tab === 'reporting' && <ReportingTab result={result} docType={docType} />}
      </div>
    </div>
  )
}
