"""Phase 3 backend: Voice Scheduler + HITL approval APIs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .services.hitl_service import HITLService
from .services.state_store import StateStore
from .services.theme_provider import ThemeProvider
from .services.voice_service import VoiceService


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(
    title="Investor Intelligence Suite - Phase 3",
    description="Voice Scheduler + MCP/HITL backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

state_store = StateStore(Path(__file__).resolve().parents[2] / "data" / "state.json")
theme_provider = ThemeProvider()
hitl_service = HITLService(state_store, theme_provider)
voice_service = VoiceService(state_store, theme_provider, hitl_service)


class StartRecordingRequest(BaseModel):
    session_id: Optional[str] = None


class StopRecordingRequest(BaseModel):
    recording_id: str


class CancelRecordingRequest(BaseModel):
    recording_id: str


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "meera"


class MessageRequest(BaseModel):
    message: str


class VoiceMessageRequest(BaseModel):
    audio_base64: str


class EditEmailRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None


class SendEmailRequest(BaseModel):
    approved: Optional[bool] = True


class RejectRequest(BaseModel):
    reason: Optional[str] = None


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "healthy", "phase": 3, "pillar": "C"}


@app.post("/api/v1/pillar-c/voice/record/start")
async def start_recording(req: Optional[StartRecordingRequest] = None) -> Dict[str, Any]:
    return voice_service.start_recording(req.session_id if req else None)


@app.post("/api/v1/pillar-c/voice/record/stop")
async def stop_recording(req: StopRecordingRequest) -> Dict[str, Any]:
    return voice_service.stop_recording(req.recording_id)


@app.post("/api/v1/pillar-c/voice/record/cancel")
async def cancel_recording(req: CancelRecordingRequest) -> Dict[str, Any]:
    return voice_service.cancel_recording(req.recording_id)


@app.get("/api/v1/pillar-c/voice/play/{audio_id}")
async def play_audio(audio_id: str) -> Dict[str, Any]:
    return {"audio_id": audio_id, "audio_url": f"/api/v1/pillar-c/voice/play/{audio_id}", "status": "ready"}


@app.post("/api/v1/pillar-c/tts/play")
async def tts_play(req: TTSRequest) -> Dict[str, Any]:
    return {"status": "ready", "voice": req.voice or "meera", "text_length": len(req.text), "audio_url": "/api/v1/pillar-c/voice/play/tts-preview"}


@app.get("/api/v1/pillar-c/pipeline/status")
async def pipeline_status() -> Dict[str, Any]:
    return voice_service.get_pipeline_status()


@app.get("/api/v1/pillar-c/mcp/logs")
async def mcp_logs() -> Dict[str, Any]:
    state = state_store.get_state()
    return {"logs": state.get("mcp_calls", [])[-50:]}


@app.post("/api/v1/pillar-c/conversation/message")
async def conversation_message(req: MessageRequest) -> Dict[str, Any]:
    return voice_service.process_message(req.message)


@app.post("/api/v1/pillar-c/conversation/voice")
async def conversation_voice(req: VoiceMessageRequest) -> Dict[str, Any]:
    try:
        return voice_service.process_voice_message(req.audio_base64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Voice processing failed: {exc}") from exc


@app.get("/api/v1/hitl/pending")
async def hitl_pending() -> Dict[str, Any]:
    return {"pending_actions": hitl_service.get_pending_actions()}


@app.get("/api/v1/hitl/actions")
async def hitl_actions() -> Dict[str, Any]:
    return {"actions": hitl_service.get_all_actions()}


@app.get("/api/v1/hitl/email/preview/{booking_code}")
async def hitl_email_preview(booking_code: str) -> Dict[str, Any]:
    return hitl_service.get_email_preview(booking_code)


@app.post("/api/v1/hitl/email/send/{booking_code}")
async def hitl_email_send(booking_code: str, req: SendEmailRequest) -> Dict[str, Any]:
    if req.approved is False:
        raise HTTPException(status_code=400, detail="Email send requires approved=true")
    return hitl_service.send_email(booking_code)


@app.post("/api/v1/hitl/email/edit/{booking_code}")
async def hitl_email_edit(booking_code: str, req: EditEmailRequest) -> Dict[str, Any]:
    return {"updated_draft": hitl_service.edit_email_draft(booking_code, req.subject, req.body)}


@app.post("/api/v1/hitl/approve/{action_id}")
async def hitl_approve(action_id: str) -> Dict[str, Any]:
    return hitl_service.approve_action(action_id)


@app.post("/api/v1/hitl/reject/{action_id}")
async def hitl_reject(action_id: str, req: RejectRequest) -> Dict[str, Any]:
    return hitl_service.reject_action(action_id, req.reason)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
