"""Service module for audio transcription using OpenAI's Whisper model."""

from typing import Optional
import logging
import librosa
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Configure logging
logger = logging.getLogger(__name__)


class TranscriberService:
    """Service for handling audio transcription operations using OpenAI/Whisper-tiny model."""

    MODEL_ID = "openai/whisper-tiny"

    def __init__(self, language: str = "en"):
        """Initialize the transcriber service with Whisper-tiny model.

        Args:
            language: Language code for transcription (default: "en" for English)
        """
        self.processor = WhisperProcessor.from_pretrained(self.MODEL_ID)
        self.model = WhisperForConditionalGeneration.from_pretrained(self.MODEL_ID)
        # Check if GPU is available and move model to GPU if possible
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.language = language


    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file to text and store in database.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (transcription_id, transcribed_text) or None if transcription fails
        """
        try:
            # Load and preprocess the audio
            input_features = self._preprocess_audio(audio_path)

            # Generate transcription with language and attention mask
            predicted_ids = self.model.generate(
                input_features,
                language=self.language,
                task="transcribe",
                return_timestamps=False,
            )

            # Decode the transcription
            transcribed_text = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )[0]

            return transcribed_text
        except Exception as e:
            self._handle_error(e)

    def _preprocess_audio(self, audio_path: str, sample_rate: int = 16000) -> torch.Tensor:
        """Preprocess audio file for transcription.

        Args:
            audio_path: Path to the audio file

        Returns:
            Processed audio features as tensor
        """
        try:
            # Load the audio file 
            audio_data, sampling_rate = librosa.load(audio_path, sr=sample_rate)

            # Process audio input with the Whisper processor
            input_features = self.processor(
                audio_data,
                sampling_rate=sampling_rate,
                return_tensors="pt"
            ).input_features
            
            # Move to appropriate device
            input_features = input_features.to(self.device)
            return input_features
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise

    def _handle_error(self, error: Exception):
        """Handle transcription errors."""
        logger.error("Error transcribing audio: %s", error)
        raise error
