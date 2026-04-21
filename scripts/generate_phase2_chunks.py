import json
from pathlib import Path
from datetime import datetime


def build_chunks(repo_root: Path) -> dict:
    data_dir = repo_root / "data" / "ragData"
    chunks = []
    chunk_id = 0
    latest_scraped_at = None

    for json_file in sorted(data_dir.glob("*.json")):
        data = json.loads(json_file.read_text())
        scraped_at = data.get("last_scraped_at")
        if scraped_at and (latest_scraped_at is None or scraped_at > latest_scraped_at):
            latest_scraped_at = scraped_at
        fund_name = data.get("fund_name") or data.get("name") or json_file.stem.replace("-", " ").title()
        scheme_id = data.get("scheme_id", json_file.stem)
        source_url = data.get("source_url")
        overview = data.get("overview", {})

        chunks.append(
            {
                "id": f"chunk_{chunk_id}",
                "text": (
                    f"Fund: {fund_name}. NAV: {overview.get('nav', 'N/A')}. "
                    f"Benchmark: {overview.get('benchmark', 'N/A')}. "
                    f"AUM: {overview.get('aum', 'N/A')}. "
                    f"Risk: {overview.get('risk', 'N/A')}."
                ),
                "scheme_id": scheme_id,
                "scheme_name": fund_name,
                "source_url": source_url,
                "chunk_type": "overview",
                "tags": ["overview", "nav", "benchmark", "aum", "risk"],
                "scraped_at": scraped_at,
            }
        )
        chunk_id += 1

        chunks.append(
            {
                "id": f"chunk_{chunk_id}",
                "text": (
                    f"Fund: {fund_name}. Returns since inception: {overview.get('returns_since_inception', 'N/A')}. "
                    f"1Y return: {overview.get('returns_1y', 'N/A')}. "
                    f"3Y return: {overview.get('returns_3y', 'N/A')}. "
                    f"5Y return: {overview.get('returns_5y', 'N/A')}."
                ),
                "scheme_id": scheme_id,
                "scheme_name": fund_name,
                "source_url": source_url,
                "chunk_type": "returns",
                "tags": ["returns", "performance"],
                "scraped_at": scraped_at,
            }
        )
        chunk_id += 1

        chunks.append(
            {
                "id": f"chunk_{chunk_id}",
                "text": (
                    f"Fund: {fund_name}. Expense ratio: {overview.get('expense_ratio', 'N/A')}. "
                    f"Exit load: {overview.get('exit_load', 'N/A')}. "
                    f"Lock-in: {overview.get('lock_in', 'N/A')}. "
                    f"Minimum lumpsum: {overview.get('min_lumpsum', 'N/A')}. "
                    f"Minimum SIP: {overview.get('min_sip', 'N/A')}."
                ),
                "scheme_id": scheme_id,
                "scheme_name": fund_name,
                "source_url": source_url,
                "chunk_type": "fees",
                "tags": ["fees", "expense-ratio", "exit-load", "lock-in", "min-investment"],
                "scraped_at": scraped_at,
            }
        )
        chunk_id += 1

        notes = []
        if data.get("data_freshness_note"):
            notes.append(f"Freshness note: {data['data_freshness_note']}")
        if data.get("simulation_note"):
            notes.append(f"Simulation note: {data['simulation_note']}")

        if notes:
            chunks.append(
                {
                    "id": f"chunk_{chunk_id}",
                    "text": f"Fund: {fund_name}. " + " ".join(notes),
                    "scheme_id": scheme_id,
                    "scheme_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "notes",
                    "tags": ["notes", "freshness"],
                    "scraped_at": scraped_at,
                }
            )
            chunk_id += 1

    generated_at = latest_scraped_at or datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return {
        "generated_at": generated_at,
        "source": "data/ragData",
        "total_chunks": len(chunks),
        "chunks": chunks,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    payload = build_chunks(repo_root)
    out_dir = repo_root / "data" / "chunking"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "chunks.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote {payload['total_chunks']} chunks to {out_file}")


if __name__ == "__main__":
    main()
