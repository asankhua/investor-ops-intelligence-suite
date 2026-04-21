"""Grounded response generation with strict JSON output."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List


class ResponseGeneratorService:
    def __init__(self, llm_client, model: str = "openai/gpt-4o"):
        self.llm_client = llm_client
        self.model = model

    async def generate(self, query: str, matches: List[Dict[str, Any]], max_bullets: int = 6) -> Dict[str, Any]:
        docs = self._build_docs(matches)
        if not docs:
            return {
                "bullets": [{"text": "I could not find enough grounded information in indexed sources.", "sources": []}],
                "sources_used": [],
                "citations": [],
            }

        prompt = (
            "Answer the question using ONLY the provided documents.\n"
            "No generic finance explanations unless directly present in the documents.\n"
            f"Return maximum {max_bullets} bullets.\n"
            "Return strict JSON only with this shape:\n"
            '{"bullets":["..."],"sources_used":["M1","M1.1"],"citations":[{"bullet_index":0,"source":"M1","doc_id":"chunk_1"}]}'
        )
        try:
            resp = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a facts-only RAG answer formatter. Output valid JSON only."},
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nQuestion: {query}\n\nDocuments:\n{json.dumps(docs, ensure_ascii=True)}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=700,
            )
            payload = self._parse_json(resp.choices[0].message.content or "")
            return self._normalize_payload(payload, docs, max_bullets)
        except Exception:
            return self._fallback_from_docs(docs, max_bullets)

    def _build_docs(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        docs = []
        for m in matches[:10]:
            meta = m.get("metadata", {})
            docs.append(
                {
                    "doc_id": m.get("id"),
                    "source": meta.get("document", "M1"),
                    "text": meta.get("text", ""),
                }
            )
        return docs

    def _normalize_payload(self, payload: Any, docs: List[Dict[str, Any]], max_bullets: int) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return self._fallback_from_docs(docs, max_bullets)

        bullets_raw = payload.get("bullets", [])
        bullets_text = [b.strip() for b in bullets_raw if isinstance(b, str) and b.strip()][:max_bullets]
        if not bullets_text:
            return self._fallback_from_docs(docs, max_bullets)

        citations = payload.get("citations", [])
        valid_doc_ids = {d["doc_id"] for d in docs}
        normalized_citations = []
        for c in citations:
            if not isinstance(c, dict):
                continue
            doc_id = c.get("doc_id")
            if doc_id not in valid_doc_ids:
                continue
            normalized_citations.append(
                {
                    "bullet_index": int(c.get("bullet_index", 0)),
                    "source": str(c.get("source", "M1")),
                    "doc_id": doc_id,
                }
            )

        per_bullet_sources = {idx: set() for idx in range(len(bullets_text))}
        for c in normalized_citations:
            bi = c["bullet_index"]
            if 0 <= bi < len(bullets_text):
                per_bullet_sources[bi].add(c["source"])

        bullets = [{"text": text, "sources": sorted(list(per_bullet_sources[i]))} for i, text in enumerate(bullets_text)]

        sources_used_raw = payload.get("sources_used", [])
        sources_used = sorted({s for s in sources_used_raw if isinstance(s, str) and s})
        if not sources_used:
            sources_used = sorted({d["source"] for d in docs})

        return {
            "bullets": bullets,
            "sources_used": sources_used,
            "citations": normalized_citations,
        }

    def _fallback_from_docs(self, docs: List[Dict[str, Any]], max_bullets: int) -> Dict[str, Any]:
        bullets = []
        citations = []
        for idx, d in enumerate(docs[:max_bullets]):
            text = (d["text"] or "").strip()
            first_sentence = text.split(".")[0].strip()
            if first_sentence:
                bullets.append({"text": f"{first_sentence}.", "sources": [d["source"]]})
                citations.append({"bullet_index": len(bullets) - 1, "source": d["source"], "doc_id": d["doc_id"]})

        if not bullets:
            bullets = [{"text": "I could not find enough grounded information in indexed sources.", "sources": []}]

        return {
            "bullets": bullets,
            "sources_used": sorted({d["source"] for d in docs}),
            "citations": citations,
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
