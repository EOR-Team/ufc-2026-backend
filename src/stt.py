# src/stt.py
# Speech-to-text endpoint - accepts audio upload, converts, and transcribes
#
# @author n1ghts4kura
# @date 2026-04-24

import os
import subprocess
from pathlib import Path
from typing import Annotated

import requests
from fastapi import APIRouter, File, UploadFile, HTTPException

from src.logger import error
from src.whisper_manager import whisper_manager


router = APIRouter()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
TEMP_AUDIO_PATH = "/tmp/voice_input.wav"


class TranscriptionError(Exception):
    """Raised when transcription fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


def convert_audio_to_wav(input_path: str, output_path: str) -> bool:
    """
    Convert audio file to 16kHz mono 16bit WAV using FFmpeg.

    Args:
        input_path: Path to input audio file
        output_path: Path to output WAV file

    Returns:
        True if conversion succeeded, False otherwise
    """
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        output_path,
        "-y",  # overwrite
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        return result.returncode == 0
    except FileNotFoundError:
        error("ffmpeg not found")
        return False
    except subprocess.TimeoutExpired:
        error("ffmpeg conversion timed out")
        return False


def transcribe_audio(audio_path: str) -> str:
    """
    Send audio file to whisper-server and get transcribed text.

    Args:
        audio_path: Path to audio file (16kHz mono WAV)

    Returns:
        Transcribed text string

    Raises:
        TranscriptionError: If transcription fails
    """
    if not whisper_manager.available:
        raise TranscriptionError("whisper service unavailable")

    url = f"http://{whisper_manager.host}:{whisper_manager.port}/inference"

    try:
        with open(audio_path, "rb") as f:
            files = {"file": f}
            resp = requests.post(url, files=files, timeout=30)
    except requests.RequestException as e:
        raise TranscriptionError(f"whisper inference failed: {e}")

    if resp.status_code != 200:
        raise TranscriptionError("whisper inference failed")

    data = resp.json()
    return data.get("text", "")


@router.post("")
async def handle_stt_upload(
    audio: Annotated[UploadFile, File(description="Audio file to transcribe")]
) -> dict:
    """
    Handle audio file upload for speech-to-text transcription.

    Accepts mp3 audio, converts to WAV, sends to whisper-server,
    and returns transcribed text.

    Returns:
        dict with success status and text/error
    """
    # Check if file was provided
    if audio is None:
        return {"success": False, "error": "no audio file provided"}

    # Check file size
    content = await audio.read()
    if len(content) > MAX_FILE_SIZE:
        return {"success": False, "error": "file too large (max 10MB)"}

    # Save uploaded file temporarily
    temp_input = "/tmp/voice_upload.mp3"
    try:
        with open(temp_input, "wb") as f:
            f.write(content)
    except IOError as e:
        return {"success": False, "error": f"failed to save audio: {e}"}

    # Convert to WAV
    if not convert_audio_to_wav(temp_input, TEMP_AUDIO_PATH):
        return {"success": False, "error": "audio conversion failed"}

    # Transcribe
    try:
        text = transcribe_audio(TEMP_AUDIO_PATH)
        return {"success": True, "text": text}
    except TranscriptionError as e:
        return {"success": False, "error": e.message}
    finally:
        # Cleanup temp file
        if os.path.exists(temp_input):
            os.remove(temp_input)


__all__ = [
    "router",
    "TranscriptionError",
    "convert_audio_to_wav",
    "transcribe_audio",
    "handle_stt_upload",
]
