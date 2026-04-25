# test/test_stt.py
# STT endpoint tests

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.stt import (
    TranscriptionError,
    convert_audio_to_wav,
    transcribe_audio,
    handle_stt_upload,
    MAX_FILE_SIZE,
)


# ============================================================================
# Unit Tests: TranscriptionError
# ============================================================================

class TestTranscriptionError:
    """Tests for TranscriptionError exception."""

    def test_error_message(self):
        """TranscriptionError stores message correctly."""
        err = TranscriptionError("test error")
        assert err.message == "test error"
        assert str(err) == "test error"


# ============================================================================
# Unit Tests: convert_audio_to_wav
# ============================================================================

class TestConvertAudioToWav:
    """Tests for FFmpeg audio conversion."""

    def test_ffmpeg_not_found(self):
        """Returns False when ffmpeg is not found."""
        with patch("src.stt.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = convert_audio_to_wav("/tmp/input.mp3", "/tmp/output.wav")
            assert result is False

    def test_conversion_success(self):
        """Returns True when ffmpeg succeeds."""
        with patch("src.stt.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = convert_audio_to_wav("/tmp/input.mp3", "/tmp/output.wav")
            assert result is True

    def test_conversion_failure(self):
        """Returns False when ffmpeg fails."""
        with patch("src.stt.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr=b"error")
            result = convert_audio_to_wav("/tmp/input.mp3", "/tmp/output.wav")
            assert result is False


# ============================================================================
# Unit Tests: transcribe_audio
# ============================================================================

class TestTranscribeAudio:
    """Tests for whisper-server transcription."""

    def test_raises_when_whisper_unavailable(self):
        """Raises TranscriptionError when whisper_manager is unavailable."""
        with patch("src.stt.whisper_manager") as mock_wm:
            mock_wm.available = False
            with pytest.raises(TranscriptionError) as exc_info:
                transcribe_audio("/tmp/audio.wav")
            assert "whisper service unavailable" in str(exc_info.value)

    def test_returns_text_on_success(self):
        """Returns transcribed text when whisper-server succeeds."""
        with patch("src.stt.whisper_manager") as mock_wm:
            mock_wm.available = True
            mock_wm.host = "127.0.0.1"
            mock_wm.port = "8080"
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"text": "你好世界"}
            with patch("src.stt.requests.post") as mock_post:
                mock_post.return_value = mock_response
                with patch("builtins.open", MagicMock()):
                    result = transcribe_audio("/tmp/audio.wav")
                    assert result == "你好世界"


# ============================================================================
# Unit Tests: handle_stt_upload
# ============================================================================

class TestHandleSttUpload:
    """Tests for STT upload handler."""

    def test_returns_error_when_whisper_unavailable(self):
        """Returns error JSON when whisper is not available."""
        with patch("src.stt.whisper_manager") as mock_wm:
            mock_wm.available = False
            mock_wm.host = "127.0.0.1"
            mock_wm.port = "8080"

            mock_file = AsyncMock()
            mock_file.read = AsyncMock(return_value=b"fake audio content")

            with patch("src.stt.convert_audio_to_wav", return_value=True):
                import asyncio
                result = asyncio.run(handle_stt_upload(mock_file))

                assert result["success"] is False
                assert "whisper" in result["error"].lower()


# ============================================================================
# Integration Tests: Constants
# ============================================================================

class TestConstants:
    """Tests for module constants."""

    def test_max_file_size(self):
        """MAX_FILE_SIZE is 10MB."""
        assert MAX_FILE_SIZE == 10 * 1024 * 1024
