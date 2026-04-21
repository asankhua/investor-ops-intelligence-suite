"""Self-RAG pipeline for Phase 1 backend."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .query_expansion import QueryExpansionService
from .response_generator import ResponseGeneratorService
from .sufficiency_check import SufficiencyCheckService

logger = logging.getLogger(__name__)


class SelfRAGPipeline:
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store
        self.repo_root = Path(__file__).parent.parent.parent.parent
        self.data_dir = self.repo_root / "data" / "ragData"
        self.pre_chunked_file = self.repo_root / "data" / "chunking" / "chunks.json"
        self.reference_chunked_file = self.repo_root / "rag-based-mutualfund-faqchatbot" / "data" / "phase2" / "chunks.json"
        self.llm_client = None
        self.chat_model = os.getenv("OPENROUTER_CHAT_MODEL", "openai/gpt-4o")
        self.reflect_model = os.getenv("OPENROUTER_REFLECT_MODEL", "openai/gpt-4o-mini")
        self._fund_name_cache: Optional[List[str]] = None
        self.education_links = [
            "https://www.sebi.gov.in/sebi_data/faqfiles/jan-2023/1675088699723.pdf",
            "https://www.indmoney.com/mutual-funds",
        ]
        self._init_llm()
        self.query_expansion = QueryExpansionService(self.llm_client, self.reflect_model)
        self.sufficiency_checker = SufficiencyCheckService(self.llm_client, self.reflect_model)
        self.response_generator = ResponseGeneratorService(self.llm_client, self.chat_model)

    def _init_llm(self) -> None:
        import openai

        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.llm_client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        logger.info("Self-RAG LLM client initialized")

    def _normalize_fund_name(self, value: str) -> str:
        if not value:
            return ""
        cleaned = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
        return re.sub(r"\s+", " ", cleaned)

    def _load_fund_names(self) -> List[str]:
        if self._fund_name_cache is not None:
            return self._fund_name_cache
        funds: List[str] = []
        for json_file in self.data_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                name = data.get("name") or data.get("fund_name")
                if name:
                    funds.append(name)
            except Exception:
                continue
        self._fund_name_cache = sorted(list(set(funds)))
        return self._fund_name_cache

    def _infer_fund_from_query(self, query: str) -> Optional[str]:
        query_norm = self._normalize_fund_name(query)
        if not query_norm:
            return None
        stop_words = {
            "hdfc",
            "fund",
            "direct",
            "plan",
            "growth",
            "option",
            "etf",
            "index",
            "for",
            "the",
            "of",
            "and",
            "nav",
            "exit",
            "load",
            "expense",
            "ratio",
            "aum",
            "what",
            "is",
        }
        best_match = None
        best_score = 0
        single_token_hits: List[str] = []
        for fund in self._load_fund_names():
            fnorm = self._normalize_fund_name(fund)
            if fnorm and fnorm in query_norm:
                return fund
            tokens = [t for t in fnorm.split() if t not in stop_words]
            if not tokens:
                continue
            hits = sum(1 for t in tokens if t in query_norm)
            if hits == 1 and len(tokens) == 1 and tokens[0] in query_norm:
                single_token_hits.append(fund)
            score = hits * 10 + len(" ".join(tokens))
            if hits >= 2 and score > best_score:
                best_score = score
                best_match = fund
        if len(single_token_hits) == 1:
            return single_token_hits[0]
        return best_match

    def _infer_funds_from_query(self, query: str) -> List[str]:
        query_norm = self._normalize_fund_name(query)
        matched: List[str] = []
        for fund in self._load_fund_names():
            fnorm = self._normalize_fund_name(fund)
            if fnorm and fnorm in query_norm:
                matched.append(fund)
                continue
            tokens = [t for t in fnorm.split() if t not in {"hdfc", "fund", "direct", "plan", "growth", "option", "etf", "index"}]
            if tokens and all(t in query_norm for t in tokens[:2]):
                matched.append(fund)
        # dedupe keep order
        unique = []
        seen = set()
        for fund in matched:
            key = fund.lower()
            if key not in seen:
                seen.add(key)
                unique.append(fund)
        return unique

    def _is_nav_query(self, query: str) -> bool:
        q = (query or "").strip().lower()
        return q in {"nav", "net asset value"} or " nav " in f" {q} "

    def _is_exit_load_query(self, query: str) -> bool:
        q = (query or "").strip().lower()
        return "exit load" in q or "redemption charge" in q

    def _is_expense_ratio_query(self, query: str) -> bool:
        q = (query or "").strip().lower()
        return "expense ratio" in q

    def _is_aum_query(self, query: str) -> bool:
        q = (query or "").strip().lower()
        return q == "aum" or "assets under management" in q or "aum" in q

    def _is_advisory_query(self, query: str) -> bool:
        q = (query or "").lower()
        patterns = [
            "should i buy",
            "should i sell",
            "should i hold",
            "best fund",
            "which fund is best",
            "recommend",
            "advice",
            "portfolio",
            "allocation",
            "good for me",
        ]
        return any(p in q for p in patterns)

    def _is_personal_data_query(self, query: str) -> bool:
        q = (query or "").lower()
        patterns = [
            "my kyc",
            "my portfolio",
            "my pan",
            "my aadhaar",
            "my aadhar",
            "my account",
            "my sip amount",
            "my phone",
            "my email",
            "otp",
            "login",
            "password",
        ]
        return any(p in q for p in patterns)

    def _boost_fund_specific_matches(self, matches: List[Dict[str, Any]], fund_name: Optional[str]) -> List[Dict[str, Any]]:
        if not fund_name:
            return matches
        target = self._normalize_fund_name(fund_name)
        boosted = []
        for m in matches:
            metadata = m.get("metadata", {})
            score = float(m.get("score", 0.0))
            if self._normalize_fund_name(metadata.get("fund_name", "")) == target:
                score += 0.25
            item = dict(m)
            item["score"] = score
            boosted.append(item)
        boosted.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return boosted

    def _diversify_matches_across_funds(self, matches: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        diversified: List[Dict[str, Any]] = []
        seen_funds = set()
        for m in matches:
            fund = m.get("metadata", {}).get("fund_name")
            if fund and fund not in seen_funds:
                diversified.append(m)
                seen_funds.add(fund)
            if len(diversified) >= top_k:
                return diversified
        for m in matches:
            if m not in diversified:
                diversified.append(m)
            if len(diversified) >= top_k:
                break
        return diversified

    def _dedupe_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_id: Dict[str, Dict[str, Any]] = {}
        for m in matches:
            mid = m.get("id")
            if not mid:
                continue
            if mid not in by_id or float(m.get("score", 0.0)) > float(by_id[mid].get("score", 0.0)):
                by_id[mid] = m
        return sorted(by_id.values(), key=lambda x: float(x.get("score", 0.0)), reverse=True)

    def _query_single_variant(self, query_text: str, top_k: int, filter_dict: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        vector = self.embedder.embed_query(query_text)
        return self.vector_store.query(vector=vector, top_k=top_k, filter_dict=filter_dict)

    def _build_citations(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        for m in matches:
            meta = m.get("metadata", {})
            text = meta.get("text", "") or ""
            citations.append(
                {
                    "chunk_id": m.get("id"),
                    "document": meta.get("document", "M1"),
                    "preview": text[:150] + "..." if len(text) > 150 else text,
                    "score": float(m.get("score", 0.0)),
                    "source_url": meta.get("source_url"),
                }
            )
        return citations

    def _extract_rows(self, matches: List[Dict[str, Any]], regex: re.Pattern, metric_key: str, default_doc: str) -> List[Dict[str, str]]:
        rows_by_fund: Dict[str, Dict[str, str]] = {}
        for m in matches:
            meta = m.get("metadata", {})
            text = meta.get("text", "") or ""
            fund = meta.get("fund_name")
            if not fund or not text:
                continue
            hit = regex.search(text)
            if not hit:
                continue
            value = hit.group(1).strip()
            row = {"fund_name": fund, metric_key: value, "document": meta.get("document", default_doc)}
            if regex.groups >= 2:
                row["date"] = hit.group(2).strip()
            rows_by_fund[fund] = row
        return sorted(rows_by_fund.values(), key=lambda r: r["fund_name"])

    def _filter_rows_by_fund(self, rows: List[Dict[str, str]], fund_name: Optional[str]) -> List[Dict[str, str]]:
        if not fund_name:
            return rows
        target = self._normalize_fund_name(fund_name)
        filtered = [r for r in rows if self._normalize_fund_name(r["fund_name"]) == target]
        return filtered or rows

    async def query(self, query: str, top_k: int = 5, fund_name: Optional[str] = None) -> Dict[str, Any]:
        inferred_funds = self._infer_funds_from_query(query)
        resolved_fund_name = fund_name or (inferred_funds[0] if len(inferred_funds) == 1 else None)
        q_lower = (query or "").lower()
        combined_query = len(inferred_funds) > 1 or any(
            token in q_lower for token in ["compare", "comparison", "versus", " vs ", "difference between"]
        )

        if self._is_personal_data_query(query):
            return {
                "bullets": [
                    {
                        "text": "I cannot access personal/account-specific information. I only provide public facts from indexed scheme data.",
                        "sources": self.education_links,
                    }
                ],
                "citations": [],
                "self_rag": {"query_expansion": "policy route", "sufficiency_check": "✅ Personal/account query refused", "retrieved_chunks": 0},
                "sources_used": [],
                "self_rag_loops": 0,
                "query_variants": [query],
                "structured_citations": [],
            }

        if self._is_advisory_query(query):
            return {
                "bullets": [
                    {
                        "text": "I cannot provide investment advice or recommendations. I can share objective fund facts from indexed data.",
                        "sources": self.education_links,
                    }
                ],
                "citations": [],
                "self_rag": {"query_expansion": "policy route", "sufficiency_check": "✅ Advisory query refused", "retrieved_chunks": 0},
                "sources_used": [],
                "self_rag_loops": 0,
                "query_variants": [query],
                "structured_citations": [],
            }

        nav_query = self._is_nav_query(query)
        exit_query = self._is_exit_load_query(query)
        expense_query = self._is_expense_ratio_query(query)
        aum_query = self._is_aum_query(query)
        metric_query = nav_query or exit_query or expense_query or aum_query

        query_variants = await self.query_expansion.expand(query)
        retrieval_k = max(top_k, 24) if metric_query and not resolved_fund_name else max(top_k, 10)

        filter_dict: Dict[str, Any] = {"document": {"$in": ["M1", "M1.1"]}}
        if fund_name:
            filter_dict["fund_name"] = {"$eq": resolved_fund_name}
        elif len(inferred_funds) > 1:
            filter_dict["fund_name"] = {"$in": inferred_funds}
        elif resolved_fund_name:
            filter_dict["fund_name"] = {"$eq": resolved_fund_name}
        if nav_query or aum_query:
            filter_dict["chunk_type"] = {"$eq": "overview"}
        elif exit_query or expense_query:
            filter_dict["chunk_type"] = {"$eq": "fees"}

        all_matches: List[Dict[str, Any]] = []
        for variant in query_variants:
            all_matches.extend(self._query_single_variant(variant, retrieval_k, filter_dict))
        matches = self._dedupe_matches(all_matches)

        sufficiency = await self.sufficiency_checker.evaluate(query, matches[:10])
        loops = 0
        if not bool(sufficiency.get("sufficient")) and loops < 1:
            loops += 1
            expanded_query = str(sufficiency.get("expanded_query") or query).strip() or query
            extra = self._query_single_variant(expanded_query, retrieval_k, filter_dict)
            matches = self._dedupe_matches(matches + extra)
            if expanded_query.lower() not in {v.lower() for v in query_variants}:
                query_variants.append(expanded_query)

        matches = self._boost_fund_specific_matches(matches, resolved_fund_name)
        if not resolved_fund_name:
            matches = self._diversify_matches_across_funds(matches, retrieval_k)
        matches = matches[: max(top_k, 10)]

        citations = self._build_citations(matches)
        sources_used = sorted({c["document"] for c in citations if c.get("document")})

        if nav_query:
            rows = self._extract_rows(matches, re.compile(r"NAV:\s*(.*?)\s*\(as on\s*([^)]+)\)", re.IGNORECASE), "nav", "M1")
            rows = self._filter_rows_by_fund(rows, resolved_fund_name)
            if rows:
                bullets = [{"text": f"{r['fund_name']}: NAV {r['nav']} (as on {r['date']}).", "sources": [r["document"]]} for r in rows]
                return self._build_response_payload(
                    bullets=bullets,
                    citations=citations,
                    query_variants=query_variants,
                    loops=loops,
                    sources_used=sources_used,
                    sufficiency_text="✅ NAV values extracted from retrieved overview chunks",
                    retrieved_chunks=len(matches),
                    enforce_six_bullets=combined_query,
                )

        if exit_query:
            rows = self._extract_rows(matches, re.compile(r"Exit load:\s*(.*?)\.\s*Lock-in:", re.IGNORECASE), "exit_load", "M1.1")
            rows = self._filter_rows_by_fund(rows, resolved_fund_name)
            if rows:
                bullets = [{"text": f"{r['fund_name']}: Exit load {r['exit_load']}.", "sources": [r["document"]]} for r in rows]
                return self._build_response_payload(
                    bullets=bullets,
                    citations=citations,
                    query_variants=query_variants,
                    loops=loops,
                    sources_used=sources_used,
                    sufficiency_text="✅ Exit load values extracted from retrieved fee chunks",
                    retrieved_chunks=len(matches),
                    enforce_six_bullets=combined_query,
                )

        if expense_query:
            rows = self._extract_rows(matches, re.compile(r"Expense ratio:\s*(.*?)\.\s*Exit load:", re.IGNORECASE), "expense_ratio", "M1.1")
            rows = self._filter_rows_by_fund(rows, resolved_fund_name)
            if rows:
                bullets = [{"text": f"{r['fund_name']}: Expense ratio {r['expense_ratio']}.", "sources": [r["document"]]} for r in rows]
                return self._build_response_payload(
                    bullets=bullets,
                    citations=citations,
                    query_variants=query_variants,
                    loops=loops,
                    sources_used=sources_used,
                    sufficiency_text="✅ Expense ratio values extracted from retrieved fee chunks",
                    retrieved_chunks=len(matches),
                    enforce_six_bullets=combined_query,
                )

        if aum_query:
            rows = self._extract_rows(matches, re.compile(r"AUM:\s*(.*?)\.\s*Risk:", re.IGNORECASE), "aum", "M1")
            rows = self._filter_rows_by_fund(rows, resolved_fund_name)
            if rows:
                bullets = [{"text": f"{r['fund_name']}: AUM {r['aum']}.", "sources": [r["document"]]} for r in rows]
                return self._build_response_payload(
                    bullets=bullets,
                    citations=citations,
                    query_variants=query_variants,
                    loops=loops,
                    sources_used=sources_used,
                    sufficiency_text="✅ AUM values extracted from retrieved overview chunks",
                    retrieved_chunks=len(matches),
                    enforce_six_bullets=combined_query,
                )

        generated = await self.response_generator.generate(query, matches, max_bullets=6)
        return self._build_response_payload(
            bullets=generated["bullets"],
            citations=citations,
            query_variants=query_variants,
            loops=loops,
            sources_used=generated.get("sources_used", sources_used),
            structured_citations=generated.get("citations", []),
            sufficiency_text=f"{'✅' if sufficiency.get('sufficient') else '⚠️'} {sufficiency.get('reason', 'Sufficiency check complete')}",
            retrieved_chunks=len(matches),
            enforce_six_bullets=combined_query,
        )

    def _build_response_payload(
        self,
        bullets: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        query_variants: List[str],
        loops: int,
        sources_used: List[str],
        sufficiency_text: str,
        retrieved_chunks: int,
        structured_citations: Optional[List[Dict[str, Any]]] = None,
        enforce_six_bullets: bool = False,
    ) -> Dict[str, Any]:
        bullets = list(bullets or [])
        structured_citations = list(structured_citations or [])

        if enforce_six_bullets and len(bullets) < 6:
            existing = {b.get("text", "").strip().lower() for b in bullets}
            for citation in citations:
                if len(bullets) >= 6:
                    break
                preview = (citation.get("preview") or "").replace("\n", " ").strip()
                if preview.endswith("..."):
                    preview = preview[:-3].strip()
                if not preview:
                    continue
                text = preview if preview.endswith(".") else f"{preview}."
                key = text.lower()
                if key in existing:
                    continue

                source = citation.get("document")
                bullets.append({"text": text, "sources": [source] if source else []})
                existing.add(key)

                chunk_id = citation.get("chunk_id")
                if source and chunk_id:
                    structured_citations.append(
                        {
                            "bullet_index": len(bullets) - 1,
                            "source": source,
                            "doc_id": chunk_id,
                        }
                    )

        if enforce_six_bullets:
            while len(bullets) < 6:
                bullets.append({"text": "Not specified in available documents.", "sources": []})
            bullets = bullets[:6]

        return {
            "bullets": bullets[:6],
            "citations": citations,
            "self_rag": {
                "query_expansion": f"{len(query_variants)} variants",
                "sufficiency_check": sufficiency_text,
                "retrieved_chunks": retrieved_chunks,
            },
            "sources_used": sources_used,
            "self_rag_loops": loops,
            "query_variants": query_variants,
            "structured_citations": structured_citations,
        }

    def _parse_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        text = str(value)
        hit = re.search(r"[\d,.]+", text)
        if not hit:
            return None
        try:
            return float(hit.group(0).replace(",", ""))
        except ValueError:
            return None

    def _load_prechunked(self) -> List[Dict[str, Any]]:
        source_file = self.pre_chunked_file if self.pre_chunked_file.exists() else self.reference_chunked_file
        if not source_file.exists():
            return []
        try:
            payload = json.loads(source_file.read_text())
            chunks = payload.get("chunks", payload) if isinstance(payload, dict) else payload
            if isinstance(chunks, list):
                return chunks
        except Exception as exc:
            logger.warning("Failed loading pre-chunked data: %s", exc)
        return []

    def _build_chunks_from_ragdata(self) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        chunk_id = 0
        for json_file in sorted(self.data_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text())
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
                            f"AUM: {overview.get('aum', 'N/A')}. Risk: {overview.get('risk', 'N/A')}."
                        ),
                        "scheme_id": scheme_id,
                        "scheme_name": fund_name,
                        "source_url": source_url,
                        "chunk_type": "overview",
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
                    }
                )
                chunk_id += 1
                chunks.append(
                    {
                        "id": f"chunk_{chunk_id}",
                        "text": (
                            f"Fund: {fund_name}. Expense ratio: {overview.get('expense_ratio', 'N/A')}. "
                            f"Exit load: {overview.get('exit_load', 'N/A')}. Lock-in: {overview.get('lock_in', 'N/A')}. "
                            f"Minimum lumpsum: {overview.get('min_lumpsum', 'N/A')}. Minimum SIP: {overview.get('min_sip', 'N/A')}."
                        ),
                        "scheme_id": scheme_id,
                        "scheme_name": fund_name,
                        "source_url": source_url,
                        "chunk_type": "fees",
                    }
                )
                chunk_id += 1
            except Exception as exc:
                logger.error("Chunk build failed for %s: %s", json_file, exc)
        return chunks

    async def index_documents(self) -> Dict[str, Any]:
        import asyncio

        chunks = self._load_prechunked() or self._build_chunks_from_ragdata()
        if not chunks:
            raise RuntimeError("No chunks found to index. Check data/ragData or data/phase2/chunks.json.")

        vectors: List[Dict[str, Any]] = []
        for chunk in chunks:
            text = chunk.get("text", "")
            if not text:
                continue
            fund_name = chunk.get("scheme_name") or chunk.get("fund_name")
            ctype = chunk.get("chunk_type", "overview")
            source = "M1.1" if ctype in {"fees", "min_investment"} else "M1"
            metadata = {
                "text": text,
                "document": source,
                "fund_name": fund_name,
                "scheme_id": chunk.get("scheme_id"),
                "source_url": chunk.get("source_url"),
                "chunk_type": ctype,
                "source": source,
                "expense_ratio": self._parse_float(text if "expense ratio" in text.lower() else None),
                "exit_load": self._parse_float(text if "exit load" in text.lower() else None),
                "aum_cr": self._parse_float(text if "aum" in text.lower() else None),
            }
            metadata = {k: v for k, v in metadata.items() if v is not None}
            vectors.append({"id": str(chunk.get("id")), "text": text, "metadata": metadata})

        batch_size = 64
        total = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            embeddings = self.embedder.embed_documents([b["text"] for b in batch])
            payload = []
            for j, b in enumerate(batch):
                payload.append({"id": b["id"], "values": embeddings[j], "metadata": b["metadata"]})
            self.vector_store.upsert(payload)
            total += len(payload)
            await asyncio.sleep(0.05)

        logger.info("Indexed %s chunks into Pinecone", total)
        return {"count": total}

    async def search_funds(self, query: str) -> List[Dict[str, Any]]:
        funds = []
        for json_file in self.data_dir.glob("*.json"):
            fallback_name = json_file.stem.replace("-", " ").title()
            try:
                data = json.loads(json_file.read_text())
                name = data.get("fund_name") or data.get("name") or fallback_name
                if query and query.lower() not in name.lower():
                    continue
                funds.append({"name": name, "category": data.get("category", "Unknown"), "amc": data.get("amc", "HDFC")})
            except Exception:
                if not query or query.lower() in fallback_name.lower():
                    funds.append({"name": fallback_name, "category": "Unknown", "amc": "HDFC"})
        return funds[:20]

    async def get_sources(self) -> List[Dict[str, Any]]:
        sources = []
        for json_file in self.data_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                sources.append(
                    {
                        "id": data.get("scheme_id", json_file.stem),
                        "name": data.get("name", json_file.stem.replace("-", " ").title()),
                        "description": "Public INDMoney scheme page",
                        "source_url": data.get("source_url"),
                    }
                )
            except Exception:
                continue
        return sources
