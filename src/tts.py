# src/tts.py
# TTS endpoint for Piper text-to-speech synthesis
#
# @author n1ghts4kura
# @date 2026-04-25

from fastapi import APIRouter
from pydantic import BaseModel

from src.piper_tts_service import piper_tts_service


router = APIRouter()


class TTSRequest(BaseModel):
    text: str


@router.post("")
def tts_endpoint(request: TTSRequest) -> dict:
    """
    Synthesize text to audio using Piper TTS.

    Args:
        request: TTSRequest with text

    Returns:
        JSON with success status and audio_path, or error message
    """
    return piper_tts_service.synthesize(request.text)