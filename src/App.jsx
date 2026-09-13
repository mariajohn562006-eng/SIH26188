import React from 'react'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Verification from './pages/Verification.jsx'
import Information from './pages/Information.jsx'
import ConsoleShell from './components/ConsoleShell.jsx'

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/about" element={<Information />} />

        <Route element={<ConsoleShell />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/verify" element={<Verification />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  )
}