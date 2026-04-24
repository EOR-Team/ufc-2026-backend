#!/usr/bin/env python3
# test_tts.py
# End-to-end test for Piper TTS synthesis
#
# @author n1ghts4kura
# @date 2026-04-25

import wave
import os
import sys


def test_tts_synthesis():
    """Test TTS synthesis end-to-end."""
    test_text = "你好，欢迎使用 Piper 语音合成"
    output_path = "./outputs/tts/test_output.wav"

    # Ensure output dir exists
    os.makedirs("./outputs/tts", exist_ok=True)

    # Import after ensuring deps are installed
    try:
        from src.piper_tts_service import piper_tts_service
    except ImportError as e:
        print(f"FAILED: Could not import piper_tts_service: {e}")
        sys.exit(1)

    # Synthesize
    result = piper_tts_service.synthesize(
        text=test_text,
        output_path=output_path,
        length_scale=1.0,
    )

    print(f"Result: {result}")

    # Check success
    if not result.get("success"):
        print(f"FAILED: Synthesis failed - {result.get('error')}")
        sys.exit(1)

    # Verify file exists and is valid WAV
    audio_path = result.get("audio_path")
    if not audio_path or not os.path.exists(audio_path):
        print(f"FAILED: Audio file not created at {audio_path}")
        sys.exit(1)

    # Validate WAV format
    try:
        with wave.open(audio_path, "rb") as wav:
            channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            nframes = wav.getnframes()

        print(f"WAV valid: channels={channels}, sampwidth={sampwidth}, framerate={framerate}, frames={nframes}")

        if channels != 1:
            print(f"FAILED: Expected mono (1 channel), got {channels}")
            sys.exit(1)
        if sampwidth != 2:
            print(f"FAILED: Expected 16-bit (2 bytes), got {sampwidth}")
            sys.exit(1)
        if framerate != 22050:
            print(f"WARNING: Expected 22050 Hz, got {framerate}")

        duration_secs = nframes / framerate if framerate else 0
        print(f"Generated audio duration: {duration_secs:.2f} seconds")

        if nframes == 0:
            print(f"FAILED: Audio has zero frames")
            sys.exit(1)

    except wave.Error as e:
        print(f"FAILED: Invalid WAV file - {e}")
        sys.exit(1)

    print("SUCCESS: TTS synthesis test passed!")
    print(f"Audio saved to: {audio_path}")


if __name__ == "__main__":
    test_tts_synthesis()