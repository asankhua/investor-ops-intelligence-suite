# Safety & Compliance Rules

## Overview

This document defines the safety, compliance, and guardrail rules for the Investor Ops & Intelligence Suite. These rules ensure fintech compliance, data privacy, and ethical AI usage.

## PII Handling

### Detection Flow

```
Input → PII Detector → [REDACTED] Replacement → LLM → Output Filter
         │                                    │
         ▼                                    ▼
   Regex Patterns:                      Output Validation:
   • Email: \S+@\S+\.\S+               • Re-check for leaked PII
   • Phone: \d{10,12}                  • Log detection events
   • Name: NER tagging                 • Alert if bypass detected
   • Aadhar/PAN: Custom patterns       • Mask in logs
```

### PII Patterns

| Data Type | Pattern | Replacement |
|-----------|---------|-------------|
| **Email** | `\S+@\S+\.\S+` | `[REDACTED_EMAIL]` |
| **Phone** | `\d{10,12}` | `[REDACTED_PHONE]` |
| **Name** | NER `PERSON` tag | `[REDACTED_NAME]` |
| **Aadhar** | `\d{4}[ -]?\d{4}[ -]?\d{4}` | `[REDACTED_AADHAR]` |
| **PAN** | `[A-Z]{5}[0-9]{4}[A-Z]` | `[REDACTED_PAN]` |
| **Account Number** | `\d{9,18}` | `[REDACTED_ACCT]` |

### Implementation

```python
import re
from typing import List, Tuple

class PIIMasker:
    PATTERNS = {
        'email': (r'\S+@\S+\.\S+', '[REDACTED_EMAIL]'),
        'phone': (r'\b\d{10,12}\b', '[REDACTED_PHONE]'),
        'aadhar': (r'\d{4}[ -]?\d{4}[ -]?\d{4}', '[REDACTED_AADHAR]'),
        'pan': (r'[A-Z]{5}[0-9]{4}[A-Z]', '[REDACTED_PAN]'),
    }
    
    def mask(self, text: str) -> Tuple[str, List[str]]:
        """Mask PII and return detected types."""
        detected = []
        masked_text = text
        
        for pii_type, (pattern, replacement) in self.PATTERNS.items():
            if re.search(pattern, text):
                detected.append(pii_type)
                masked_text = re.sub(pattern, replacement, masked_text)
        
        return masked_text, detected
    
    def check_output(self, text: str) -> bool:
        """Verify output doesn't contain unmasked PII."""
        for pattern, _ in self.PATTERNS.values():
            if re.search(pattern, text):
                return False
        return True
```

## Guardrails Layer

| Guardrail | Implementation | Trigger | Action |
|-----------|----------------|---------|--------|
| **Investment Advice Block** | Keyword filter + LLM judge | "best fund", "guaranteed returns", "should I invest", "will give X%" | Refuse + explain limitation |
| **PII Redaction** | Regex + NER | Any detected PII pattern | Mask before LLM, verify after |
| **Source Citation Enforcer** | Output parser | All Pillar A responses | Ensure [Source: M1/M2] present |
| **6-Bullet Constraint** | Prompt + post-processor | All Pillar A responses | Truncate or request regeneration |
| **Tone Compliance** | Sentiment classifier | Voice agent greetings | Ensure professional, helpful tone |
| **Adversarial Prompt Detection** | Pattern matching + LLM | "ignore previous", "disregard rules", "DAN mode" | Block + log attempt |

### Investment Advice Blocker

```python
INVESTMENT_KEYWORDS = [
    "best fund", "guaranteed returns", "should I invest",
    "will give", "% returns", "predict", "recommend",
    "top performing", "buy this", "sell that"
]

def check_investment_advice(text: str) -> Tuple[bool, str]:
    """Check if query requests investment advice."""
    # Keyword check
    for keyword in INVESTMENT_KEYWORDS:
        if keyword.lower() in text.lower():
            return True, "investment_keywords"
    
    # LLM judge for nuanced cases
    judge_prompt = f"""
    Does this query ask for investment advice or predictions?
    Query: {text}
    Answer YES if it asks which fund to buy, predictions, or recommendations.
    Answer NO if it asks about fees, rules, or factual information.
    """
    
    response = llm.invoke(judge_prompt)
    is_advice = "YES" in response.content.upper()
    
    return is_advice, "llm_judge"

def get_refusal_message(reason: str) -> str:
    """Return compliant refusal message."""
    return """
    I cannot provide investment advice or predict fund performance. 
    I can help you understand fees, exit loads, and fund rules based on our documentation.
    For personalized investment advice, please consult with a registered financial advisor.
    """
```

### Source Citation Enforcer

```python
class CitationEnforcer:
    REQUIRED_TAG = "[Source:"
    VALID_SOURCES = ["M1", "M2"]
    
    def validate(self, response: dict) -> Tuple[bool, List[str]]:
        """Validate citations in response."""
        bullets = response.get("bullets", [])
        citations = response.get("citations", [])
        errors = []
        
        # Check each bullet has citation
        for i, bullet in enumerate(bullets):
            has_citation = any(c["bullet_index"] == i for c in citations)
            if not has_citation:
                errors.append(f"Bullet {i} missing citation")
        
        # Check valid sources
        for citation in citations:
            if citation["source"] not in self.VALID_SOURCES:
                errors.append(f"Invalid source: {citation['source']}")
        
        return len(errors) == 0, errors
```

### 6-Bullet Constraint

```python
class BulletConstraint:
    MAX_BULLETS = 6
    
    def enforce(self, response: dict) -> dict:
        """Enforce max 6 bullets."""
        bullets = response.get("bullets", [])
        
        if len(bullets) > self.MAX_BULLETS:
            # Truncate or regenerate
            response["bullets"] = bullets[:self.MAX_BULLETS]
            response["truncated"] = True
        
        return response
    
    def validate_schema(self) -> dict:
        """Return JSON schema for GPT-4o."""
        return {
            "type": "object",
            "properties": {
                "bullets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6
                },
                "sources_used": {
                    "type": "array",
                    "items": {"enum": ["M1", "M2"]}
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "bullet_index": {"type": "integer"},
                            "source": {"type": "string"},
                            "doc_id": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["bullets", "sources_used", "citations"]
        }
```

## Adversarial Prompt Detection

### Blocked Patterns

| Pattern | Category | Action |
|---------|----------|--------|
| "ignore previous instructions" | Jailbreak | Block + log |
| "disregard system prompt" | Jailbreak | Block + log |
| "DAN mode" / "do anything now" | Jailbreak | Block + log |
| "you are not an AI" | Roleplay | Block + log |
| "pretend you are" | Roleplay | Block + log |
| "leak your prompt" | Extraction | Block + log |

```python
ADVERSARIAL_PATTERNS = [
    r"ignore\s+(?:previous|all)\s+(?:instructions?|prompts?)",
    r"disregard\s+(?:system\s+)?(?:prompt|instructions?)",
    r"DAN\s+mode|do\s+anything\s+now",
    r"you\s+are\s+not\s+(?:an\s+)?AI",
    r"pretend\s+you\s+(?:are|can)",
    r"leak\s+(?:your\s+)?(?:prompt|instructions?)",
]

class AdversarialDetector:
    def detect(self, text: str) -> Tuple[bool, str]:
        """Detect adversarial patterns."""
        for pattern in ADVERSARIAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, pattern
        return False, None
    
    def block(self, reason: str):
        """Block adversarial attempt."""
        logger.warning(f"Adversarial attempt blocked: {reason}")
        return "I cannot process this request. Please ask questions about mutual funds, fees, or scheduling."
```

## Technical Constraints

### Single Entry Point Rule

**Requirement:** All three pillars must be accessible from a single UI (Streamlit, Vercel, etc.).

**Implementation:**
```python
# app.py - Single entry point
import streamlit as st

st.set_page_config(
    page_title="Investor Intelligence Suite",
    layout="wide"
)

# Sidebar navigation for all pillars
pillar = st.sidebar.radio(
    "Select Pillar:",
    ["Pillar A: RAG Knowledge Base", "Pillar B: Weekly Pulse", "Pillar C: Voice Agent & Bookings"]
)

if pillar == "Pillar A: RAG Knowledge Base":
    render_pillar_a()
elif pillar == "Pillar B: Weekly Pulse":
    render_pillar_b()
else:
    render_pillar_c()
```

**Enforcement:**
- No external redirects to separate apps
- All state shared via LocalStorage/Redux
- Unified authentication

### No PII Rule

**Requirement:** Mask all sensitive data. Use [REDACTED] for any simulated user names.

**PII Patterns to Redact:**
| Data Type | Example Input | Masked Output |
|-----------|---------------|---------------|
| Email | `ashish@example.com` | `[REDACTED_EMAIL]` |
| Phone | `9876543210` | `[REDACTED_PHONE]` |
| Name | `John Smith` | `[REDACTED_NAME]` |
| Aadhar | `1234 5678 9012` | `[REDACTED_AADHAR]` |
| PAN | `ABCDE1234F` | `[REDACTED_PAN]` |
| Account | `123456789012` | `[REDACTED_ACCT]` |

**Implementation:**
```python
class PIIRule:
    def enforce(self, text: str) -> str:
        """Enforce PII masking."""
        masked, detected = PIIMasker().mask(text)
        
        # Post-validation
        if not PIIMasker().check_output(masked):
            raise PIIViolation("PII detected in output")
        
        return masked
```

### State Persistence Rule

**Requirement:** The Booking Code (M3) must be visible in the Notes/Doc (M2) to show systems are connected.

**Implementation:**
```python
class StatePersistenceRule:
    """Enforce cross-pillar state persistence."""
    
    REQUIRED_SYNCS = {
        "booking_code": {
            "source": "pillar_c",
            "targets": ["pillar_b_notes", "tracking_doc"],
            "timeout_seconds": 30
        }
    }
    
    def validate_sync(self, booking_code: str) -> bool:
        """Validate booking code appears in all required locations."""
        
        # Check M2 notes
        m2_notes = get_m2_notes()
        in_m2 = any(n.get("booking_code") == booking_code for n in m2_notes)
        
        # Check tracking doc
        doc_entries = get_tracking_doc_entries()
        in_doc = any(e.get("booking_code") == booking_code for e in doc_entries)
        
        return in_m2 and in_doc
    
    def enforce(self, booking_code: str):
        """Enforce state persistence."""
        if not self.validate_sync(booking_code):
            raise StateSyncViolation(
                f"Booking code {booking_code} not found in M2 notes or tracking doc"
            )
```

## Compliance Rules

### Fintech-Specific Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| **No Performance Claims** | Cannot state "X% returns" | Block + redirect to factual info |
| **No Fund Recommendations** | Cannot say "buy fund Y" | Block + suggest consulting advisor |
| **Fee Transparency** | Must cite exact fee structures | Source from M2 only |
| **Risk Disclosure** | Must mention risks when discussing investments | Auto-append risk disclaimer |
| **Advisor Referral** | Must suggest human advisor for complex queries | Include in refusal messages |

### Risk Disclaimer

```python
RISK_DISCLAIMER = """
**Disclaimer:** Mutual fund investments are subject to market risks. 
Past performance does not guarantee future returns. 
Please read all scheme-related documents carefully before investing.
For personalized advice, consult a SEBI-registered investment advisor.
"""

def append_disclaimer(response: str, context: str) -> str:
    """Append risk disclaimer to investment-related responses."""
    if any(word in context.lower() for word in ["invest", "fund", "return"]):
        return response + "\n\n" + RISK_DISCLAIMER
    return response
```

## Environment Configuration

```bash
# Safety Settings
GUARDRAILS_ENABLED=true
PII_MASKING_MODE=strict  # strict|permissive|disabled
ADVERSARIAL_DETECTION=true
INVESTMENT_ADVICE_BLOCK=true
LOG_SAFETY_EVENTS=true

# Technical Constraints
SINGLE_ENTRY_POINT=true
PII_REDACTION_ENABLED=true
STATE_PERSISTENCE_CHECK=true
BOOKING_CODE_VISIBILITY_REQUIRED=true

# Refusal Message Customization
REFUSAL_INVESTMENT_ADVICE="I cannot provide investment advice. Please consult a registered advisor."
REFUSAL_PII_REQUEST="I cannot share personal information."
```

## Project Structure

```
src/shared/
├── pii_masker.py         # PII detection/redaction
├── guardrails.py         # Safety filters
└── logger.py             # Structured logging for safety events
```

## Dependencies

```txt
# Safety & Compliance
presidio-analyzer>=2.2.0  # Alternative PII detection
presidio-anonymizer>=2.2.0
spacy>=3.7.0  # For NER

# Logging
structlog>=24.1.0
```

---

## UI/UX Layout Rules

**Visual Design** (supports `wireframe.md` design system):

### Colors
| Role | Color Code | Usage |
|------|------------|-------|
| Background | `#E8F4FC` | Light Blue - all page backgrounds |
| Cards | `#FFFFFF` | White - content panels |
| Headers/CTAs | `#1E3A5F` | Navy Blue - primary actions |
| Accents | `#5DADE2` | Sky Blue - highlights, badges |

### Layout Patterns
| Page | Layout | Columns |
|------|--------|---------|
| **Dashboard/Home** | Sidebar + Main Content | 1 (full width) |
| **Pillar A (RAG)** | 3-column | Fund List (left) + Chat (center) + Sources (right) |
| **Pillar B (Pulse)** | 2-column | Content (left 70%) + Analytics (right 30%) |
| **Pillar C (Voice)** | 3-column | Recording (left) + Chatbot (center) + Booking (right) |
| **HITL** | 2-column | Actions (left 60%) + Preview (right 40%) |

### Sidebar Navigation
```
🏠 H = Home (Dashboard Overview)
📊 A = Pillar A (RAG Knowledge Base)
📈 B = Pillar B (Weekly Pulse)
🎙️ C = Pillar C (Voice Agent)
⚙️ H = HITL (Approval Center)
📊 E = Evals (Testing Suite)
[2] ⚡ = Pending Approvals (badge count)
```

### Component Guidelines
- **Cards**: White background, subtle shadow, 8px border-radius
- **Buttons**: Navy (#1E3A5F) for primary, Sky Blue (#5DADE2) for secondary
- **Sidebar**: Compact 60px width, icon-only with hover tooltips
- **Pipeline Status**: Top-center, 7 steps (VAD›STT›LLM›TTS›Calendar›Doc›Email)
- **Quick Use Tips**: Bottom of each section, 3-4 actionable tips

### Responsive Behavior
- **Desktop (>1024px)**: Full multi-column layouts
- **Tablet (768-1024px)**: Collapse to 2-column where applicable
- **Mobile (<768px)**: Single column, stacked sections

## References

1. [Presidio PII Detection](https://microsoft.github.io/presidio/)
2. [SEBI Investment Advisor Regulations](https://www.sebi.gov.in/legal/regulations)
3. [LLM Guardrails Best Practices](https://www.fiddler.ai/articles/ai-guardrails-metrics)
