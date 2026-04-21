"""Sufficiency check service for Self-RAG loop control."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List


class SufficiencyCheckService:
    def __init__(self, llm_client, model: str = "openai/gpt-4o-mini"):
        self.llm_client = llm_client
        self.model = model

    async def evaluate(self, query: str, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not matches:
            return {
                "sufficient": False,
                "reason": "No retrieved chunks",
                "expanded_query": query,
            }

        compact_chunks = []
        for m in matches[:10]:
            meta = m.get("metadata", {})
            compact_chunks.append(
                {
                    "id": m.get("id"),
                    "score": round(float(m.get("score", 0.0)), 4),
                    "source": meta.get("document", "M1"),
                    "chunk_type": meta.get("chunk_type", ""),
                    "text": (meta.get("text", "") or "")[:320],
                }
            )

        prompt = (
            "You are evaluating retrieval quality for a RAG system.\n"
            "Respond with strict JSON only:\n"
            '{"sufficient": true|false, "reason": "short reason", "expanded_query": "improved retrieval query when insufficient"}'
        )
        try:
            resp = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON. Be strict and concise."},
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nQuestion: {query}\n\nRetrieved chunks:\n{json.dumps(compact_chunks, ensure_ascii=True)}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=220,
            )
            payload = self._parse_json(resp.choices[0].message.content or "")
            if isinstance(payload, dict) and "sufficient" in payload:
                expanded = payload.get("expanded_query") or query
                return {
                    "sufficient": bool(payload.get("sufficient")),
                    "reason": str(payload.get("reason", ""))[:180] or "Model sufficiency check",
                    "expanded_query": str(expanded).strip() or query,
                }
        except Exception:
            pass

        # Heuristic fallback
        avg_score = sum(float(m.get("score", 0.0)) for m in matches) / len(matches)
        sufficient = avg_score >= 0.55
        return {
            "sufficient": sufficient,
            "reason": "Heuristic fallback based on similarity scores",
            "expanded_query": query,
        }

    def _parse_json(self, content: str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                return {}
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
