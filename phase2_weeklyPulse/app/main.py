"""Phase 2 backend: Weekly Pulse and Theme Analytics APIs."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .services.pulse_service import PulseService


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(
    title="Investor Intelligence Suite - Phase 2",
    description="Weekly Pulse API (Pillar B)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo_root = Path(__file__).resolve().parents[2]
pulse_service = PulseService(repo_root)
_scheduler_task: asyncio.Task | None = None


async def _weekly_scheduler_loop() -> None:
    check_seconds = max(300, int(os.getenv("PULSE_SCHEDULER_CHECK_SECONDS", "3600")))
    while True:
        try:
            pulse_service.run_scheduler_if_due()
        except Exception:
            # Keep scheduler resilient; failures are reflected in scheduler status.
            pass
        await asyncio.sleep(check_seconds)


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "healthy", "phase": 2, "pillar": "B"}

@app.on_event("startup")
async def startup_scheduler() -> None:
    global _scheduler_task
    pulse_service.run_scheduler_if_due()
    _scheduler_task = asyncio.create_task(_weekly_scheduler_loop())


@app.on_event("shutdown")
async def shutdown_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        _scheduler_task = None


@app.get("/api/v1/pillar-b/weekly-pulse")
async def weekly_pulse() -> Dict[str, Any]:
    pulse = pulse_service.get_pulse()
    pulse["freshness"] = pulse_service.freshness()
    pulse["scheduler"] = pulse_service.get_scheduler_status()
    return pulse


@app.get("/api/v1/pillar-b/themes")
async def themes() -> Dict[str, Any]:
    return {"themes": pulse_service.get_themes()}


@app.get("/api/v1/pillar-b/analytics")
async def analytics() -> Dict[str, Any]:
    return pulse_service.get_analytics()


@app.get("/api/v1/pillar-b/analytics/themes/{theme_id}")
async def analytics_theme(theme_id: str) -> Dict[str, Any]:
    return {"theme": pulse_service.get_theme_details(theme_id)}


@app.get("/api/v1/pillar-b/analytics/sentiment")
async def analytics_sentiment() -> Dict[str, Any]:
    a = pulse_service.get_analytics()
    return {"sentiment_trends": a.get("sentiment_trends", [])}


@app.get("/api/v1/pillar-b/analytics/volume")
async def analytics_volume() -> Dict[str, Any]:
    a = pulse_service.get_analytics()
    return {"mention_volume": a.get("mention_volume", [])}


@app.get("/api/v1/pillar-b/analytics/keywords")
async def analytics_keywords() -> Dict[str, Any]:
    a = pulse_service.get_analytics()
    return {"keywords": a.get("keywords", [])}


@app.post("/api/v1/pillar-b/refresh")
async def refresh() -> Dict[str, Any]:
    try:
        pulse = pulse_service.refresh(fetch_live_reviews=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Play Store refresh failed: {exc}") from exc
    return {
        "status": "success",
        "generated_at": pulse.get("generated_at"),
        "reviews_processed": pulse.get("raw_reviews_processed", 0),
        "top_theme": (pulse.get("top_themes", [{}])[0].get("theme") if pulse.get("top_themes") else None),
    }


@app.get("/api/v1/pillar-b/scheduler/status")
async def scheduler_status() -> Dict[str, Any]:
    return pulse_service.get_scheduler_status()


# Compatibility aliases from architecture snippets
@app.get("/api/v1/pulse/current")
async def pulse_current_alias() -> Dict[str, Any]:
    return await weekly_pulse()


@app.post("/api/v1/themes/update")
async def themes_update_alias() -> Dict[str, Any]:
    return await refresh()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
