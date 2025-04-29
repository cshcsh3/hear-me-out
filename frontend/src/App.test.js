import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import App from './App'
import { apiService } from './services/api'

// Mock timers
jest.useFakeTimers()

// Mock the API service
jest.mock('./services/api', () => ({
  apiService: {
    getTranscriptions: jest.fn(),
    searchTranscriptions: jest.fn(),
    transcribe: jest.fn()
  }
}))

describe('App Component', () => {
  const mockTranscriptions = [
    {
      id: 1,
      audio_file_name: 'test1.mp3',
      transcribed_text: 'This is a test transcription',
      created_at: '2024-01-01T12:00:00Z'
    },
    {
      id: 2,
      audio_file_name: 'test2.mp3',
      transcribed_text: 'Another test transcription',
      created_at: '2024-01-02T12:00:00Z'
    }
  ]

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks()
    apiService.getTranscriptions.mockResolvedValue({ data: mockTranscriptions })
    apiService.searchTranscriptions.mockResolvedValue({
      data: [mockTranscriptions[0]]
    })
    apiService.transcribe.mockResolvedValue({})
  })

  afterEach(() => {
    // Clear all timers after each test
    jest.clearAllTimers()
  })

  test('renders the app title', async () => {
    await act(async () => {
      render(<App />)
    })
    const titleElement = screen.getByText(/Hear Me Out/i)
    expect(titleElement).toBeInTheDocument()
  })

  test('loads and displays transcriptions', async () => {
    await act(async () => {
      render(<App />)
    })

    // Wait for transcriptions to load
    await waitFor(() => {
      expect(screen.getByText('test1.mp3')).toBeInTheDocument()
      expect(screen.getByText('test2.mp3')).toBeInTheDocument()
    })
  })

  test('handles search functionality', async () => {
    await act(async () => {
      render(<App />)
    })

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('test1.mp3')).toBeInTheDocument()
    })

    // Enter search term
    const searchInput = screen.getByPlaceholderText(/Search transcriptions/i)
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'test1' } })
    })

    // Wait for search results
    await waitFor(() => {
      expect(apiService.searchTranscriptions).toHaveBeenCalledWith('test1')
      expect(screen.getByText('test1.mp3')).toBeInTheDocument()
      expect(screen.queryByText('test2.mp3')).not.toBeInTheDocument()
    })
  })

  test('handles file upload', async () => {
    render(<App />)

    // Create mock files
    const files = [
      new File(['test1'], 'test1.mp3', { type: 'audio/mp3' }),
      new File(['test2'], 'test2.mp3', { type: 'audio/mp3' })
    ]

    // Get the file input and upload button
    const fileInput = screen.getByTestId('file-input')
    const uploadButton = screen.getByTestId('upload-button')

    // Simulate file selection
    fireEvent.change(fileInput, { target: { files } })

    // Verify files are selected
    expect(screen.getByDisplayValue('2 file(s) selected')).toBeInTheDocument()

    // Click upload button
    fireEvent.click(uploadButton)

    // Check if transcribe was called with the correct files
    await waitFor(() => {
      expect(apiService.transcribe).toHaveBeenCalledWith(files)
    })

    // Verify success message
    await waitFor(() => {
      expect(
        screen.getByText('2 file(s) transcribed successfully!')
      ).toBeInTheDocument()
    })

    // Verify transcriptions are refreshed
    await waitFor(() => {
      expect(apiService.getTranscriptions).toHaveBeenCalled()
    })
  })
})
