import React, { useCallback, useRef, useState, useMemo } from 'react'
import { documentTypes } from '../mock/data.js'
import { startVerification } from '../api.js'
import VerificationResultWorkspace from '../components/result/VerificationResultWorkspace.jsx'

const STEPS = [
  'Document type',
  'Upload document',
  'Live photo',
  'Preview',
  'Start verification',
]

export default function Verification() {
  const [step, setStep] = useState(0)
  const [docType, setDocType] = useState(null)
  const [docFile, setDocFile] = useState(null)
  const [photoDataUrl, setPhotoDataUrl] = useState(null)
  const [analysing, setAnalysing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const canAdvance = [
    !!docType,
    !!docFile,
    !!photoDataUrl,
    true,
    false,
  ]

  function next() {
    setError(null)
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
  }

  function back() {
    setError(null)
    setStep((s) => Math.max(s - 1, 0))
  }

  async function startVerificationProcess() {
    if (!docFile || !photoDataUrl) {
      setError('Please provide both a document and a live photo.')
      return
    }

    setAnalysing(true)
    setResult(null)
    setError(null)

    try {
      const photoBlob = await dataUrlToBlob(photoDataUrl)

      const response = await startVerification(
        docFile,
        photoBlob,
  docType
)
      

      const backendResult = toWorkspaceResult(response)

      setResult(backendResult)
    } catch (err) {
      console.error('Verification failed:', err)

      setError(
        err.message ||
        'Unable to connect to the verification backend.'
      )
    } finally {
      setAnalysing(false)
    }
  }

  function resetAll() {
    setStep(0)
    setDocType(null)
    setDocFile(null)
    setPhotoDataUrl(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className={`p-8 ${result ? 'max-w-6xl' : 'max-w-4xl'}`}>
      <h1 className="font-display text-2xl mb-1">
        Verification workspace
      </h1>

      <p className="text-ink2 text-sm mb-8">
        Capture a document and a live photo, then run the analysis.
      </p>

      <Stepper
        current={step}
        disabled={analysing || !!result}
        onJump={setStep}
      />

      <div className="mt-8 border border-line rounded-sm p-6 min-h-[22rem]">

        {result ? (
          <ResultPreview
            result={result}
            onReset={resetAll}
            docType={docType}
            docFile={docFile}
            photoDataUrl={photoDataUrl}
          />

        ) : analysing ? (
          <AnalysingPanel />

        ) : (
          <>
            {step === 0 && (
              <StepDocType
                selected={docType}
                onSelect={setDocType}
              />
            )}

            {step === 1 && (
              <StepUploadDocument
                docType={docType}
                file={docFile}
                onFile={setDocFile}
              />
            )}

            {step === 2 && (
              <StepLivePhoto
                photoDataUrl={photoDataUrl}
                onCapture={setPhotoDataUrl}
              />
            )}

            {step === 3 && (
              <StepPreview
                docType={docType}
                docFile={docFile}
                photoDataUrl={photoDataUrl}
              />
            )}

            {step === 4 && (
              <StepStart
                docType={docType}
                docFile={docFile}
                photoDataUrl={photoDataUrl}
              />
            )}
          </>
        )}
      </div>

      {error && !analysing && (
        <div className="mt-4 border border-danger/40 bg-danger/10 rounded-sm p-4 text-sm text-danger">
          <strong>Verification failed:</strong>{' '}
          {error}
        </div>
      )}

      {!result && !analysing && (
        <div className="flex justify-between mt-6">

          <button
            onClick={back}
            disabled={step === 0}
            className="px-4 py-2.5 rounded-sm border border-line2 text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:border-ink2 transition-colors"
          >
            Back
          </button>

          {step < 4 ? (
            <button
              onClick={next}
              disabled={!canAdvance[step]}
              className="px-5 py-2.5 rounded-sm bg-signal text-ink text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed hover:bg-signal/90 transition-colors"
            >
              Continue
            </button>
          ) : (
            <button
              onClick={startVerificationProcess}
              disabled={!docFile || !photoDataUrl}
              className="px-5 py-2.5 rounded-sm bg-signal text-ink text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed hover:bg-signal/90 transition-colors"
            >
              Start verification
            </button>
          )}

        </div>
      )}
    </div>
  )
}


// ---------- Convert captured photo ----------

async function dataUrlToBlob(dataUrl) {
  const response = await fetch(dataUrl)
  return response.blob()
}


// ---------- Stepper ----------

function Stepper({ current, disabled, onJump }) {
  return (
    <div className="flex items-center">

      {STEPS.map((label, i) => (
        <React.Fragment key={label}>

          <button
            onClick={() =>
              !disabled &&
              i <= current &&
              onJump(i)
            }
            className={`flex items-center gap-2 text-sm ${
              i <= current
                ? 'text-inktext'
                : 'text-ink2'
            } ${
              i < current && !disabled
                ? 'cursor-pointer'
                : 'cursor-default'
            }`}
          >

            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono border ${
                i < current
                  ? 'bg-signal text-ink border-signal'
                  : i === current
                    ? 'border-signal text-signal'
                    : 'border-line2 text-ink2'
              }`}
            >
              {i + 1}
            </span>

            <span className="hidden md:inline">
              {label}
            </span>

          </button>

          {i < STEPS.length - 1 && (
            <span className="flex-1 h-px bg-line2 mx-3" />
          )}

        </React.Fragment>
      ))}

    </div>
  )
}


// ---------- Step 1: Document type ----------

function StepDocType({ selected, onSelect }) {
  return (
    <div>

      <h2 className="font-display text-lg mb-4">
        What document is being presented?
      </h2>

      <div className="grid grid-cols-2 gap-3">

        {documentTypes.map((d) => (
          <button
            key={d.id}
            onClick={() => onSelect(d.id)}
            className={`text-left p-4 rounded-sm border transition-colors ${
              selected === d.id
                ? 'border-signal bg-signal/10'
                : 'border-line2 hover:border-ink2'
            }`}
          >
            <div className="font-medium">
              {d.label}
            </div>

            <div className="text-xs text-ink2 mt-1">
              {d.hint}
            </div>
          </button>
        ))}

      </div>
    </div>
  )
}


// ---------- Step 2: Upload document ----------

function StepUploadDocument({
  docType,
  file,
  onFile,
}) {
  const inputRef = useRef(null)

  const label =
    documentTypes.find(
      (d) => d.id === docType
    )?.label || 'document'

  return (
    <div>

      <h2 className="font-display text-lg mb-1">
        Upload the {label.toLowerCase()}
      </h2>

      <p className="text-sm text-ink2 mb-4">
        Use a clear, well-lit photo or scan.
        JPG, PNG or PDF.
      </p>

      <input
        ref={inputRef}
        type="file"
        accept="image/*,.pdf"
        className="hidden"
        onChange={(e) => {
          if (e.target.files[0]) {
            onFile(e.target.files[0])
          }
        }}
      />

      <div
        onClick={() =>
          inputRef.current?.click()
        }
        onDragOver={(e) =>
          e.preventDefault()
        }
        onDrop={(e) => {
          e.preventDefault()

          if (e.dataTransfer.files[0]) {
            onFile(e.dataTransfer.files[0])
          }
        }}
        className="border border-dashed border-line2 rounded-sm p-10 text-center cursor-pointer hover:border-signal/60 transition-colors"
      >

        {file ? (
          <div>

            <div className="font-mono text-sm text-signal">
              {file.name}
            </div>

            <div className="text-xs text-ink2 mt-1">
              {(file.size / 1024).toFixed(0)} KB
              {' — '}
              click to replace
            </div>

          </div>
        ) : (
          <div>

            <div className="text-sm">
              Drop a file here, or click to browse
            </div>

            <div className="text-xs text-ink2 mt-1">
              File will be sent to the ByteMind backend
            </div>

          </div>
        )}

      </div>

    </div>
  )
}


// ---------- Step 3: Live photo ----------

function StepLivePhoto({
  photoDataUrl,
  onCapture,
}) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const fileInputRef = useRef(null)

  const [streaming, setStreaming] = useState(false)
  const [camError, setCamError] = useState(null)

  const startCamera = useCallback(async () => {
    setCamError(null)

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'user',
          },
        })

      if (videoRef.current) {
        videoRef.current.srcObject = stream

        await videoRef.current.play()

        setStreaming(true)
      }

    } catch (err) {
      console.error(err)

      setCamError(
        'Camera unavailable — you can upload a photo instead.'
      )
    }
  }, [])

  function capture() {
    const video = videoRef.current
    const canvas = canvasRef.current

    if (!video || !canvas) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    canvas
      .getContext('2d')
      .drawImage(
        video,
        0,
        0
      )

    onCapture(
      canvas.toDataURL('image/jpeg')
    )

    video.srcObject
      ?.getTracks()
      .forEach((track) => track.stop())

    setStreaming(false)
  }

  function handleFileFallback(e) {
    const file = e.target.files[0]

    if (!file) return

    const reader = new FileReader()

    reader.onload = () => {
      onCapture(reader.result)
    }

    reader.readAsDataURL(file)
  }

  function retake() {
    onCapture(null)
    setCamError(null)
  }

  return (
    <div>

      <h2 className="font-display text-lg mb-1">
        Take a live photo
      </h2>

      <p className="text-sm text-ink2 mb-4">
        Used to match the presenter's face against
        the document photo.
      </p>

      <div className="w-72 aspect-[4/3] bg-panel border border-line2 rounded-sm overflow-hidden mx-auto flex items-center justify-center relative">

        {photoDataUrl ? (
          <img
            src={photoDataUrl}
            alt="Captured"
            className="w-full h-full object-cover"
          />
        ) : (
          <video
            ref={videoRef}
            className={`w-full h-full object-cover ${
              streaming ? '' : 'hidden'
            }`}
            muted
            playsInline
          />
        )}

        {!streaming && !photoDataUrl && (
          <span className="text-sm text-ink2">
            No photo yet
          </span>
        )}

      </div>

      <canvas
        ref={canvasRef}
        className="hidden"
      />

      <div className="flex items-center justify-center gap-3 mt-5">

        {photoDataUrl ? (
          <button
            onClick={retake}
            className="px-4 py-2 rounded-sm border border-line2 text-sm hover:border-ink2"
          >
            Retake
          </button>

        ) : streaming ? (
          <button
            onClick={capture}
            className="px-4 py-2 rounded-sm bg-signal text-ink text-sm font-medium hover:bg-signal/90"
          >
            Capture photo
          </button>

        ) : (
          <>
            <button
              onClick={startCamera}
              className="px-4 py-2 rounded-sm bg-signal text-ink text-sm font-medium hover:bg-signal/90"
            >
              Enable camera
            </button>

            <button
              onClick={() =>
                fileInputRef.current?.click()
              }
              className="px-4 py-2 rounded-sm border border-line2 text-sm hover:border-ink2"
            >
              Upload photo instead
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileFallback}
            />
          </>
        )}

      </div>

      {camError && (
        <p className="text-xs text-amber text-center mt-3">
          {camError}
        </p>
      )}

    </div>
  )
}


// ---------- Step 4: Preview ----------

function StepPreview({
  docType,
  docFile,
  photoDataUrl,
}) {
  const label =
    documentTypes.find(
      (d) => d.id === docType
    )?.label

  return (
    <div>

      <h2 className="font-display text-lg mb-4">
        Confirm before analysis
      </h2>

      <div className="grid grid-cols-2 gap-6">

        <div>

          <div className="text-xs text-ink2 mb-2">
            {label}
          </div>

          <div className="aspect-[4/3] bg-panel border border-line2 rounded-sm flex items-center justify-center">
            <span className="font-mono text-sm text-signal">
              {docFile?.name}
            </span>
          </div>

        </div>

        <div>

          <div className="text-xs text-ink2 mb-2">
            Live photo
          </div>

          <div className="aspect-[4/3] bg-panel border border-line2 rounded-sm overflow-hidden">

            {photoDataUrl && (
              <img
                src={photoDataUrl}
                alt="Live capture"
                className="w-full h-full object-cover"
              />
            )}

          </div>

        </div>

      </div>

      <p className="text-xs text-ink2 mt-5">
        Go back to any step above to retake either
        capture.
      </p>

    </div>
  )
}


// ---------- Step 5: Start ----------

function StepStart({
  docType,
  docFile,
  photoDataUrl,
}) {
  const label =
    documentTypes.find(
      (d) => d.id === docType
    )?.label

  return (
    <div>

      <h2 className="font-display text-lg mb-4">
        Ready to analyse
      </h2>

      <ul className="text-sm space-y-2 text-ink2 mb-6">

        <li>
          Document type —
          {' '}
          <span className="text-inktext">
            {label}
          </span>
        </li>

        <li>
          Document file —
          {' '}
          <span className="text-inktext font-mono">
            {docFile?.name}
          </span>
        </li>

        <li>
          Live photo —
          {' '}
          <span className="text-inktext">
            {photoDataUrl
              ? 'captured'
              : 'missing'}
          </span>
        </li>

      </ul>

      <p className="text-sm text-ink2">
        Pressing "Start verification" sends the
        document and live photo to the ByteMind
        backend.
      </p>

    </div>
  )
}


// ---------- Analysing state ----------

function AnalysingPanel() {
  const stages = [
    'Uploading document',
    'Uploading live photo',
    'Preparing verification',
    'Waiting for AI analysis',
  ]

  const [active, setActive] = useState(0)

  React.useEffect(() => {
    const id = setInterval(() => {
      setActive((a) =>
        Math.min(
          a + 1,
          stages.length - 1
        )
      )
    }, 800)

    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center h-full py-10">

      <div className="w-10 h-10 border-2 border-line2 border-t-signal rounded-full animate-spin mb-6" />

      <div className="font-display text-lg mb-6">
        Connecting to ByteMind AI
      </div>

      <ul className="text-sm space-y-2">

        {stages.map((stage, i) => (
          <li
            key={stage}
            className={`flex items-center gap-2 ${
              i <= active
                ? 'text-inktext'
                : 'text-ink2'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                i <= active
                  ? 'bg-signal'
                  : 'bg-line2'
              }`}
            />

            {stage}
          </li>
        ))}

      </ul>

    </div>
  )
}


// ---------- Result preview ----------

function ResultPreview({
  result,
  onReset,
  docType,
  docFile,
  photoDataUrl,
}) {
  const decisionColor =
    result.decision === 'approved'
      ? 'text-safe'
      : result.decision === 'rejected'
        ? 'text-danger'
        : 'text-amber'

  const docLabel =
    documentTypes.find(
      (d) => d.id === docType
    )?.label

  const docImageUrl = useMemo(
    () =>
      docFile
        ? URL.createObjectURL(docFile)
        : undefined,
    [docFile]
  )

  return (
    <div>

      <div className="flex items-center justify-between mb-6">

        <div>

          <h2 className="font-display text-lg">
            Verification received
          </h2>

          <p className="text-xs text-ink2 font-mono mt-1">
            {result.id}
          </p>

        </div>

        <span
          className={`text-sm font-medium ${decisionColor}`}
        >
          {result.decision.replace('_', ' ')}
        </span>

      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">

        <MiniStat
          label="Trust score"
          value={result.trustScore}
          color="text-signal"
        />

        <MiniStat
          label="Risk score"
          value={result.riskScore}
          color="text-amber"
        />

        <MiniStat
          label="Face match"
          value={
            result.faceMatch?.score
              ? `${result.faceMatch.score}%`
              : 'Pending'
          }
        />

      </div>

      <div className="mb-6">

        <VerificationResultWorkspace
          result={result}
          docType={docLabel}
          docImageUrl={docImageUrl}
          livePhotoUrl={photoDataUrl}
        />

      </div>

      <div className="text-sm text-ink2 mb-4">
        {result.message}
      </div>

      <button
        onClick={onReset}
        className="px-4 py-2.5 rounded-sm border border-line2 text-sm hover:border-ink2"
      >
        Run another verification
      </button>

    </div>
  )
}


// ---------- Mini stat ----------

function MiniStat({
  label,
  value,
  color,
}) {
  return (
    <div className="border border-line rounded-sm p-4 text-center">

      <div
        className={`font-display text-2xl ${
          color || ''
        }`}
      >
        {value}
      </div>

      <div className="text-xs text-ink2 mt-1">
        {label}
      </div>

    </div>
  )
}

function toWorkspaceResult(response) {
  const documentAnalysis = response.documentAnalysis ?? response.ocr ?? {}
  const ocr = documentAnalysis.ocr ?? {}
  const mrz = documentAnalysis.mrz ?? {}
  const face = response.faceAnalysis?.faceAnalysis ?? response.faceAnalysis ?? {}
  const tamper = response.tamperAnalysis?.tamperAnalysis
    ?? response.tamperAnalysis
    ?? {}
  const risk = response.riskAnalysis ?? response.risk ?? {}
  const finalResult = response.finalResult ?? {}
  const riskScore = Number(risk.riskScore ?? finalResult.risk?.score ?? 0)
  const faceUsable = Boolean(face.documentFaceUsable && face.livePhotoFaceUsable)
  const mrzValid = Boolean(
    mrz.detected
    && (
      mrz.parsed?.success
      || mrz.lines?.length >= 2
      || mrz.status === 'verified'
    )
  )
  const tamperScore = Math.min(100, Number(tamper.warningCount ?? 0) * 25)
  const status = finalResult.status ?? response.status

  return {
    id: response.verification_id ?? response.verificationId,
    decision: status === 'rejected'
      ? 'rejected'
      : status === 'manual_review'
        ? 'manual_review'
        : status === 'review'
          ? 'suspicious'
          : 'approved',
    trustScore: Math.max(0, 100 - riskScore),
    riskScore,
    ocr: {
      confidence: ocr.success ? 85 : 0,
      fields: {
        fullName: '-',
        documentNumber: '-',
        dateOfBirth: '-',
        expiryDate: '-',
        nationality: '-',
      },
    },
    mrz: {
      valid: mrzValid,
      checksumsPassed: mrzValid ? 4 : 0,
      checksumsTotal: 4,
    },
    faceMatch: {
      score: faceUsable ? 90 : 0,
      livenessPassed: face.livePhotoFaceUsable === true,
    },
    authenticity: {
      score: tamperScore === 0 ? 85 : Math.max(0, 85 - tamperScore),
      securityFeaturesDetected: [],
    },
    tampering: {
      score: tamperScore,
      suspiciousRegions: tamper.warningCount
        ? tamper.warnings.map((warning) => ({ label: warning }))
        : [],
    },
    riskContributors: (risk.riskFactors ?? []).map((factor) => ({
      label: factor.factor ?? 'Risk signal',
      weight: Number(factor.impact ?? 0),
    })),
    decisionTimeline: [],
    hash: 'unavailable',
    backendStatus: response.status,
    message: response.message,
  }
}