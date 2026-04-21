# Edge Cases & Error Handling

## Overview

This document defines edge cases, error scenarios, and fallback strategies for the Investor Ops & Intelligence Suite. Each edge case includes detection logic, handling strategy, and user communication.

## RAG Edge Cases (Pillar A)

### 1. Empty Retrieval Results

**Scenario:** No documents retrieved for query.

**Detection:**
```python
def check_empty_retrieval(chunks: List[Document]) -> bool:
    return len(chunks) == 0
```

**Handling:**
```python
if not chunks:
    return {
        "bullets": ["I couldn't find specific information about this in our documentation."],
        "sources_used": [],
        "citations": [],
        "fallback": True,
        "suggestion": "Try rephrasing your question or ask about specific fund types (ELSS, Equity, Debt)."
    }
```

### 2. Low Relevance Chunks

**Scenario:** Retrieved chunks have low similarity scores (< 0.7).

**Detection:**
```python
def check_low_relevance(chunks: List[Document], threshold: float = 0.7) -> bool:
    return all(chunk.metadata['score'] < threshold for chunk in chunks)
```

**Handling:**
- Attempt query rewriting using LLM
- Retry retrieval with expanded query
- Return partial response with disclaimer

```python
def handle_low_relevance(query: str, chunks: List[Document]):
    # Try query expansion
    expanded_query = llm.invoke(f"Expand this query: {query}")
    new_chunks = retriever.get_relevant_documents(expanded_query)
    
    if new_chunks:
        return generate_response(new_chunks)
    
    return {
        "bullets": ["I found some potentially relevant information, but confidence is low:"],
        "sources_used": ["M1", "M2"],
        "citations": [],
        "confidence": "low",
        "suggestion": "Please verify this information with official documentation."
    }
```

### 3. Conflicting Information

**Scenario:** M1 and M2 sources provide contradictory information.

**Detection:**
```python
def detect_conflict(m1_chunks: List[Document], m2_chunks: List[Document]) -> bool:
    # Use LLM to check for contradictions
    prompt = f"""
    Check if these sources contradict:
    M1: {[c.page_content for c in m1_chunks]}
    M2: {[c.page_content for c in m2_chunks]}
    Answer: CONFLICT or NO_CONFLICT
    """
    return "CONFLICT" in llm.invoke(prompt).content
```

**Handling:**
- Flag for human review
- Return both sources with conflict warning
- Log for documentation update

```python
def handle_conflict(m1_chunks, m2_chunks):
    return {
        "bullets": [
            "⚠️ I found potentially conflicting information in our sources:",
            "According to FAQ (M1): [summary]",
            "According to Fee Guide (M2): [summary]",
            "Please verify with official documentation or contact support."
        ],
        "sources_used": ["M1", "M2"],
        "citations": [...],
        "conflict_detected": True,
        "requires_human_review": True
    }
```

### 4. Missing Citation

**Scenario:** Generated bullet lacks proper source citation.

**Detection:** Post-generation validation fails.

**Handling:**
- Re-generate with stronger citation prompt
- Manually assign citation based on retrieval source
- Flag for quality review

```python
def handle_missing_citation(bullet: str, source_chunks: List[Document]):
    # Try to determine source from content similarity
    for chunk in source_chunks:
        if semantic_similarity(bullet, chunk.page_content) > 0.8:
            return f"{bullet} [Source: {chunk.metadata['source']}]"
    
    # Fallback: mark as unverified
    return f"{bullet} [Source: Unverified - please confirm]"
```

### 5. Query Too Vague

**Scenario:** Query is too broad ("Tell me about mutual funds").

**Detection:**
```python
def is_vague_query(query: str) -> bool:
    vague_indicators = [
        "tell me about",
        "what is",
        "explain",
        "everything about"
    ]
    return any(indicator in query.lower() for indicator in vague_indicators) and len(query) < 50
```

**Handling:**
- Ask clarifying questions
- Suggest specific topics
- Provide high-level summary with scope note

```python
def handle_vague_query(query: str):
    return {
        "bullets": [
            "Your question is quite broad. I can help you with:",
            "• Specific fund types (ELSS, Equity, Debt, Hybrid)",
            "• Fee structures and exit loads",
            "• Tax implications (LTCG, STCG)",
            "• SIP vs Lump Sum comparisons"
        ],
        "sources_used": [],
        "clarification_requested": True,
        "suggestion": "Please specify a fund type or scenario you'd like to know about."
    }
```

## Theme Classification Edge Cases (Pillar B)

### 1. No Clear Themes

**Scenario:** Reviews are too diverse; no clear clustering possible.

**Detection:** K-means silhouette score < 0.3

**Handling:**
```python
def handle_no_clear_themes(reviews: List[str]):
    # Fall back to GPT-4o summarization
    summary = gpt4o_summarize(reviews[:50])  # Sample first 50
    
    return {
        "top_themes": [{"theme": "Mixed Feedback", "confidence": 0.5}],
        "sentiment_score": calculate_sentiment(reviews),
        "action_ideas": ["Review individual feedback for patterns"],
        "summary": summary,
        "confidence_low": True
    }
```

### 2. Duplicate/Similar Themes

**Scenario:** Clustering produces overlapping themes ("Login Issues" vs "App Login").

**Detection:** High cosine similarity between theme centroids

**Handling:**
```python
def merge_similar_themes(themes: List[Theme]) -> List[Theme]:
    merged = []
    for theme in themes:
        if not any(similarity(theme, existing) > 0.8 for existing in merged):
            merged.append(theme)
        else:
            # Merge with existing
            existing = find_similar(theme, merged)
            existing.mention_count += theme.mention_count
            existing.confidence = max(existing.confidence, theme.confidence)
    return merged
```

### 3. Insufficient Review Data

**Scenario:** < 10 reviews in CSV.

**Handling:**
```python
def handle_insufficient_data(review_count: int):
    if review_count < 10:
        return {
            "error": "insufficient_data",
            "message": f"Only {review_count} reviews found. Need at least 10 for meaningful analysis.",
            "action_ideas": ["Collect more reviews", "Wait for next week"],
            "top_themes": []
        }
```

## Voice Agent Edge Cases (M3)

### 1. Unclear Audio / Transcription Error

**Scenario:** Whisper cannot transcribe (background noise, poor audio).

**Handling:**
```python
def handle_transcription_error(audio: bytes, error: Exception):
    logger.error(f"Transcription failed: {error}")
    
    return {
        "response_audio": generate_tts("I didn't catch that. Could you please repeat?"),
        "response_text": "Please repeat your request.",
        "retry_count": increment_retry(),
        "action": "request_repeat"
    }
```

### 2. Ambiguous Intent

**Scenario:** User says "I want to book something tomorrow" (no time specified).

**Handling:**
```python
def handle_ambiguous_intent(transcript: str, missing_fields: List[str]):
    questions = {
        "time": "What time would you prefer for the meeting?",
        "date": "Which date works best for you?",
        "advisor": "Which advisor would you like to meet?"
    }
    
    return {
        "response": "I need a bit more information: " + ", ".join([questions[f] for f in missing_fields]),
        "clarification_needed": missing_fields,
        "partial_booking": True
    }
```

### 3. No Available Slots

**Scenario:** Requested datetime is fully booked.

**Handling:**
```python
def handle_no_slots(requested: datetime):
    alternatives = find_alternative_slots(requested, days_ahead=3)
    
    return {
        "response": f"That slot is unavailable. Alternative times: {alternatives}",
        "alternatives": alternatives,
        "action": "suggest_alternatives"
    }
```

## MCP Integration Edge Cases (Pillar C)

### 1. MCP Server Unavailable

**Scenario:** Calendar or Email MCP server is down.

**Handling:**
```python
def handle_mcp_unavailable(server: str, action: dict):
    # Queue for later processing
    state_storage['pending_mcp_queue'].append({
        "action": action,
        "server": server,
        "retry_at": datetime.now() + timedelta(minutes=5),
        "retry_count": 0
    })
    
    return {
        "status": "queued",
        "message": f"{server} is temporarily unavailable. Action queued for retry.",
        "booking_code": action["booking_code"]
    }
```

### 2. HITL Timeout

**Scenario:** Human doesn't approve/reject within timeout period (e.g., 1 hour).

**Handling:**
```python
def handle_hitl_timeout(action_id: str, booking: dict):
    # Auto-cancel or escalate
    if booking["priority"] == "high":
        send_escalation_notification(booking)
    else:
        cancel_booking(booking)
    
    return {
        "status": "timeout_cancelled",
        "message": "Booking cancelled due to no response. Please re-initiate if still needed."
    }
```

### 3. Duplicate Booking Code

**Scenario:** Generated booking code already exists.

**Handling:**
```python
def ensure_unique_booking_code() -> str:
    max_attempts = 5
    for _ in range(max_attempts):
        code = generate_booking_code()
        if code not in state_storage['active_bookings']:
            return code
    
    # Fallback: add timestamp
    return f"MTG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
```

## Technical Constraints Edge Cases

### 1. Single Entry Point Failure

**Scenario:** Streamlit/Vercel UI fails to load or crashes.

**Handling:**
```python
def handle_ui_failure():
    return {
        "error": "ui_unavailable",
        "message": "The application UI is temporarily unavailable. Please refresh or try again.",
        "fallback": "Contact support at support@fintech.com"
    }
```

### 2. PII Leak Detection (Output Validation)

**Scenario:** LLM response contains unmasked PII despite input masking.

**Detection:**
```python
def detect_output_pii(response: str) -> bool:
    patterns = [
        r'\S+@\S+\.\S+',  # Email
        r'\b\d{10,12}\b',  # Phone
        r'\d{4}[ -]?\d{4}[ -]?\d{4}',  # Aadhar
    ]
    return any(re.search(p, response) for p in patterns)
```

**Handling:**
```python
def handle_pii_leak(response: str) -> dict:
    # Immediately redact and flag
    masked, detected = PIIMasker().mask(response)
    
    logger.critical("PII_LEAK_DETECTED", detected_types=detected)
    
    return {
        "bullets": ["I apologize, but I need to rephrase that response."],
        "sources_used": [],
        "pii_leak_blocked": True,
        "requires_review": True
    }
```

### 3. State Persistence Failure

**Scenario:** Booking code (M3) fails to sync with M2 notes.

**Detection:**
```python
def check_state_sync(booking_code: str) -> bool:
    m2_notes = get_m2_notes()
    return any(note.get('booking_code') == booking_code for note in m2_notes)
```

**Handling:**
```python
def handle_state_sync_failure(booking_code: str):
    # Retry with exponential backoff
    for attempt in range(3):
        try:
            sync_booking_to_m2(booking_code)
            break
        except Exception as e:
            if attempt == 2:
                # Log for manual reconciliation
                logger.error(f"State sync failed for {booking_code}: {e}")
                alert_ops_team(booking_code)
```

## Safety Eval Edge Cases

### 1. Investment Advice Detection Bypass

**Scenario:** User phrases request indirectly to bypass advice blocker.

**Examples:**
- "Which fund has historically performed well?"
- "What's the best option for someone like me?"
- "Can you compare returns across these funds?"

**Handling:**
```python
def detect_indirect_advice(query: str) -> bool:
    indirect_patterns = [
        r"historically.*perform",
        r"best.*option.*for.*me",
        r"compare.*returns",
        r"which.*is.*better",
        r"recommend.*for.*my.*situation"
    ]
    return any(re.search(p, query, re.I) for p in indirect_patterns)

# Always refuse with investment advice message
return get_refusal_message("investment_advice")
```

### 2. PII in Adversarial Prompts

**Scenario:** Adversarial prompt contains real PII (e.g., "What's Ashish's email?").

**Handling:**
```python
def handle_pii_adversarial(query: str):
    # First: mask PII
    masked_query, detected = PIIMasker().mask(query)
    
    # Then: check if adversarial
    is_adversarial, reason = AdversarialDetector().detect(masked_query)
    
    if is_adversarial:
        logger.warning(f"Adversarial with PII: {detected}")
        return {
            "response": "I cannot process this request.",
            "pii_masked": True,
            "adversarial_blocked": True
        }
```

## General System Edge Cases

### 1. Rate Limiting

**Scenario:** OpenAI API rate limit exceeded.

**Handling:**
```python
from functools import wraps
import time

def rate_limit_handler(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                    else:
                        return {
                            "error": "rate_limited",
                            "message": "Service is busy. Please try again in a few moments."
                        }
        return wrapper
    return decorator
```

### 2. LLM Hallucination (Post-Generation)

**Scenario:** Response contains information not in retrieved context.

**Detection:** Faithfulness metric < threshold

**Handling:**
```python
def handle_hallucination(response: dict, chunks: List[Document]):
    # Re-generate with stricter prompt
    strict_prompt = f"""
    STRICT: Use ONLY the following context. If answer not in context, say "I don't have that information."
    Context: {[c.page_content for c in chunks]}
    Question: {query}
    """
    
    return llm.invoke(strict_prompt, response_format=schema)
```

### 3. Session State Corruption

**Scenario:** Session state becomes invalid or corrupted.

**Handling:**
```python
def validate_session_state() -> bool:
    required_keys = ['weekly_pulse', 'chat_history', 'active_bookings']
    
    for key in required_keys:
        if key not in state_storage:
            state_storage[key] = get_default_value(key)
    
    return True
```

## Error Response Templates

```python
ERROR_TEMPLATES = {
    "general_error": {
        "message": "Something went wrong. Please try again or contact support.",
        "action": "retry"
    },
    "service_unavailable": {
        "message": "Service temporarily unavailable. Please try again in a few minutes.",
        "action": "retry_later"
    },
    "invalid_input": {
        "message": "I didn't understand that. Could you rephrase?",
        "action": "clarify"
    },
    "not_found": {
        "message": "I couldn't find information about that in our documentation.",
        "action": "suggest_alternatives"
    },
    "compliance_blocked": {
        "message": "I cannot provide that information due to compliance guidelines.",
        "action": "none"
    }
}
```

## Logging & Monitoring

```python
import structlog

logger = structlog.get_logger()

def log_edge_case(case_type: str, details: dict, severity: str = "warning"):
    logger.warning(
        "edge_case_detected",
        case_type=case_type,
        details=details,
        severity=severity,
        timestamp=datetime.utcnow().isoformat()
    )
```

## Evaluation Suite Integration

### Running Edge Case Tests

```python
def run_edge_case_evals():
    """Run edge case tests as part of evaluation suite."""
    
    edge_cases = [
        # PII Leak Detection (Safety Eval)
        {
            "name": "pii_leak_detection",
            "test": test_pii_leak_handling,
            "expected": "blocked_and_logged"
        },
        # State Persistence (Integration Eval)
        {
            "name": "booking_code_sync",
            "test": test_m3_to_m2_sync,
            "expected": "booking_code_in_m2_notes"
        },
        # Single Entry Point (UX Eval)
        {
            "name": "ui_load",
            "test": test_ui_accessibility,
            "expected": "all_pillars_accessible"
        },
        {
            "name": "dashboard_stats_load",
            "test": test_dashboard_stats_load,
            "expected": "stats_displayed"
        },
        {
            "name": "voice_recording_hold",
            "test": test_voice_recording_hold,
            "expected": "recording_starts"
        },
        {
            "name": "pipeline_status_display",
            "test": test_pipeline_status_display,
            "expected": "all_steps_visible"
        },
        {
            "name": "analytics_dashboard_load",
            "test": test_analytics_charts_load,
            "expected": "charts_rendered"
        },
        {
            "name": "email_preview_display",
            "test": test_email_preview_display,
            "expected": "draft_email_shown"
        }
    ]
    
    results = []
    for case in edge_cases:
        try:
            result = case["test"]()
            results.append({
                "name": case["name"],
                "passed": result == case["expected"],
                "result": result
            })
        except Exception as e:
            results.append({
                "name": case["name"],
                "passed": False,
                "error": str(e)
            })
    
    return results
```

## References

1. [LangGraph Error Handling](https://langchain-ai.github.io/langgraph/how-tos/error-handling/)
2. [OpenAI Error Codes](https://platform.openai.com/docs/guides/error-codes)
3. [Redux State Management Best Practices](https://redux.js.org/tutorials/essentials/part-1-overview-concepts)
4. [SEBI Investment Advisor Guidelines](https://www.sebi.gov.in/legal/regulations)
