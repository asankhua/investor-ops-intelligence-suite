# Theme Classification - Phase 2: Weekly Pulse

## Overview

Extracts themes from customer reviews, generates a Weekly Product Pulse with sentiment analysis, and exposes themes to Phase 3 (Voice Scheduler) for context-aware greetings and email enrichment.

---

## Architecture

```
data/reviews/*.json (app store reviews)
  │
  ▼
ReviewLoader — loads latest review file
  │
  ▼
ThemeEngine (Groq LLaMA)
  ├── Theme extraction from review text
  ├── Confidence scoring per theme
  ├── Sentiment score per theme (TextBlob)
  └── Top 3 themes selected
  │
  ▼
PulseService
  ├── Generates summary (≤250 words)
  ├── Generates 3 action ideas
  ├── Calculates overall sentiment score
  └── Saves to data/weekly_pulse.json
  │
  ▼
FastAPI endpoints expose pulse + themes + analytics
```

---

## Key Files

| File | Role |
|------|------|
| `phase2_weeklyPulse/app/main.py` | FastAPI endpoints |
| `phase2_weeklyPulse/app/services/pulse_service.py` | Pulse generation orchestrator |
| `phase2_weeklyPulse/app/services/theme_engine.py` | Groq theme extraction |
| `phase2_weeklyPulse/app/services/review_loader.py` | Load reviews from data/reviews/ |
| `phase2_weeklyPulse/data/weekly_pulse.json` | Cached pulse output |

---

## API Endpoints (:8102)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/pillar-b/weekly-pulse` | Full pulse with themes, summary, actions |
| GET | `/api/v1/pillar-b/themes` | Top 3 themes with confidence + sentiment |
| GET | `/api/v1/pillar-b/analytics` | Theme distribution, sentiment trends, keywords |
| GET | `/api/v1/pillar-b/analytics/sentiment` | Sentiment trend data |
| GET | `/api/v1/pillar-b/analytics/volume` | Mention volume per theme |
| GET | `/api/v1/pillar-b/analytics/keywords` | Top keywords |
| POST | `/api/v1/pillar-b/refresh` | Re-run theme extraction |

---

## Weekly Pulse Response

```json
{
  "generated_at": "2026-04-21T10:22:09Z",
  "top_themes": [
    {"theme": "Feature Requests", "confidence": 0.8, "mention_count": 19, "sentiment_score": -0.186},
    {"theme": "Support & Service", "confidence": 0.71, "mention_count": 9, "sentiment_score": -0.406},
    {"theme": "Performance & Stability", "confidence": 0.67, "mention_count": 6, "sentiment_score": -0.078}
  ],
  "sentiment_score": -0.223,
  "summary": "This week's customer pulse highlights Feature Requests (19 mentions)...",
  "action_ideas": [
    "Review top requested UX features and schedule at least one quick-win release.",
    "Strengthen support workflow with faster first-response SLA.",
    "Ship performance hotfixes and monitor crash/latency regressions daily."
  ],
  "word_count": 59,
  "analytics": {
    "theme_distribution": [...],
    "sentiment_trends": [...],
    "mention_volume": [...],
    "keywords": [...]
  }
}
```

---

## Cross-Pillar Usage

### Phase 3 (Voice Scheduler)
`ThemeProvider` in Phase 3 calls `GET /api/v1/pillar-b/themes` to:
- Inject theme names into voice greeting
- Detect topic from user input (substring match against theme names)
- Enrich email body with full pulse context (themes, sentiment, summary, actions)

**Default URL**: `http://localhost:8102` (env: `PHASE2_BASE_URL`)

### Phase 4 (Gateway)
Proxies all `/api/v1/pillar-b/*` calls to Phase 2.

### Phase 5 (Dashboard)
- `/weekly-pulse` page: full analytics UI
- Dashboard pillar card: shows `themes_active` count + sentiment score
- Voice Scheduler: theme chips bar (fetched on demand)

---

## Data

Reviews stored in `data/reviews/YYYY-MM-DD.json`. Latest file is used automatically.

Current data: `data/reviews/2026-04-21.json` (100 reviews processed).

---

## UX Constraints (enforced)

- Summary: ≤ 250 words (`word_count` field)
- Action ideas: exactly 3 (`action_ideas` array)
- Top themes: max 3

These are validated by the UX Eval (`POST /api/v1/evals/ux`).

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Required for theme extraction |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Groq endpoint |
| `WEEKLY_PULSE_WORD_LIMIT` | `250` | Max words in summary |
| `WEEKLY_PULSE_ACTION_COUNT` | `3` | Number of action ideas |
