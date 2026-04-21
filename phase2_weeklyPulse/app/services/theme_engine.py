"""Theme extraction + sentiment heuristics for weekly pulse."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import math
import re


THEME_KEYWORDS = {
    "Login Issues": {"login", "otp", "password", "biometric", "sign", "signin", "logout"},
    "Fee Transparency": {"fee", "charges", "brokerage", "mtf", "exit load", "pricing", "commission"},
    "Performance & Stability": {"slow", "crash", "white screen", "bug", "working poor", "lag", "down"},
    "Feature Requests": {"add", "feature", "request", "would", "missing", "please"},
    "Support & Service": {"support", "customer care", "help", "response", "service"},
}

POSITIVE_WORDS = {"good", "great", "excellent", "nice", "best", "awesome", "smooth", "super"}
NEGATIVE_WORDS = {"bad", "poor", "hate", "uninstall", "misleading", "looting", "disappeared", "crash", "slow", "down"}


@dataclass
class ThemeResult:
    theme: str
    confidence: float
    mention_count: int
    sentiment_score: float


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _sentiment_from_review(review: Dict[str, Any]) -> float:
    text = _normalize(str(review.get("text", "")))
    rating = review.get("rating")
    score = 0.0
    if isinstance(rating, (int, float)):
        score += (float(rating) - 3.0) / 2.0

    tokens = set(re.findall(r"[a-zA-Z]+", text))
    score += 0.12 * sum(1 for w in tokens if w in POSITIVE_WORDS)
    score -= 0.15 * sum(1 for w in tokens if w in NEGATIVE_WORDS)
    return max(-1.0, min(1.0, score))


def extract_themes(reviews: List[Dict[str, Any]]) -> Tuple[List[ThemeResult], Dict[str, Any]]:
    if not reviews:
        return [], {"keywords": [], "sentiment_trends": [], "mention_volume": []}

    theme_hits: Dict[str, List[float]] = defaultdict(list)
    global_keywords: Counter = Counter()
    dated_sentiment: Dict[str, List[float]] = defaultdict(list)

    for review in reviews:
        text = _normalize(str(review.get("text", "")))
        review_sent = _sentiment_from_review(review)

        date = str(review.get("date", ""))[:10]
        if date:
            dated_sentiment[date].append(review_sent)

        words = re.findall(r"[a-zA-Z]{3,}", text)
        global_keywords.update(words)

        for theme, keys in THEME_KEYWORDS.items():
            if any(k in text for k in keys):
                theme_hits[theme].append(review_sent)

    total_thematic_mentions = sum(len(v) for v in theme_hits.values()) or 1
    results: List[ThemeResult] = []
    for theme, sentiments in theme_hits.items():
        mention_count = len(sentiments)
        # confidence is frequency-adjusted and smooth-clamped between 0.5..0.95
        raw = mention_count / total_thematic_mentions
        confidence = min(0.95, max(0.5, 0.5 + math.sqrt(raw) * 0.45))
        results.append(
            ThemeResult(
                theme=theme,
                confidence=round(confidence, 2),
                mention_count=mention_count,
                sentiment_score=round(sum(sentiments) / max(1, mention_count), 3),
            )
        )

    results.sort(key=lambda t: (t.confidence, t.mention_count), reverse=True)
    top_three = results[:3]

    sentiment_trends = []
    for dt in sorted(dated_sentiment.keys()):
        arr = dated_sentiment[dt]
        sentiment_trends.append({"date": dt, "score": round(sum(arr) / max(1, len(arr)), 3)})

    keyword_items = [
        {"word": w, "frequency": int(c)}
        for (w, c) in global_keywords.most_common(30)
        if w not in {"the", "and", "for", "with", "this", "that", "you", "app", "indmoney"}
    ]

    analytics = {
        "keywords": keyword_items[:20],
        "sentiment_trends": sentiment_trends,
        "mention_volume": [{"theme": t.theme, "count": t.mention_count} for t in top_three],
    }
    return top_three, analytics


def generate_action_ideas(top_themes: List[ThemeResult]) -> List[str]:
    defaults = [
        "Run root-cause analysis on top negative review cluster and publish ETA.",
        "Improve in-app messaging for fee/risk/charge explanations with examples.",
        "Track weekly improvements and close-the-loop with release notes.",
    ]
    if not top_themes:
        return defaults

    mapping = {
        "Login Issues": "Prioritize login reliability fixes (OTP, biometric, session handling).",
        "Fee Transparency": "Publish a fee transparency panel for brokerage/MTF/charges before order confirm.",
        "Performance & Stability": "Ship performance hotfixes and monitor crash/latency regressions daily.",
        "Feature Requests": "Review top requested UX features and schedule at least one quick-win release.",
        "Support & Service": "Strengthen support workflow with faster first-response SLA and clearer escalation.",
    }
    ideas = [mapping.get(t.theme, defaults[0]) for t in top_themes]
    for item in defaults:
        if len(ideas) >= 3:
            break
        if item not in ideas:
            ideas.append(item)
    return ideas[:3]
