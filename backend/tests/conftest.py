"""Pytest configuration and fixtures for FastAPI application tests."""

from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def mock_transcriber():
    """Create a mock transcriber service."""
    with patch("src.main.TranscriberService") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_transcriptions():
    """Create a mock transcriptions service."""
    with patch("src.main.TranscriptionsService") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def client(mock_transcriber, mock_transcriptions):
    """Create a test client for the FastAPI application with mocked services."""
    # Override the app's dependencies with our mocks
    app.dependency_overrides = {
        "get_transcriber": lambda: mock_transcriber,
        "get_transcriptions_service": lambda: mock_transcriptions
    }
    return TestClient(app)
