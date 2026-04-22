"""Run a Phase 2 Weekly Pulse refresh from Play Store reviews."""

from __future__ import annotations

from pathlib import Path
import json
import os
import sys

from dotenv import load_dotenv


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    # Ensure project modules are importable regardless of caller working directory.
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    load_dotenv(repo_root / ".env")

    # Default to the URL requested by the user if not set.
    os.environ.setdefault(
        "PLAYSTORE_REVIEW_URLS",
        "https://play.google.com/store/apps/details?id=in.indwealth&hl=en_IN",
    )

    try:
        from phase2_weeklyPulse.app.services.pulse_service import PulseService

        service = PulseService(repo_root)
        pulse = service.refresh(fetch_live_reviews=True)
        scheduler_result = service.run_scheduler_if_due()

        payload = {
            "status": "success",
            "generated_at": pulse.get("generated_at"),
            "reviews_source": pulse.get("reviews_source"),
            "reviews_processed": pulse.get("raw_reviews_processed"),
            "top_theme": (pulse.get("top_themes") or [{}])[0].get("theme"),
            "scheduler_result": scheduler_result,
        }
        print(json.dumps(payload, indent=2))
        return 0
    except Exception as exc:
        print(f"Weekly pulse refresh failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
