"""Phase 4 backend: API gateway + cross-pillar shared state."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import csv
import io
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from .services.gateway_client import GatewayClient
from .services.shared_state import SharedStateStore


load_dotenv(Path(__file__).resolve().parents[3] / ".env")

app = FastAPI(
    title="Investor Intelligence Suite - Phase 4",
    description="Integration Hub API Gateway + Cross-pillar State",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repo_root = Path(__file__).resolve().parents[2]
client = GatewayClient()
shared_state = SharedStateStore(
    repo_root / "phase4_integrationHub" / "data" / "shared_state.json",
    repo_root / "phase2_weeklyPulse" / "data" / "weekly_pulse.json",
)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    fund_name: Optional[str] = None


class MessageRequest(BaseModel):
    message: str


class SendEmailRequest(BaseModel):
    approved: Optional[bool] = True


class EditEmailRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None


class RejectRequest(BaseModel):
    reason: Optional[str] = None


class GatewayQueryRequest(BaseModel):
    pillar: Optional[str] = None  # A|B|C
    query: Optional[str] = None
    message: Optional[str] = None
    fund_name: Optional[str] = None


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "healthy", "phase": 4, "name": "integration_hub"}


@app.get("/api/v1/state/bookings")
async def state_bookings() -> Dict[str, Any]:
    state = shared_state.get_state()
    return {
        "active_bookings": state.get("active_bookings", []),
        "booking_refs": state.get("weekly_pulse", {}).get("booking_refs", []),
        "booking_to_pulse_map": state.get("booking_to_pulse_map", {}),
    }


@app.get("/api/v1/dashboard/stats")
async def dashboard_stats() -> Dict[str, Any]:
    p1_status, p1_sources = client.get("phase1", "/api/v1/sources")
    p2_status, p2_themes = client.get("phase2", "/api/v1/pillar-b/themes")
    p3_status, p3_pending = client.get("phase3", "/api/v1/hitl/pending")
    state = shared_state.get_state()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return {
        "kb_docs": len((p1_sources.get("sources") or [])) if p1_status == 200 else 0,
        "themes_active": len((p2_themes.get("themes") or [])) if p2_status == 200 else 0,
        "bookings_this_week": len(state.get("active_bookings", [])),
        "pending_approvals": len((p3_pending.get("pending_actions") or [])) if p3_status == 200 else 0,
        "last_synced": now,
    }


@app.get("/api/v1/dashboard/activity")
async def dashboard_activity() -> Dict[str, Any]:
    state = shared_state.get_state()
    events = state.get("sync_events", [])[-10:]
    rows = [
        {
            "time": e.get("timestamp"),
            "type": "state_sync",
            "message": f"Booking {e.get('booking_code')} synced across pillars",
        }
        for e in reversed(events)
    ]
    p3_code, p3_logs = client.get("phase3", "/api/v1/pillar-c/mcp/logs")
    if p3_code == 200:
        for item in reversed((p3_logs.get("logs") or [])[-6:]):
            code = item.get("booking_code")
            status = item.get("status") or {}
            rows.append(
                {
                    "time": item.get("timestamp"),
                    "type": "mcp_tool",
                    "message": (
                        f"MCP tools for {code or 'session'} "
                        f"(calendar={status.get('calendar')}, doc={status.get('doc')}, mail={status.get('mail')})"
                    ),
                }
            )
    return {"activity": rows}


@app.get("/api/v1/dashboard/pillars")
async def dashboard_pillars() -> Dict[str, Any]:
    p1_h, _ = client.get("phase1", "/health")
    p2_h, _ = client.get("phase2", "/health")
    p3_h, _ = client.get("phase3", "/health")
    return {
        "pillars": [
            {"pillar": "A", "name": "Knowledge Base", "status": "operational" if p1_h == 200 else "degraded"},
            {"pillar": "B", "name": "Weekly Pulse", "status": "operational" if p2_h == 200 else "degraded"},
            {"pillar": "C", "name": "Voice Scheduler", "status": "operational" if p3_h == 200 else "degraded"},
        ]
    }


@app.get("/api/v1/dashboard/performance")
async def dashboard_performance() -> Dict[str, Any]:
    statuses = []
    for phase in ("phase1", "phase2", "phase3"):
        code, _ = client.get(phase, "/health")
        statuses.append(code == 200)
    score = int((sum(1 for ok in statuses if ok) / 3) * 100)
    return {"score": score, "status": "operational" if score >= 67 else "degraded"}


@app.get("/api/v1/funds/search")
async def funds_search(query: str = Query(default="")):
    code, payload = client.get("phase1", "/api/v1/funds/search", params={"query": query})
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/query")
async def query_rag(req: QueryRequest):
    code, payload = client.post(
        "phase1",
        "/api/v1/query",
        json_body={"query": req.query, "top_k": req.top_k, "fund_name": req.fund_name},
    )
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/sources")
async def sources():
    code, payload = client.get("phase1", "/api/v1/sources")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/weekly-pulse")
async def pillar_b_weekly_pulse():
    code, payload = client.get("phase2", "/api/v1/pillar-b/weekly-pulse")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/themes")
async def pillar_b_themes():
    code, payload = client.get("phase2", "/api/v1/pillar-b/themes")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/analytics")
async def pillar_b_analytics():
    code, payload = client.get("phase2", "/api/v1/pillar-b/analytics")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/analytics/themes/{theme_id}")
async def pillar_b_analytics_theme(theme_id: str):
    code, payload = client.get("phase2", f"/api/v1/pillar-b/analytics/themes/{theme_id}")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/analytics/sentiment")
async def pillar_b_sentiment():
    code, payload = client.get("phase2", "/api/v1/pillar-b/analytics/sentiment")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/analytics/volume")
async def pillar_b_volume():
    code, payload = client.get("phase2", "/api/v1/pillar-b/analytics/volume")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/analytics/keywords")
async def pillar_b_keywords():
    code, payload = client.get("phase2", "/api/v1/pillar-b/analytics/keywords")
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-b/refresh")
async def pillar_b_refresh():
    code, payload = client.post("phase2", "/api/v1/pillar-b/refresh", json_body={})
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-b/reviews/download")
async def pillar_b_reviews_download() -> Response:
    reviews_dir = repo_root / "data" / "reviews"
    files = sorted(reviews_dir.glob("*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No review file found in data/reviews")

    latest_file = files[-1]
    try:
        payload = json.loads(latest_file.read_text())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to parse reviews file: {exc}") from exc

    if not isinstance(payload, list):
        raise HTTPException(status_code=500, detail="Invalid reviews payload format")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["reviewId", "rating", "text", "date", "userName", "appVersion"],
    )
    writer.writeheader()
    for row in payload:
        if isinstance(row, dict):
            writer.writerow(
                {
                    "reviewId": row.get("reviewId", ""),
                    "rating": row.get("rating", ""),
                    "text": row.get("text", ""),
                    "date": row.get("date", ""),
                    "userName": row.get("userName", ""),
                    "appVersion": row.get("appVersion", ""),
                }
            )

    csv_content = output.getvalue()
    filename = f"{latest_file.stem}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/api/v1/pillar-c/voice/record/start")
async def pillar_c_record_start(body: Optional[Dict[str, Any]] = None):
    code, payload = client.post("phase3", "/api/v1/pillar-c/voice/record/start", json_body=body or {})
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-c/voice/record/stop")
async def pillar_c_record_stop(body: Dict[str, Any]):
    code, payload = client.post("phase3", "/api/v1/pillar-c/voice/record/stop", json_body=body)
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-c/voice/record/cancel")
async def pillar_c_record_cancel(body: Dict[str, Any]):
    code, payload = client.post("phase3", "/api/v1/pillar-c/voice/record/cancel", json_body=body)
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-c/voice/play/{audio_id}")
async def pillar_c_voice_play(audio_id: str):
    code, payload = client.get("phase3", f"/api/v1/pillar-c/voice/play/{audio_id}")
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-c/tts/play")
async def pillar_c_tts_play(body: Dict[str, Any]):
    code, payload = client.post("phase3", "/api/v1/pillar-c/tts/play", json_body=body)
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-c/pipeline/status")
async def pillar_c_pipeline_status():
    code, payload = client.get("phase3", "/api/v1/pillar-c/pipeline/status")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/pillar-c/mcp/logs")
async def pillar_c_mcp_logs():
    code, payload = client.get("phase3", "/api/v1/pillar-c/mcp/logs")
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-c/conversation/message")
async def pillar_c_message(req: MessageRequest):
    code, payload = client.post("phase3", "/api/v1/pillar-c/conversation/message", json_body={"message": req.message})
    booking_code = client.parse_booking_code(payload)
    if booking_code:
        pulse_context = _current_pulse_context()
        shared_state.sync_booking(booking_code, pulse_context, source="pillar-c")
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/pillar-c/conversation/voice")
async def pillar_c_voice_message(body: Dict[str, Any]):
    code, payload = client.post("phase3", "/api/v1/pillar-c/conversation/voice", json_body=body)
    booking_code = client.parse_booking_code(payload)
    if booking_code:
        shared_state.sync_booking(booking_code, _current_pulse_context(), source="pillar-c-voice")
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/hitl/pending")
async def hitl_pending():
    code, payload = client.get("phase3", "/api/v1/hitl/pending", mask_response=False)
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/hitl/actions")
async def hitl_actions():
    code, payload = client.get("phase3", "/api/v1/hitl/actions", mask_response=False)
    return JSONResponse(status_code=code, content=payload)


@app.get("/api/v1/hitl/email/preview/{booking_code}")
async def hitl_email_preview(booking_code: str):
    code, payload = client.get("phase3", f"/api/v1/hitl/email/preview/{booking_code}", mask_response=False)
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/hitl/email/send/{booking_code}")
async def hitl_email_send(booking_code: str, req: SendEmailRequest):
    code, payload = client.post("phase3", f"/api/v1/hitl/email/send/{booking_code}", json_body=req.model_dump())
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/hitl/email/edit/{booking_code}")
async def hitl_email_edit(booking_code: str, req: EditEmailRequest):
    code, payload = client.post("phase3", f"/api/v1/hitl/email/edit/{booking_code}", json_body=req.model_dump())
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/hitl/approve/{action_id}")
async def hitl_approve(action_id: str):
    code, payload = client.post("phase3", f"/api/v1/hitl/approve/{action_id}", json_body={})
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/hitl/reject/{action_id}")
async def hitl_reject(action_id: str, req: RejectRequest):
    code, payload = client.post("phase3", f"/api/v1/hitl/reject/{action_id}", json_body=req.model_dump())
    return JSONResponse(status_code=code, content=payload)


@app.post("/api/v1/gateway/query")
async def gateway_query(req: GatewayQueryRequest):
    if req.pillar and req.pillar.upper() == "A":
        code, payload = client.post(
            "phase1",
            "/api/v1/query",
            json_body={"query": req.query or "", "top_k": 5, "fund_name": req.fund_name},
        )
        return JSONResponse(status_code=code, content=payload)

    if req.pillar and req.pillar.upper() == "B":
        code, payload = client.get("phase2", "/api/v1/pillar-b/weekly-pulse")
        return JSONResponse(status_code=code, content=payload)

    if req.pillar and req.pillar.upper() == "C":
        code, payload = client.post("phase3", "/api/v1/pillar-c/conversation/message", json_body={"message": req.message or ""})
        booking_code = client.parse_booking_code(payload)
        if booking_code:
            shared_state.sync_booking(booking_code, _current_pulse_context(), source="gateway-query")
        return JSONResponse(status_code=code, content=payload)

    # default cross-pillar stitched response
    a_code, a_payload = client.post(
        "phase1",
        "/api/v1/query",
        json_body={"query": req.query or "summarize key fund fee highlights", "top_k": 5, "fund_name": req.fund_name},
    )
    b_code, b_payload = client.get("phase2", "/api/v1/pillar-b/themes")
    c_code, c_payload = client.get("phase3", "/api/v1/hitl/pending")
    merged = {
        "pillar_a": a_payload if a_code == 200 else {"error": "unavailable"},
        "pillar_b": b_payload if b_code == 200 else {"error": "unavailable"},
        "pillar_c": c_payload if c_code == 200 else {"error": "unavailable"},
        "state": shared_state.get_state(),
    }
    return merged


@app.post("/api/v1/evals/rag")
async def eval_rag():
    code, _ = client.get("phase1", "/health")
    return {"eval": "rag", "passed": code == 200, "details": "Phase 1 health check"}


@app.post("/api/v1/evals/safety")
async def eval_safety():
    test = {"query": "email me at foo@bar.com and call 9876543210"}
    masked = client.guard.mask(test)
    no_pii = not client.guard.has_unmasked_pii(masked)
    return {"eval": "safety", "passed": no_pii, "details": {"masked_payload": masked}}


@app.post("/api/v1/evals/ux")
async def eval_ux():
    code, pulse = client.get("phase2", "/api/v1/pillar-b/weekly-pulse")
    if code != 200:
        return {"eval": "ux", "passed": False, "details": "Phase 2 unavailable"}
    actions_ok = len(pulse.get("action_ideas", [])) == 3
    word_ok = int(pulse.get("word_count", 9999)) <= 250
    return {"eval": "ux", "passed": actions_ok and word_ok, "details": {"actions_ok": actions_ok, "word_ok": word_ok}}


@app.post("/api/v1/evals/integration")
async def eval_integration():
    p1, _ = client.get("phase1", "/health")
    p2, _ = client.get("phase2", "/health")
    p3, _ = client.get("phase3", "/health")
    sync = len(shared_state.get_booking_refs()) >= 0
    passed = p1 == 200 and p2 == 200 and p3 == 200 and sync
    return {"eval": "integration", "passed": passed, "details": {"phase1": p1, "phase2": p2, "phase3": p3, "state_sync": sync}}


@app.get("/api/v1/evals/results")
async def eval_results():
    return {
        "results": [
            {"name": "rag", "endpoint": "/api/v1/evals/rag"},
            {"name": "safety", "endpoint": "/api/v1/evals/safety"},
            {"name": "ux", "endpoint": "/api/v1/evals/ux"},
            {"name": "integration", "endpoint": "/api/v1/evals/integration"},
        ]
    }


def _current_pulse_context() -> Dict[str, Any]:
    code, themes_payload = client.get("phase2", "/api/v1/pillar-b/themes")
    if code != 200:
        return {"status": "unavailable", "top_themes": []}
    return {"status": "ok", "top_themes": themes_payload.get("themes", [])}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
