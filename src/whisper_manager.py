# src/whisper_manager.py
# Whisper-server lifecycle manager - binds whisper-server to FastAPI lifecycle
#
# @author n1ghts4kura
# @date 2026-04-24

import os
import signal
import subprocess
import time
from typing import Optional, List

import requests

from src.logger import info, error


class WhisperServerManager:
    """Manages whisper-server child process lifecycle."""

    def __init__(self) -> None:
        """Initialize manager with configuration from environment variables."""
        self.bin_path: str = os.environ.get(
            "WHISPER_SERVER_BIN",
            "./whisper.cpp/build/bin/whisper-server"
        )
        self.model_path: str = os.environ.get(
            "WHISPER_MODEL_PATH",
            "./whisper.cpp/models/ggml-tiny-q50.bin"
        )
        self.port: str = os.environ.get("WHISPER_SERVER_PORT", "9000")
        self.language: str = os.environ.get("WHISPER_SERVER_LANGUAGE", "zh")
        self.host: str = "127.0.0.1"

        self._proc: Optional[subprocess.Popen] = None
        self._available: bool = False

    def _build_args(self) -> List[str]:
        """Build whisper-server command arguments."""
        return [
            self.bin_path,
            "-m", self.model_path,
            "--port", self.port,
            "--language", self.language,
            "--host", self.host,
        ]

    def start(self) -> None:
        """Start whisper-server subprocess."""
        info(f"Starting whisper-server: {self.bin_path}")
        info(f"  model={self.model_path}, language={self.language}, port={self.port}")

        try:
            self._proc = subprocess.Popen(
                self._build_args(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Wait briefly for startup
            time.sleep(1)

            if self._proc.poll() is not None:
                # Process already exited
                stdout, stderr = self._proc.communicate()
                error(f"whisper-server exited immediately: {self._proc.returncode}")
                error(f"stdout: {stdout.decode('utf-8', errors='replace')}")
                error(f"stderr: {stderr.decode('utf-8', errors='replace')}")
                self._available = False
                return

            # Check health endpoint
            if self.is_ready():
                self._available = True
                info(f"whisper-server started on {self.host}:{self.port}")
            else:
                error("whisper-server process started but health check failed")
                self._available = False

        except FileNotFoundError:
            error(f"whisper-server binary not found: {self.bin_path}")
            self._available = False
        except Exception as e:
            error(f"Failed to start whisper-server: {e}", exc_info=True)
            self._available = False

    def stop(self) -> None:
        """Stop whisper-server subprocess gracefully."""
        if self._proc is None:
            info("whisper-server not running (no process)")
            return

        info("whisper-server shutting down")
        try:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
                info("whisper-server stopped gracefully")
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
                error("whisper-server force killed (did not exit in 5s)")
        except Exception as e:
            error(f"Error stopping whisper-server: {e}", exc_info=True)
        finally:
            self._proc = None
            self._available = False

    def is_ready(self) -> bool:
        """Check if whisper-server is running and healthy."""
        if self._proc is None or self._proc.poll() is not None:
            return False

        try:
            resp = requests.get(
                f"http://{self.host}:{self.port}/health",
                timeout=2
            )
            return resp.status_code == 200 and resp.json().get("status") == "ok"
        except Exception:
            return False

    @property
    def available(self) -> bool:
        """Return whether whisper-server is available."""
        return self._available


# Global instance
whisper_manager = WhisperServerManager()


__all__ = [
    "WhisperServerManager",
    "whisper_manager",
]
