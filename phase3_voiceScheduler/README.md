# Phase 3 - Voice Scheduler Backend

FastAPI backend implementing Pillar C endpoints from `docs/voiceAgent.md` and `docs/mcpIntegration.md`.

## Run

```bash
cd phase3_voiceScheduler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Endpoints

- `POST /api/v1/pillar-c/voice/record/start`
- `POST /api/v1/pillar-c/voice/record/stop`
- `POST /api/v1/pillar-c/voice/record/cancel`
- `GET /api/v1/pillar-c/voice/play/{audio_id}`
- `POST /api/v1/pillar-c/tts/play`
- `GET /api/v1/pillar-c/pipeline/status`
- `POST /api/v1/pillar-c/conversation/message`
- `GET /api/v1/hitl/pending`
- `GET /api/v1/hitl/email/preview/{booking_code}`
- `POST /api/v1/hitl/email/send/{booking_code}`
- `POST /api/v1/hitl/email/edit/{booking_code}`
- `POST /api/v1/hitl/approve/{action_id}`
- `POST /api/v1/hitl/reject/{action_id}`

## Notes

- Current implementation includes simulated voice/audio handling and HITL queue behavior.
- Booking flow generates `MTG-YYYY-XXX` codes and queues calendar + email actions for approval.
- Theme-aware greeting uses Phase 2 themes endpoint when available, otherwise falls back to defaults.
