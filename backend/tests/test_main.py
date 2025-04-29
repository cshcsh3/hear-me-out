"""Test cases for the main FastAPI application."""
import os

def test_health(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_transcribe_success(client, mock_transcriber, mock_transcriptions, tmp_path):
    """Test successful transcription."""
    mock_transcriber.transcribe_audio.return_value = "Test transcription"
    mock_transcriptions.create.return_value = "123"
    
    test_file = tmp_path / "test.mp3"
    test_file.touch()
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.mp3", f, "audio/mpeg")})
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "results": [{
            "status": "success",
            "transcription_id": "123",
            "transcription_text": "Test transcription",
            "filename": "test.mp3"
        }]
    }
    # Delete the temporary files
    test_file.unlink()


def test_transcribe_invalid_file_type(client, tmp_path):
    """Test the transcribe endpoint with an invalid file type."""
    test_file = tmp_path / "test.m4a"
    test_file.touch()
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.m4a", f, "audio/m4a")})
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
    # Delete the temporary files
    test_file.unlink()


def test_transcribe_failed(client, mock_transcriber, tmp_path):
    """Test the transcribe endpoint when transcription fails."""
    mock_transcriber.transcribe_audio.return_value = None
    # Create a temporary MP3 file
    test_file = tmp_path / "test.mp3"
    test_file.touch()
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.mp3", f, "audio/mpeg")})
    assert response.status_code == 400
    assert "Audio transcription failed" in response.json()["detail"]
    # Delete the temporary files
    test_file.unlink()


def test_search_transcription_success(client, mock_transcriptions):
    """Test the search transcription endpoint."""
    mock_transcriptions.search.return_value = [{"id": "1", "text": "test"}]
    response = client.get("/transcriptions/search?query=test")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "text": "test"}]


def test_search_transcription_no_results(client, mock_transcriptions):
    """Test the search transcription endpoint with no results."""
    mock_transcriptions.search.return_value = []
    response = client.get("/transcriptions/search?query=test")
    assert response.status_code == 200
    assert response.json() == []


def test_get_transcription_success(client, mock_transcriptions):
    """Test the get transcription endpoint."""
    mock_transcriptions.get.return_value = {"id": "1", "text": "test"}
    response = client.get("/transcriptions/1")
    assert response.status_code == 200
    assert response.json() == {"id": "1", "text": "test"}


def test_get_transcription_not_found(client, mock_transcriptions):
    """Test the get transcription endpoint with a non-existent transcription."""
    mock_transcriptions.get.return_value = None
    response = client.get("/transcriptions/1")
    assert response.status_code == 404
    assert "Transcription not found" in response.json()["detail"]


def test_get_transcription_throws_unexpected_error(client, mock_transcriptions):
    """Test the get transcription endpoint with an error."""
    mock_transcriptions.get.side_effect = Exception("Test error")
    response = client.get("/transcriptions/1")
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]


def test_search_transcription_throws_unexpected_error(client, mock_transcriptions):
    """Test the search transcription endpoint with an error."""
    mock_transcriptions.search.side_effect = Exception("Test error")
    response = client.get("/transcriptions/search?query=test")
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]


def test_transcribe_throws_unexpected_error(client, mock_transcriber, tmp_path):
    """Test the transcribe endpoint with an error."""
    mock_transcriber.transcribe_audio.side_effect = Exception("Test error")
    test_file = tmp_path / "test.mp3"
    test_file.touch()
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.mp3", f, "audio/mpeg")})
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]

    # Delete the temporary files
    test_file.unlink()


def test_transcribe_duplicate_file(client, mock_transcriber, mock_transcriptions, tmp_path):
    """Test the transcribe endpoint with a duplicate file name."""
    # First transcription attempt
    mock_transcriber.transcribe_audio.return_value = "Test transcription"
    mock_transcriptions.create.return_value = "123"
    
    test_file = tmp_path / "test.mp3"
    test_file.touch()
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.mp3", f, "audio/mpeg")})
    assert response.status_code == 200

    # Second attempt with same file name should fail
    mock_transcriptions.create.side_effect = ValueError("A transcription for file 'test.mp3' already exists")
    with open(test_file, "rb") as f:
        response = client.post("/transcribe", files={"files": ("test.mp3", f, "audio/mpeg")})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    # Clean up
    test_file.unlink()
