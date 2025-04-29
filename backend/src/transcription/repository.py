"""Repository module for managing transcription data."""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


class TranscriptionRecord:
    """Represents a transcription record."""

    def __init__(
        self,
        record_id: int,
        audio_file_name: str,
        transcribed_text: str,
        created_at: datetime,
    ):
        self.record_id = record_id
        self.audio_file_name = audio_file_name
        self.transcribed_text = transcribed_text
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary.

        Returns:
            Dictionary representation of the record
        """
        return {
            "id": self.record_id,
            "audio_file_name": self.audio_file_name,
            "transcribed_text": self.transcribed_text,
            "created_at": self.created_at.isoformat(),
        }


class TranscriptionsRepository:
    """Repository for managing transcription data"""

    def __init__(self, db_path: str):
        """Initialize the repository with database connection."""
        self.db_path = db_path
        self._create_table()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path, timeout=30)  # Add timeout to handle locks
        try:
            yield conn
        finally:
            conn.close()

    def _create_table(self):
        """Create the transcriptions table if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audio_file_name TEXT NOT NULL UNIQUE,
                    transcribed_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

    def get_all(self) -> List[TranscriptionRecord]:
        """Retrieve all transcriptions.

        Returns:
            List of all transcriptions
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transcriptions")
            rows = cursor.fetchall()
            return [
                TranscriptionRecord(
                    record_id=row[0],
                    audio_file_name=row[1],
                    transcribed_text=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                )
                for row in rows
            ]

    def get(self, id: int) -> Optional[TranscriptionRecord]:
        """Retrieve a transcription by ID.

        Args:
            id: ID of the transcription to retrieve

        Returns:
            Transcription record if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transcriptions WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return TranscriptionRecord(
                record_id=row[0],
                audio_file_name=row[1],
                transcribed_text=row[2],
                created_at=datetime.fromisoformat(row[3]),
            )

    def create(self, audio_file_name: str, transcribed_text: str) -> int:
        """Create a new transcription record.

        Args:
            audio_file_name: Name of the audio file
            transcribed_text: The transcribed text content

        Returns:
            ID of the created transcription

        Raises:
            sqlite3.IntegrityError: If a transcription with the same audio_file_name already exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO transcriptions (audio_file_name, transcribed_text) VALUES (?, ?)",
                    (audio_file_name, transcribed_text),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    raise ValueError(f"A transcription for file '{audio_file_name}' already exists")
                raise

    def search(self, query: str) -> List[TranscriptionRecord]:
        """Search for transcriptions by query.

        Args:
            query: Search query

        Returns:
            List of transcriptions matching the query
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Assume simple LIKE search is sufficient
            cursor.execute(
                "SELECT * FROM transcriptions WHERE LOWER(transcribed_text) LIKE LOWER(?) OR LOWER(audio_file_name) LIKE LOWER(?)",
                (f"%{query}%", f"%{query}%"),
            )
            rows = cursor.fetchall()
            return [
                TranscriptionRecord(
                    record_id=row[0],
                    audio_file_name=row[1],
                    transcribed_text=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                )
                for row in rows
            ]
