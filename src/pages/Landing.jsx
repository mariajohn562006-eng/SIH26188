import React from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import Footer from '../components/Footer.jsx'

export default function Landing() {
  return (
    <div className="bg-ink text-inktext font-body min-h-screen">
      <Navbar />

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-24 grid md:grid-cols-2 gap-16 items-center">
        <div>
          <h1 className="font-display text-5xl leading-[1.05] tracking-tight text-inktext">
            Verify a document.
            <br />
            See exactly why.
          </h1>
          <p className="mt-6 text-lg text-ink2 max-w-md">
            ByteMind checks identity documents for authenticity, matches the holder's face,
            and shows the evidence behind every trust score, so a rejection is never a black box.
          </p>

          <div className="mt-8 flex items-center gap-4">
            <Link
              to="/verify"
              className="px-5 py-3 rounded-sm bg-signal text-ink font-medium hover:bg-signal/90 transition-colors"
            >
              Start a verification
            </Link>
            <Link to="/dashboard" className="px-5 py-3 rounded-sm border border-line2 hover:border-ink2 transition-colors">
              View console
            </Link>
          </div>

          <div className="mt-14 grid grid-cols-3 gap-8 max-w-md">
            <div>
              <div className="font-display text-3xl">6.4s</div>
              <div className="text-xs text-ink2 mt-1">Median decision time</div>
            </div>
            <div>
              <div className="font-display text-3xl">99.1%</div>
              <div className="text-xs text-ink2 mt-1">MRZ parse accuracy</div>
            </div>
            <div>
              <div className="font-display text-3xl">180+</div>
              <div className="text-xs text-ink2 mt-1">Document templates</div>
            </div>
          </div>
        </div>

        {/* Subject-grounded hero visual: a document mid-scan */}
        <div className="relative">
          <div className="relative mx-auto w-80 aspect-[16/10] rounded-md border border-line2 bg-panel overflow-hidden scanline-bg">
            <div className="absolute inset-4 border border-dashed border-line2 rounded-sm" />
            <div className="absolute top-6 left-6 h-8 w-8 rounded-full bg-line2" />
            <div className="absolute top-7 left-16 h-2 w-28 bg-line2 rounded-full" />
            <div className="absolute top-11 left-16 h-2 w-20 bg-line2 rounded-full" />
            <div className="absolute bottom-6 left-6 right-6 h-2 bg-line2 rounded-full" />
            <div className="absolute bottom-11 left-6 right-14 h-2 bg-line2 rounded-full" />

            <div
              className="absolute left-0 right-0 h-16 bg-gradient-to-b from-transparent via-signal/25 to-transparent"
              style={{ animation: 'scan 2.8s ease-in-out infinite' }}
            />

            <span className="absolute top-3 right-3 text-[10px] font-mono px-2 py-1 rounded-sm bg-ink/70 border border-line2 text-signal">
              OCR 98%
            </span>
            <span className="absolute bottom-3 right-3 text-[10px] font-mono px-2 py-1 rounded-sm bg-ink/70 border border-line2 text-ink2">
              MRZ verified
            </span>
          </div>
          <style>{`
            @keyframes scan {
              0% { top: -20%; }
              50% { top: 100%; }
              100% { top: -20%; }
            }
          `}</style>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t border-line2">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <h2 className="font-display text-2xl mb-10">Five steps, one decision</h2>
          <div className="grid md:grid-cols-5 gap-6">
            {[
              ['Select document', 'Choose the document type being presented.'],
              ['Upload document', 'Front and back capture of the physical document.'],
              ['Live photo', 'A liveness-checked photo of the person presenting it.'],
              ['Preview', 'Confirm both captures are sharp and complete.'],
              ['Analyse', 'OCR, MRZ, face match and tamper checks run together.'],
            ].map(([title, body], i) => (
              <div key={title} className="border-t border-signal/40 pt-4">
                <div className="font-mono text-xs text-ink2 mb-2">{`0${i + 1}`}</div>
                <div className="font-display text-base mb-1.5">{title}</div>
                <div className="text-sm text-ink2">{body}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="technology" className="border-t border-line2 bg-panel2">
        <div className="max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-12">
          <div>
            <h2 className="font-display text-2xl mb-4">Every check, kept visible</h2>
            <p className="text-ink2 max-w-md">
              Trust scores are built from named signals, not a single opaque model. Reviewers can open
              any verification and see exactly which check pulled the score down.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {['Optical character recognition', 'MRZ checksum validation', 'Biometric face matching', 'Tamper & forgery detection'].map((f) => (
              <div key={f} className="border border-line2 rounded-sm p-4">
                {f}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust */}
      <section id="trust" className="border-t border-line2">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <h2 className="font-display text-2xl mb-4">An audit trail for every decision</h2>
          <p className="text-ink2 max-w-lg mb-8">
            Each verification is hashed and timestamped the moment a decision is made, so the record
            can't be edited after the fact without it being noticed.
          </p>
          <Link to="/verify" className="px-5 py-3 rounded-sm bg-signal text-ink font-medium inline-block hover:bg-signal/90 transition-colors">
            Try a verification
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  )
}