"""Repository module for managing transcription data."""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List


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
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create the transcriptions table if it doesn't exist."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audio_file_name TEXT NOT NULL UNIQUE,
                transcribed_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.conn.commit()

    def get_all(self) -> List[TranscriptionRecord]:
        """Retrieve all transcriptions.

        Returns:
            List of all transcriptions
        """
        self.cursor.execute("SELECT * FROM transcriptions")
        rows = self.cursor.fetchall()
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
        self.cursor.execute("SELECT * FROM transcriptions WHERE id = ?", (id,))
        row = self.cursor.fetchone()
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
        try:
            self.cursor.execute(
                "INSERT INTO transcriptions (audio_file_name, transcribed_text) VALUES (?, ?)",
                (audio_file_name, transcribed_text),
            )
            self.conn.commit()
            return self.cursor.lastrowid
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
        self.cursor.execute(
            "SELECT * FROM transcriptions WHERE LOWER(transcribed_text) LIKE LOWER(?) OR LOWER(audio_file_name) LIKE LOWER(?)",
            (f"%{query}%", f"%{query}%"),
        )
        rows = self.cursor.fetchall()
        return [
            TranscriptionRecord(
                record_id=row[0],
                audio_file_name=row[1],
                transcribed_text=row[2],
                created_at=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]
