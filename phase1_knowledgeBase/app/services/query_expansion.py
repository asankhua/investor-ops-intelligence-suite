"""LLM-backed query expansion for Self-RAG."""

from __future__ import annotations

import json
import re
from typing import List


class QueryExpansionService:
    def __init__(self, llm_client, model: str = "openai/gpt-4o-mini"):
        self.llm_client = llm_client
        self.model = model

    async def expand(self, query: str) -> List[str]:
        prompt = (
            "Generate up to 3 semantically equivalent retrieval queries for mutual fund knowledge search.\n"
            "Always include the original query as one variant.\n"
            "Return strict JSON only:\n"
            '{"variants":["..."]}'
        )
        try:
            resp = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You produce only valid compact JSON."},
                    {"role": "user", "content": f"{prompt}\n\nQuery: {query}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=200,
            )
            content = resp.choices[0].message.content or ""
            payload = self._parse_json(content)
            variants = payload.get("variants", []) if isinstance(payload, dict) else []
            return self._normalize_variants(query, variants)
        except Exception:
            return self._fallback_variants(query)

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

    def _normalize_variants(self, original: str, variants: List[str]) -> List[str]:
        cleaned = [original]
        for item in variants:
            if isinstance(item, str):
                value = item.strip()
                if value:
                    cleaned.append(value)
        unique = []
        seen = set()
        for item in cleaned:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique[:3]

    def _fallback_variants(self, query: str) -> List[str]:
        variants = [query]
        q = query.lower()
        if "exit load" in q:
            variants.extend(["mutual fund redemption fee", "exit load holding period rules"])
        elif "expense ratio" in q:
            variants.extend(["mutual fund annual management fee", "expense ratio percentage fund"])
        elif "nav" in q:
            variants.extend(["net asset value fund", "fund nav latest value"])
        elif "aum" in q:
            variants.extend(["assets under management fund size", "fund aum in crore"])
        return self._normalize_variants(query, variants)
