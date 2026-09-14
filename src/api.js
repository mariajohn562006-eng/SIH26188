const API_BASE_URL = 'http://localhost:8000'

export async function startVerification(
  documentFile,
  photoBlob,
  documentType
) {
  const formData = new FormData()

  formData.append('document', documentFile)
  formData.append(
    'photo',
    photoBlob,
    'live-photo.jpg'
  )
if (documentType) {
  formData.append('document_type', documentType)
}
  const response = await fetch(
    `${API_BASE_URL}/api/verification/start`,
    {
      method: 'POST',
      body: formData,
    }
  )

  if (!response.ok) {
    let errorMessage = 'Verification request failed'

    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorMessage
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
    throw new Error('Backend is not available')
  }

  return response.json()
}