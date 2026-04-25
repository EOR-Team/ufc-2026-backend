# test/test_whisper_manager.py
# WhisperServerManager lifecycle management tests

import os
import pytest
from unittest.mock import patch, MagicMock

from src.whisper_manager import WhisperServerManager


# ============================================================================
# Unit Tests: Initialization
# ============================================================================

class TestInitialization:
    """Tests for WhisperServerManager configuration loading."""

    def test_default_values(self):
        """Manager uses correct default values when env vars are not set."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            assert manager.bin_path == "./whisper.cpp/build/bin/whisper-server"
            assert manager.model_path == "./whisper.cpp/models/ggml-tiny-q50.bin"
            assert manager.port == "8080"
            assert manager.language == "zh"
            assert manager.host == "127.0.0.1"

    def test_custom_env_values(self):
        """Manager loads configuration from environment variables."""
        env = {
            "WHISPER_SERVER_BIN": "/custom/path/whisper-server",
            "WHISPER_MODEL_PATH": "/custom/models/ggml-base.bin",
            "WHISPER_SERVER_PORT": "9090",
            "WHISPER_SERVER_LANGUAGE": "en",
        }
        with patch.dict(os.environ, env, clear=True):
            manager = WhisperServerManager()
            assert manager.bin_path == "/custom/path/whisper-server"
            assert manager.model_path == "/custom/models/ggml-base.bin"
            assert manager.port == "9090"
            assert manager.language == "en"


# ============================================================================
# Unit Tests: Build Args
# ============================================================================

class TestBuildArgs:
    """Tests for whisper-server command argument building."""

    def test_args_structure(self):
        """Command arguments are built correctly."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            args = manager._build_args()
            assert args[0] == manager.bin_path
            assert "-m" in args
            assert "--port" in args
            assert "--language" in args
            assert "--host" in args

    def test_args_order(self):
        """Arguments are in correct order for whisper-server."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            args = manager._build_args()
            idx = args.index("-m")
            assert args[idx + 1] == manager.model_path
            idx = args.index("--port")
            assert args[idx + 1] == manager.port


# ============================================================================
# Unit Tests: Health Check
# ============================================================================

class TestIsReady:
    """Tests for whisper-server health check."""

    def test_returns_false_when_no_process(self):
        """is_ready() returns False when no subprocess exists."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            manager._proc = None
            assert manager.is_ready() is False

    def test_returns_false_when_process_exited(self):
        """is_ready() returns False when process has already exited."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            mock_proc = MagicMock()
            mock_proc.poll.return_value = 1  # process exited with code 1
            manager._proc = mock_proc
            assert manager.is_ready() is False


# ============================================================================
# Unit Tests: Available Property
# ============================================================================

class TestAvailable:
    """Tests for the available property."""

    def test_default_unavailable(self):
        """Manager is unavailable by default before start."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            assert manager.available is False

    def test_marked_available_on_successful_start(self):
        """Manager marks itself available after successful start."""
        with patch.dict(os.environ, {}, clear=True):
            manager = WhisperServerManager()
            manager._available = True
            assert manager.available is True
