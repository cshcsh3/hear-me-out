"""Service module for managing transcriptions."""

from typing import Optional, Dict, Any, List
from transcription.repository import TranscriptionsRepository


class TranscriptionsService:
    """Service for managing transcription operations."""

    DEFAULT_DB_PATH = "transcriptions.db"

    def __init__(self):
        """Initialize the service with default database connection."""
        self.repository = TranscriptionsRepository(self.DEFAULT_DB_PATH)

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all transcriptions.

        Returns:
            List of all transcriptions
        """
        return [record.to_dict() for record in self.repository.get_all()]

    def get(self, transcription_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a transcription by ID.

        Args:
            transcription_id: ID of the transcription to retrieve

        Returns:
            Dictionary representation of the transcription if found, None otherwise
        """
        record = self.repository.get(transcription_id)
        return record.to_dict() if record else None

    def create(self, audio_file_name: str, transcription_text: str) -> int:
        """Create a new transcription record.

        Args:
            audio_file_name: Name of the audio file
            transcription_text: The transcribed text content

        Returns:
            ID of the created transcription
        """
        return self.repository.create(audio_file_name, transcription_text)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for transcriptions by query.

        Args:
            query: Search query

        Returns:
            List of transcriptions matching the query
        """
        records = self.repository.search(query)
        return [record.to_dict() for record in records]
