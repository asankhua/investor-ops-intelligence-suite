# Phase 2 - Weekly Pulse Backend

FastAPI backend for Pillar B theme classification and analytics.

## Run

```bash
cd phase2_weeklyPulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Main Endpoints

- `GET /api/v1/pillar-b/weekly-pulse`
- `GET /api/v1/pillar-b/themes`
- `GET /api/v1/pillar-b/analytics`
- `GET /api/v1/pillar-b/analytics/themes/{theme_id}`
- `GET /api/v1/pillar-b/analytics/sentiment`
- `GET /api/v1/pillar-b/analytics/volume`
- `GET /api/v1/pillar-b/analytics/keywords`
- `POST /api/v1/pillar-b/refresh`

## Data Source

- Reviews read from latest file in `data/reviews/*.json`
- Pulse persisted to `phase2_weeklyPulse/data/weekly_pulse.json`
- Last refresh tracked in `phase2_weeklyPulse/data/last_pulse_sync.txt`
