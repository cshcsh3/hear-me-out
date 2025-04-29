import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  InputAdornment
} from '@mui/material'
import Grid from '@mui/material/Grid'
import SearchIcon from '@mui/icons-material/Search'
import UploadIcon from '@mui/icons-material/Upload'
import { apiService } from './services/api'

export default function App() {
  // State management
  const [transcriptions, setTranscriptions] = useState([])
  const [filteredTranscriptions, setFilteredTranscriptions] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [error, setError] = useState(null)

  // Fetch transcriptions from API
  useEffect(() => {
    const fetchTranscriptions = async () => {
      try {
        setIsLoading(true)
        const response = await apiService.getTranscriptions()
        setTranscriptions(response.data)
        setFilteredTranscriptions(response.data)
      } catch (err) {
        setError(err.message)
        console.error('Error fetching transcriptions:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchTranscriptions()
  }, [])

  // Search functionality
  // Only start searching with minimum 3 characters with 500ms debounce delay to reduce API calls
  useEffect(() => {
    const debounceTimeout = setTimeout(() => {
      if (searchTerm.trim() === '' || searchTerm.trim().length < 3) {
        setFilteredTranscriptions(transcriptions)
      } else {
        const searchTranscriptions = async () => {
          try {
            setIsLoading(true)
            const response = await apiService.searchTranscriptions(searchTerm)
            setFilteredTranscriptions(response.data)
          } catch (err) {
            setError(err.message)
            console.error('Error searching transcriptions:', err)
          } finally {
            setIsLoading(false)
          }
        }
        searchTranscriptions()
      }
    }, 500) // 500ms debounce delay

    return () => clearTimeout(debounceTimeout)
  }, [searchTerm, transcriptions])

  // Handle file upload
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setUploadedFile(Array.from(e.target.files))
    }
  }

  const handleFileUpload = async () => {
    if (uploadedFile && uploadedFile.length > 0) {
      try {
        setIsLoading(true)

        // Transcribe the uploaded files
        await apiService.transcribe(uploadedFile)
        setSuccessMessage(
          `${uploadedFile.length} file(s) transcribed successfully!`
        )

        // Refresh transcriptions after successful upload and transcription
        const transcriptionsResponse = await apiService.getTranscriptions()
        setTranscriptions(transcriptionsResponse.data)
        setFilteredTranscriptions(transcriptionsResponse.data)
      } catch (err) {
        setError(err.message)
        console.error('Error processing files:', err)
      } finally {
        setIsLoading(false)
        setUploadedFile(null)
        setTimeout(() => {
          setSuccessMessage('')
          setError(null)
        }, 10000)
      }
    }
  }

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date)
  }

  const fileInputRef = useRef(null)

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          color="primary"
          fontWeight="bold"
        >
          Hear Me Out
        </Typography>

        {/* Error message */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Success message */}
        {successMessage && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {successMessage}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mb: 4 }}>
          {/* Search */}
          <Grid size={{ xs: 12, sm: 8 }}>
            <TextField
              fullWidth
              placeholder="Search transcriptions"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon size={20} />
                  </InputAdornment>
                )
              }}
            />
          </Grid>

          {/* File upload */}
          <Grid size={{ xs: 12, sm: 4 }}>
            <Box sx={{ display: 'flex' }}>
              <TextField
                fullWidth
                value={
                  uploadedFile ? `${uploadedFile.length} file(s) selected` : ''
                }
                placeholder="Select audio files"
                disabled
                variant="outlined"
              />
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                hidden
                multiple
                onChange={handleFileChange}
                data-testid="file-input"
              />
              <Button
                variant="contained"
                onClick={() => fileInputRef.current.click()}
                sx={{ ml: 1, minWidth: 'auto', px: 2 }}
              >
                <SearchIcon size={20} />
              </Button>
              <Button
                variant="contained"
                color="primary"
                disabled={!uploadedFile || uploadedFile.length === 0}
                onClick={handleFileUpload}
                sx={{ ml: 1, minWidth: 'auto', px: 2 }}
                data-testid="upload-button"
              >
                <UploadIcon size={20} />
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Records table */}
        <Paper elevation={2}>
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Audio File</TableCell>
                    <TableCell sx={{ width: '50%' }}>Transcription</TableCell>
                    <TableCell>Created At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredTranscriptions.length > 0 ? (
                    filteredTranscriptions.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell>{record.id}</TableCell>
                        <TableCell>{record.audio_file_name}</TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {record.transcribed_text}
                          </Typography>
                        </TableCell>
                        <TableCell>{formatDate(record.created_at)}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                        <Typography variant="body1" color="text.secondary">
                          No records found. Try a different search term.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Container>
    </Box>
  )
}
