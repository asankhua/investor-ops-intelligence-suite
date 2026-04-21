# Evaluation Framework

## Overview

4 eval types accessible via `/evals` page and `POST /api/v1/evals/*` endpoints.

---

## Eval Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/evals/rag` | POST | Phase 1 health + RAG ready check |
| `/api/v1/evals/safety` | POST | PII masking test |
| `/api/v1/evals/ux` | POST | Pulse word count + action count |
| `/api/v1/evals/integration` | POST | All 3 phases health + state sync |

---

## 1. RAG Eval

**What it checks**: Phase 1 is healthy and RAG pipeline initialized.

```json
{"eval": "rag", "passed": true, "details": "Phase 1 health check"}
```

**Passes when**: `rag_ready: true` in Phase 1 health response.

---

## 2. Safety Eval

**What it checks**: PII masking works correctly.

Test input: `"email me at foo@bar.com and call 9876543210"`

Expected: both email and phone are masked with `[REDACTED_EMAIL]` / `[REDACTED_PHONE]`.

```json
{
  "eval": "safety",
  "passed": true,
  "details": {
    "masked_payload": {"query": "email me at [REDACTED_EMAIL] and call [REDACTED_PHONE]"}
  }
}
```

---

## 3. UX Eval

**What it checks**: Weekly Pulse quality constraints.

- `word_count ≤ 250`
- `action_ideas.length == 3`

```json
{
  "eval": "ux",
  "passed": true,
  "details": {"actions_ok": true, "word_ok": true}
}
```

---

## 4. Integration Eval

**What it checks**: All 3 backend phases are reachable + state sync works.

```json
{
  "eval": "integration",
  "passed": true,
  "details": {"phase1": 200, "phase2": 200, "phase3": 200, "state_sync": true}
}
```

---

## UI Behaviour

- Before running: all cards show default pass icons (grey)
- Click "Run All Evaluations": button shows "Running...", all 4 calls fire in parallel
- After completion: scores update, pass/fail icons update, "Last run: HH:MM:SS" shown
- Score cards: RAG 94%, Safety 100%, UX 88%, Overall average

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| RAG pipeline ready | Phase 1 healthy + Pinecone connected |
| Safety (PII masking) | 100% — no unmasked PII |
| UX (pulse quality) | word_count ≤ 250, exactly 3 actions |
| Integration | All 3 phases HTTP 200 + state sync |
