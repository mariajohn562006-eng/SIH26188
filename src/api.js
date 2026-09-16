const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

function getErrorMessage(
  errorData,
  fallback = 'Verification request failed'
) {
  if (!errorData) {
    return fallback
  }

  // FastAPI detail can be a string
  if (typeof errorData.detail === 'string') {
    return errorData.detail
  }

  // FastAPI detail can be an object or array
  if (
    errorData.detail &&
    typeof errorData.detail === 'object'
  ) {
    // Object with a message field
    if (
      typeof errorData.detail.message === 'string'
    ) {
      return errorData.detail.message
    }

    // Object with an error field
    if (
      typeof errorData.detail.error === 'string'
    ) {
      return errorData.detail.error
    }

    // Validation errors or other structured details
    return JSON.stringify(
      errorData.detail,
      null,
      2
    )
  }

  // Other possible API error formats
  if (typeof errorData.message === 'string') {
    return errorData.message
  }

  return fallback
}

export async function startVerification(
  documentFile,
  photoBlob,
  documentType
) {
  const formData = new FormData()

  // Document upload
  formData.append(
    'document',
    documentFile
  )

  // Live photo upload
  // IMPORTANT:
  // The FastAPI backend expects the field name "live_photo"
  formData.append(
    'live_photo',
    photoBlob,
    'live-photo.jpg'
  )

  // Optional document type
  if (documentType) {
    formData.append(
      'document_type',
      documentType
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/api/verification/start`,
    {
      method: 'POST',
      body: formData,
    }
  )

  if (!response.ok) {
    let errorMessage =
      'Verification request failed'

    try {
      const errorData =
        await response.json()

      errorMessage =
        getErrorMessage(errorData)
    } catch {
      // Ignore JSON parsing errors
    }

    throw new Error(errorMessage)
  }

  return response.json()
}

export async function checkBackendHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  )

  if (!response.ok) {
    throw new Error(
      'Backend is not available'
    )
  }

  return response.json()
}