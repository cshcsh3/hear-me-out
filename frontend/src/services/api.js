import axios from 'axios'

// Create an axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001', // FastAPI default port
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add a response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      let errorMessage = 'An error occurred'

      switch (status) {
        case 409:
          errorMessage =
            data.detail ||
            'A conflict occurred with the current state of the resource'
          break
        case 400:
          errorMessage = data.detail || 'Invalid request'
          break
        case 404:
          errorMessage = data.detail || 'Resource not found'
          break
        case 500:
          errorMessage = data.detail || 'Internal server error'
          break
        default:
          errorMessage = data.detail || 'An unexpected error occurred'
      }

      console.error('API Error:', errorMessage)
      error.message = errorMessage
    } else if (error.request) {
      console.error('Network Error:', error.request)
      error.message = 'Network error. Please check your connection.'
    } else {
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// API service matching FastAPI backend endpoints
export const apiService = {
  // Health check
  health: () => api.get('/health'),

  // Transcribe audio file(s)
  transcribe: (files) => {
    const formData = new FormData()
    // Handle both single file and array of files
    if (Array.isArray(files)) {
      files.forEach((file) => {
        formData.append('files', file)
      })
    } else {
      formData.append('files', files)
    }
    return api.post('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Get all transcriptions
  getTranscriptions: () => api.get('/transcriptions'),

  // Get a specific transcription by ID
  getTranscription: (transcriptionId) =>
    api.get(`/transcriptions/${transcriptionId}`),

  // Search transcriptions
  searchTranscriptions: (query) =>
    api.get('/transcriptions/search', { params: { query } })
}

export default api
