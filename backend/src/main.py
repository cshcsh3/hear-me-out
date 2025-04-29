"""Main FastAPI application module."""

import logging
import tempfile
import traceback
import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transcriber.service import TranscriberService
from transcription.service import TranscriptionsService
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TranscribeRequest(BaseModel):
    """Request model for audio transcription containing the file path."""

    file_path: str


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only allow requests from localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/health")
async def health():
    """Return a simple health check message."""
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(files: List[UploadFile] = File(...)) -> JSONResponse:
    """Transcribe multiple audio files.

    Args:
        files: List of audio files to transcribe

    Returns:
        JSON response with transcription details or error message

    Raises:
        HTTPException: If the file type is invalid, transcription fails, or file already exists
    """
    results = []
    temp_files = []
    temp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            temp_file_path = os.path.join(temp_dir, file.filename)
            temp_files.append(temp_file_path)
            
            # Write the file content to the temporary location
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(await file.read())

            # Validate file type, assumes only MP3 files are supported
            if not temp_file_path.lower().endswith((".mp3")):
                raise HTTPException(
                    status_code=400, detail=f"Invalid file type for {file.filename}. Supported format(s): MP3"
                )

            # Initialize transcriber and process the file
            transcriber = TranscriberService()
            result = transcriber.transcribe_audio(temp_file_path)

            if result is None:
                raise HTTPException(status_code=400, detail=f"Audio transcription failed for {file.filename}")

            results.append({
                "status": "success",
                "transcription_id": result[0],
                "transcription_text": result[1],
                "filename": file.filename
            })

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "results": results
            },
        )

    except ValueError as e:
        # Handle the case where the file already exists
        raise HTTPException(status_code=409, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        error_detail = str(e)
        logger.error(
            "Error in transcription: %s\n%s", error_detail, traceback.format_exc()
        )
        raise HTTPException(status_code=500, detail=error_detail) from e

    finally:
        # Clean up all temporary files and the directory
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@app.get("/transcriptions/search")
async def search_transcription(query: str):
    """Search for transcriptions by query.

    Args:
        query: Search query

    Returns:
        JSON response with list of transcriptions matching the query
    """
    try:
        logger.info("Searching for transcriptions with query: %s", query)
        transcriptions_service = TranscriptionsService()
        transcriptions = transcriptions_service.search(query)

        return JSONResponse(status_code=200, content=transcriptions)
    except Exception as e:
        error_detail = str(e)
        logger.error(
            "Error in searching transcriptions: %s\n%s",
            error_detail,
            traceback.format_exc(),
        )
        raise HTTPException(status_code=500, detail=error_detail) from e


@app.get("/transcriptions/{transcription_id}")
async def get_transcription(transcription_id: str):
    """Get a transcription by ID.

    Args:
        transcription_id: ID of the transcription to retrieve
    """
    try:
        logger.info("Getting transcription with ID: %s", transcription_id)
        transcriptions_service = TranscriptionsService()
        transcription = transcriptions_service.get(transcription_id)

        if transcription is None:
            raise HTTPException(status_code=404, detail="Transcription not found")

        return JSONResponse(status_code=200, content=transcription)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        logger.error(
            "Error in getting transcription: %s\n%s",
            error_detail,
            traceback.format_exc(),
        )
        raise HTTPException(status_code=500, detail=error_detail) from e

@app.get("/transcriptions")
async def get_transcriptions():
    """Get all transcriptions.

    Returns:
        JSON response with list of all transcriptions
    """
    try:
        logger.info("Getting all transcriptions")
        transcriptions_service = TranscriptionsService()
        transcriptions = transcriptions_service.get_all()

        return JSONResponse(status_code=200, content=transcriptions)
    except Exception as e:
        error_detail = str(e)
        logger.error(
            "Error in getting all transcriptions: %s\n%s",
            error_detail,
            traceback.format_exc(),
        )
        raise HTTPException(status_code=500, detail=error_detail) from e
