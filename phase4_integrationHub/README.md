# Phase 4 - Integration Hub

Unified API gateway and cross-pillar state layer for Investor Intelligence Suite.

## Responsibilities

- Single backend entrypoint for frontend (`/api/v1/*`)
- Routes requests to:
  - Phase 1 Knowledge Base
  - Phase 2 Weekly Pulse
  - Phase 3 Voice Scheduler + HITL
- Enforces PII masking on inbound/outbound payloads
- Persists cross-pillar booking references for state sync validation

## Run

```bash
cd phase4_integrationHub
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# optional service URLs (defaults shown)
export PHASE1_BASE_URL=http://localhost:8101
export PHASE2_BASE_URL=http://localhost:8102
export PHASE3_BASE_URL=http://localhost:8103

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Key Endpoints

- `GET /api/v1/dashboard/stats`
- `GET /api/v1/dashboard/activity`
- `GET /api/v1/dashboard/pillars`
- `GET /api/v1/dashboard/performance`
- `POST /api/v1/gateway/query`
- `GET /api/v1/state/bookings`

### Forwarded API Surface

- Pillar A: `/api/v1/query`, `/api/v1/funds/search`, `/api/v1/sources`
- Pillar B: `/api/v1/pillar-b/*`
- Pillar C + HITL: `/api/v1/pillar-c/*`, `/api/v1/hitl/*`
- Evals: `/api/v1/evals/*`

## State Persistence

- Shared state file: `phase4_integrationHub/data/shared_state.json`
- Booking references also synced into:
  - `phase2_weeklyPulse/data/weekly_pulse.json` under `booking_refs`
