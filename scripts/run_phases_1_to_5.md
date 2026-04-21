# Runbook: Wire Phase 1 to Phase 5

This wiring follows the docs architecture:

- Phase 1 (`phase1_knowledgeBase`) on `:8101`
- Phase 2 (`phase2_weeklyPulse`) on `:8102`
- Phase 3 (`phase3_voiceScheduler`) on `:8103`
- Phase 4 Gateway (`phase4_integrationHub`) on `:8000`
- Phase 5 Frontend (`phase5_frontend`) on `:3000`

## Start commands

From repository root, run each in separate terminals:

```bash
python3 -m uvicorn phase1_knowledgeBase.app.main:app --host 0.0.0.0 --port 8101
python3 -m uvicorn phase2_weeklyPulse.app.main:app --host 0.0.0.0 --port 8102
python3 -m uvicorn phase3_voiceScheduler.app.main:app --host 0.0.0.0 --port 8103
PHASE1_BASE_URL=http://localhost:8101 PHASE2_BASE_URL=http://localhost:8102 PHASE3_BASE_URL=http://localhost:8103 python3 -m uvicorn phase4_integrationHub.app.main:app --host 0.0.0.0 --port 8000
cd phase5_frontend && npm start
```

## Verification endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dashboard/stats
curl http://localhost:8000/api/v1/pillar-b/weekly-pulse
curl -X POST http://localhost:8000/api/v1/evals/integration
```

If these pass, the full Phase 1→5 chain is wired.
