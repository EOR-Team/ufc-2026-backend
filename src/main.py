# src/main.py
# FastAPI application entry point with whisper-server lifecycle integration
#
# @author n1ghts4kura
# @date 2026-04-24

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import dspy
from fastapi import FastAPI

from src.logger import info, error
from src.whisper_manager import whisper_manager
from src.stt import router as stt_router
from src.tts import router as tts_router
from src.triager.routing import triager_router
from src.llm import deepseek


# set default LLM to deepseek
dspy.configure(lm=deepseek.DeepseekLM())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: start/stop whisper-server."""
    # Startup
    whisper_manager.start()
    yield
    # Shutdown
    whisper_manager.stop()


app = FastAPI(
    title="UFC 2026 Backend",
    lifespan=lifespan,
)

app.include_router(stt_router, prefix="/stt", tags=["stt"])
app.include_router(tts_router, prefix="/tts", tags=["tts"])
app.include_router(triager_router, tags=["triager"])


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    whisper_ok = whisper_manager.is_ready()
    return {
        "status": "ok",
        "whisper_available": whisper_ok,
    }


@app.get("/")
def root() -> dict:
    """Root endpoint."""
    return {"message": "UFC 2026 Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
