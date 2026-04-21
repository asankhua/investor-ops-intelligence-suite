# MCP Integration Architecture - Super-Agent Workflow (Pillar C)

## Overview

The MCP (Model Context Protocol) Integration powers Pillar C: Super-Agent Workflow. It consolidates all MCP actions into a single Human-in-the-Loop (HITL) Approval Center, handling Calendar Holds and Email Drafts with market context from Weekly Pulse.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PILLAR C ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  VOICE CALL COMPLETION                                  ││
│  │  • Booking code generated: MTG-2024-001                ││
│  │  • Call transcript saved                                ││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  MCP ACTION GENERATOR                                    ││
│  │  ┌─────────────────┐  ┌─────────────────────────────┐   ││
│  │  │ Calendar Hold   │  │ Email Draft to Advisor    │   ││
│  │  │ • Date/Time     │  │ • Customer context        │   ││
│  │  │ • Duration      │  │ • Booking code            │   ││
│  │  │ • Attendees     │  │ • Market context (M2)     │   ││
│  │  │                 │  │ • Suggested talking points│   ││
│  │  └─────────────────┘  └─────────────────────────────┘   ││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  HITL APPROVAL CENTER (Unified UI)                      ││
│  │  ┌─────────────────────────────────────────────────────┐ ││
│  │  │  Pending Actions Table                             │ ││
│  │  │  ┌─────────┬─────────────┬────────────┬───────────┐ │ ││
│  │  │  │ Action  │ Details     │ Mkt Context│ Approve?  │ │ ││
│  │  │  ├─────────┼─────────────┼────────────┼───────────┤ │ ││
│  │  │  │ Calendar│ MTG-2024-001│ "Login     │ [✓] [✗]  │ │ ││
│  │  │  │ Hold    │ [REDACTED]  │  issues..."│           │ ││
│  │  │  ├─────────┼─────────────┼────────────┼───────────┤ │ ││
│  │  │  │ Email   │ Draft ready │ Same       │ [✓] [✗]  │ │ ││
│  │  │  │ Draft   │             │ context    │           │ ││
│  │  │  └─────────┴─────────────┴────────────┴───────────┘ │ ││
│  │  └─────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  STATE PERSISTENCE                                     ││
│  │  • Booking code: MTG-2024-001 → Written to M2 notes     ││
│  │  • Cross-reference: Advisor can see pulse context       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Booking Flow Integration (Voice → MCP)

Complete booking sequence triggered from Voice Agent:

```
┌─────────────────────────────────────────────────────────────┐
│              BOOKING FLOW - MCP INTEGRATION                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. USER: "I want to book a call"                          │
│     ↓                                                       │
│  2. VOICE AGENT: "Morning or evening slot?"                │
│     ↓                                                       │
│  3. USER: "Morning"                                         │
│     ↓                                                       │
│  4. MCP: get_available_slots(date="today", slot="morning")  │
│     → Returns: ["10:00 AM", "11:00 AM", "11:30 AM"]        │
│     ↓                                                       │
│  5. VOICE AGENT: "Available: 10 AM, 11 AM, 11:30 AM"       │
│     ↓                                                       │
│  6. USER: "10 AM"                                           │
│     ↓                                                       │
│  7. MCP: book_calendar_slot(booking_code, datetime)         │
│     → Creates: Google Calendar event + Meet URL            │
│     ↓                                                       │
│  8. MCP: send_booking_email(booking_code, meet_url)         │
│     → Sends: Email to advisor with Meet link               │
│     ↓                                                       │
│  9. MCP: append_to_tracking_doc(booking_code, context)      │
│     → Appends: Booking info to Google Doc                │
│     ↓                                                       │
│  10. VOICE AGENT: "Booked! Code: MTG-2024-847             │
│      Meet: meet.google.com/..."                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### MCP Call Sequence

```python
async def execute_booking_mcp_calls(context: dict) -> dict:
    """Execute all MCP calls for booking flow."""
    
    # Step 1: Check available slots
    slots_result = await get_available_slots(
        date=context["date"],
        slot_preference=context["slot_preference"]
    )
    
    # Step 2: Book calendar with Meet
    booking_code = generate_booking_code()
    calendar_result = await book_calendar_slot(
        booking_code=booking_code,
        advisor_email="advisor@fintech.com",
        customer_email="customer@email.com",
        datetime=context["selected_datetime"],
        duration_minutes=30
    )
    
    # Step 3: Send confirmation email
    email_result = await send_booking_email(
        booking_code=booking_code,
        advisor_email="advisor@fintech.com",
        customer_email="customer@email.com",
        datetime=context["selected_datetime"],
        meet_url=calendar_result["meet_url"]
    )
    
    # Step 4: Append to tracking document
    doc_result = await append_to_tracking_doc(
        booking_code=booking_code,
        datetime=context["selected_datetime"],
        customer_context=context.get("customer_context", {}),
        pulse_context=context.get("weekly_pulse", {})
    )
    
    return {
        "booking_code": booking_code,
        "meet_url": calendar_result["meet_url"],
        "calendar_link": calendar_result["calendar_link"],
        "email_sent": email_result["success"],
        "doc_updated": doc_result["success"]
    }
```

### Post-Call MCP Action Sequence

When the voice call ends, the system automatically generates two MCP actions queued for HITL approval:

```
┌─────────────────────────────────────────────────────────────┐
│           POST-CALL ACTION SEQUENCE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VOICE CALL ENDS                                            │
│  └── Booking code generated: MTG-YYYY-XXX                   │
│      └── Transcript saved to state                          │
│                                                             │
│  ACTION 1: CALENDAR HOLD (Google Invite Draft)              │
│  ├── Creates Google Calendar event (DRAFT status)           │
│  ├── Generates Google Meet URL                              │
│  ├── Attendees: advisor@ + customer@                      │
│  └── Duration: 30 minutes                                   │
│                                                             │
│  ACTION 2: EMAIL DRAFT TO ADVISOR                           │
│  ├── To: advisor@fintech.com                                │
│  ├── Subject: Meeting Scheduled - {booking_code}            │
│  ├── Body includes:                                         │
│  │   ├── Booking Code: MTG-YYYY-XXX                         │
│  │   ├── Date/Time: {scheduled_datetime}                    │
│  │   ├── Google Meet: {meet_url}                            │
│  │   ├── Customer Context: [REDACTED]                       │
│  │   └── MARKET CONTEXT (from Weekly Pulse M2):              │
│  │       ├── Sentiment Score: {sentiment_score}              │
│  │       ├── Top Themes:                                    │
│  │       │   • {theme_1} ({confidence}%, {mentions} mentions)│
│  │       │   • {theme_2} ({confidence}%, {mentions} mentions)│
│  │       └── Suggested Talking Points:                      │
│  │           • Address {theme_1} proactively                  │
│  │           • Mention recent improvements                   │
│  └── Draft saved (NOT sent until approved)                  │
│                                                             │
│  BOTH ACTIONS QUEUED TO HITL APPROVAL CENTER                │
│  └── Advisor reviews and approves/rejects each             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Email Template with Market Context:**

```python
email_draft = {
    "to": "advisor@fintech.com",
    "subject": f"Meeting Scheduled - {booking_code}",
    "body": f"""
Dear Advisor,

You have a meeting scheduled with a customer.

**Booking Code:** {booking_code}
**Date & Time:** {datetime}
**Google Meet:** {meet_url}
**Customer:** [REDACTED - see CRM]

---
📊 MARKET CONTEXT (from Weekly Pulse - M2)
---

Customer Sentiment: {pulse.sentiment_score} ({sentiment_label})

Top Themes This Week:
1. {themes[0]['theme']} (Confidence: {themes[0]['confidence']}, {themes[0]['mentions']} mentions)
2. {themes[1]['theme']} (Confidence: {themes[1]['confidence']}, {themes[1]['mentions']} mentions)
3. {themes[2]['theme']} (Confidence: {themes[2]['confidence']}, {themes[2]['mentions']} mentions)

💡 Suggested Talking Points:
- Proactively address "{themes[0]['theme']}" if customer mentions it
- Reference recent improvements related to {themes[1]['theme']}
- Ask about general satisfaction to gauge sentiment

---

This meeting was booked via AI Voice Agent.
Please review and approve in the HITL Approval Center.

Best regards,
Investor Ops System
    """
}
```

**Key Points:**
- Calendar Hold = DRAFT calendar event (not sent until approved)
- Email = DRAFT in Gmail (not sent until approved)
- Market Context comes from `weekly_pulse` (Pillar B - M2)
- Booking Code links the call to M2 notes for cross-reference
- Both actions must be approved before execution

### ACTION 3: APPEND TO GOOGLE DOC (Tracking Document)

**Target Document:** Tracking Google Doc (configured via environment variable `GOOGLE_TRACKING_DOC_ID`)

When voice call ends, booking details are also appended to the tracking Google Doc:

```python
# Using Hugging Face MCP Server: https://huggingface.co/spaces/ashishsankhua/google-docs-gmail-mcp-server

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure MCP server connection
server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp.server.fastmcp"],
    env={"MCP_SERVER_URL": "https://huggingface.co/spaces/ashishsankhua/google-docs-gmail-mcp-server"}
)

async def append_to_tracking_doc(
    doc_id: str,
    booking_code: str,
    datetime: str,
    meet_url: str,
    pulse: WeeklyPulse,
    ctx: Context
) -> dict:
    """Append booking details to Google Doc tracking document via MCP server"""
    
    entry = f"""
## Booking: {booking_code}
- **Date/Time:** {datetime}
- **Customer:** [REDACTED]
- **Google Meet:** {meet_url}
- **Top Themes:** {', '.join([t['theme'] for t in pulse.top_themes])}
- **Sentiment:** {pulse.sentiment_score}
- **Status:** Pending Approval
- **Created:** {datetime.now().isoformat()}
---
"""
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Call the Google Docs append tool on Hugging Face MCP server
            result = await session.call_tool(
                "append_to_google_doc",
                {
                    "doc_id": doc_id,
                    "content": entry
                }
            )
            
            await ctx.info(f"Appended booking {booking_code} to tracking doc")
            return {"status": "appended", "booking_code": booking_code, "doc_id": doc_id}
```

**Purpose:**
- Central tracking log of all bookings
- Cross-reference with Weekly Pulse context
- Audit trail for compliance
- Historical record for analysis

**Note:** This action is typically auto-approved (doesn't require HITL) since it's just logging to an internal tracking doc.

## Key Design Patterns

### MCP Server with FastMCP

**MCP Server Source**: [https://huggingface.co/spaces/ashishsankhua/google-docs-gmail-mcp-server](https://huggingface.co/spaces/ashishsankhua/google-docs-gmail-mcp-server)

This Hugging Face Space provides the MCP server implementation for Google Docs and Gmail integration, handling:
- Google Calendar event creation
- Google Docs append operations (booking tracking)
- Gmail email drafting and sending

Use official `mcp.server.fastmcp` with `@mcp.tool()` decorator pattern:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("FintechScheduler", json_response=True)

@mcp.tool()
async def create_calendar_hold(
    booking_code: str,
    advisor_email: str,
    datetime: str,
    ctx: Context
) -> dict:
    """Create calendar hold for advisory meeting"""
    await ctx.info(f"Creating calendar hold for {booking_code}")
    return {"status": "pending_approval", "booking_code": booking_code}

@mcp.tool()
async def draft_advisor_email(
    booking_code: str,
    customer_context: str,
    market_context: str,  # From Weekly Pulse
    ctx: Context
) -> dict:
    """Draft email to advisor with market context"""
    await ctx.info(f"Drafting email for {booking_code}")
    return {"status": "pending_approval", "draft_id": f"DRAFT-{booking_code}"}

@mcp.tool()
async def get_available_slots(
    date: str,
    slot_preference: str,  # "morning", "afternoon", "evening"
    ctx: Context
) -> dict:
    """Query Google Calendar for available time slots."""
    await ctx.info(f"Checking availability for {date} {slot_preference}")
    
    # Query Google Calendar API for free/busy
    available_slots = [
        {"time": "10:00 AM", "duration": 30},
        {"time": "11:00 AM", "duration": 30},
        {"time": "11:30 AM", "duration": 30}
    ]
    
    return {
        "date": date,
        "slot_preference": slot_preference,
        "available_slots": available_slots,
        "timezone": "Asia/Kolkata"
    }

@mcp.tool()
async def book_calendar_slot(
    booking_code: str,
    advisor_email: str,
    customer_email: str,
    datetime: str,
    duration_minutes: int = 30,
    ctx: Context
) -> dict:
    """Book Google Calendar slot with Google Meet."""
    await ctx.info(f"Booking calendar slot for {booking_code}")
    await ctx.report_progress(0.3, message="Creating calendar event...")
    
    # Create Google Calendar event with Meet
    event_id = f"CAL-{booking_code}"
    meet_url = f"https://meet.google.com/{booking_code.lower().replace('-', '')}"
    
    await ctx.report_progress(0.6, message="Adding Google Meet...")
    
    # Add attendees
    await ctx.report_progress(0.9, message="Sending invites...")
    
    return {
        "status": "success",
        "event_id": event_id,
        "meet_url": meet_url,
        "calendar_link": f"https://calendar.google.com/calendar/event?eid={event_id}",
        "attendees": [advisor_email, customer_email],
        "booking_code": booking_code
    }

@mcp.tool()
async def send_booking_email(
    booking_code: str,
    advisor_email: str,
    customer_email: str,
    datetime: str,
    meet_url: str,
    ctx: Context
) -> dict:
    """Send confirmation email with booking details and Meet link."""
    await ctx.info(f"Sending booking email for {booking_code}")
    
    email_body = f"""
Subject: Meeting Confirmed - {booking_code}

Dear Advisor,

A meeting has been scheduled with a customer.

Booking Code: {booking_code}
Date & Time: {datetime}
Google Meet: {meet_url}

Please join the meeting using the above link.

Best regards,
Investor Ops System
"""
    
    # Send via Gmail API or SMTP
    message_id = f"EMAIL-{booking_code}"
    
    return {
        "status": "success",
        "message_id": message_id,
        "sent_to": [advisor_email, customer_email]
    }

@mcp.tool()
async def append_to_tracking_doc(
    booking_code: str,
    datetime: str,
    customer_context: dict,
    pulse_context: dict,
    ctx: Context
) -> dict:
    """Append booking details to Google Doc for tracking."""
    await ctx.info(f"Appending to tracking doc for {booking_code}")
    
    entry = f"""
## Booking: {booking_code}
- **Date/Time:** {datetime}
- **Customer:** [REDACTED]
- **Top Themes:** {', '.join([t['theme'] for t in pulse_context.get('top_themes', [])])}
- **Sentiment:** {pulse_context.get('sentiment', 'neutral')}
- **Status:** Confirmed
- **Created:** {datetime.now().isoformat()}
---
"""
    
    # Append to Google Doc
    return {
        "status": "success",
        "doc_id": "TRACKING-DOC-ID",
        "entry_appended": True
    }
```

### LangGraph Interrupt for HITL

Use `interrupt()` function to pause workflow for human approval:

```python
from langgraph.types import interrupt

def human_approval_node(state):
    """Interrupt returns user response from frontend UI."""
    result = interrupt({
        "action": "calendar_hold",
        "booking_code": state["booking_code"],
        "details": state["action_details"],
        "market_context": state["weekly_pulse_summary"],
        "requires_approval": True
    })
    return {"approved": result["decision"] == "approve"}
```

### Unified Approval Queue

Single table UI showing all pending MCP actions with approve/reject buttons. See [wireframe.md](wireframe.md) Section 5 for implementation.

### Context Enrichment

Email drafts include Weekly Pulse market context via template injection:

```python
email_template = """
Subject: Upcoming Meeting - {booking_code}

Dear Advisor,

You have a meeting scheduled with a customer.

**Booking Code:** {booking_code}
**Customer:** [REDACTED]

**Market Context:**
{market_context}

**Current Themes:**
{% for theme in top_themes %}
- {{ theme.theme }} (Confidence: {{ theme.confidence }})
{% endfor %}

**Suggested Talking Points:**
{% for point in talking_points %}
- {{ point }}
{% endfor %}

Best regards,
Investor Ops System
"""
```

### State Cross-Referencing

Booking codes appear in both M2 notes and M3 output (stored in shared state):

```python
def cross_reference_booking(booking_code: str, pulse_context: dict, state_storage: dict):
    """Store booking reference across pillars."""
    # Add to M2 notes
    state_storage['weekly_pulse']['booking_refs'].append({
        'code': booking_code,
        'context': pulse_context
    })
    
    # Add to M3 active bookings
    state_storage['active_bookings'].append(booking_code)
    
    # Create mapping
    state_storage['booking_to_pulse_map'][booking_code] = pulse_context
    
    return state_storage
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **MCP Framework** | FastMCP (official python-sdk v1.x) | Native Python decorator support, structured output, Context injection |
| **Workflow Engine** | LangGraph (v0.2+) | State machines, interrupts for HITL, durable execution |
| **Calendar** | Google Calendar API / ICS generation | Standard, widely supported |
| **Email Drafts** | Template-based (Jinja2) | Flexible, no SMTP needed for drafts |
| **Approval UI** | React / Vanilla JS / HTML / CSS | Production-grade UI for HITL approval workflows |

## Implementation

### MCP Server Definition

```python
# src/pillar_c/mcp_servers/calendar_server.py
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel

class CalendarHoldRequest(BaseModel):
    booking_code: str
    advisor_email: str
    datetime: str
    duration_minutes: int = 30

mcp = FastMCP("CalendarServer")

@mcp.tool()
async def create_hold(request: CalendarHoldRequest, ctx: Context) -> dict:
    """Create a calendar hold pending approval."""
    await ctx.info(f"Creating hold for {request.booking_code}")
    
    # Generate ICS file or Google Calendar hold
    hold_id = f"HOLD-{request.booking_code}"
    
    return {
        "status": "pending_approval",
        "hold_id": hold_id,
        "booking_code": request.booking_code,
        "requires_approval": True
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### LangGraph Workflow with HITL

```python
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from typing import TypedDict

class MCPState(TypedDict):
    booking_code: str
    action_type: str  # "calendar" or "email"
    action_details: dict
    approved: bool
    iterations: int

def create_mcp_workflow():
    """Create HITL workflow for MCP actions."""
    builder = StateGraph(MCPState)
    
    # Nodes
    builder.add_node("generate_action", generate_action)
    builder.add_node("human_approval", human_approval)
    builder.add_node("execute_action", execute_action)
    
    # Edges
    builder.set_entry_point("generate_action")
    builder.add_edge("generate_action", "human_approval")
    builder.add_conditional_edges(
        "human_approval",
        lambda state: "execute" if state["approved"] else END
    )
    builder.add_edge("execute_action", END)
    
    return builder.compile()

def generate_action(state: MCPState):
    """Generate calendar hold and email draft."""
    return {
        "booking_code": generate_booking_code(),
        "action_details": {
            "calendar": create_calendar_hold(),
            "email": create_email_draft()
        }
    }

def human_approval(state: MCPState):
    """Pause for human approval via interrupt."""
    result = interrupt({
        "booking_code": state["booking_code"],
        "actions": state["action_details"],
        "market_context": get_weekly_pulse_summary()
    })
    return {"approved": result["decision"] == "approve"}

def execute_action(state: MCPState):
    """Execute approved actions."""
    if state["approved"]:
        # Execute calendar hold
        # Send email draft
        pass
    return state
```

### HITL Approval UI

📄 **Wireframes & Frontend Implementation**: See [wireframe.md](wireframe.md) Section 5: HITL Approval Center for complete wireframe layouts and frontend implementations (React, Vanilla JS, HTML/CSS).

**UI Features**:
- Display pending MCP actions (Calendar holds, Email drafts)
- Approve/Reject individual or batch actions
- View action details and context
- **Preview Draft Email**: Full email preview panel on right side
- Track Google Doc status in tracking URL
- Show Weekly Pulse context for email drafts

**Email Preview API** (supports `wireframe.md` HITL - Preview Draft Email):

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/hitl/email/preview/{booking_code}` | GET | Get email draft preview | - | `{to, from, subject, body, context}` |
| `/api/hitl/email/send/{booking_code}` | POST | Send approved email | `{approved: true}` | `{status: "sent", message_id}` |
| `/api/hitl/email/edit/{booking_code}` | PUT | Edit email draft | `{subject, body}` | `{updated_draft}` |
| `/api/hitl/pending` | GET | List all pending HITL actions | - | `[{id, type, booking_code, details}]` |
| `/api/hitl/approve/{action_id}` | POST | Approve specific action | `{approve: true}` | `{status: "approved"}` |
| `/api/hitl/reject/{action_id}` | POST | Reject specific action | `{reason}` | `{status: "rejected"}` |

**Example - Preview Email Draft**:
```python
GET /api/hitl/email/preview/MTG-2024-001
Response: {
  "to": "advisor@example.com",
  "from": "noreply@investorsuite.com",
  "subject": "Meeting Booking Confirmation - MTG-2024-001",
  "body": "Dear Advisor,\n\nA meeting has been booked for Jan 16 at 10:30 AM.\n\nBooking Code: MTG-2024-001\nMeet Link: https://meet.google.com/abc-defg-hij\n\nContext: Login Theme\n\nBest regards,\nInvestor Intelligence Suite",
  "context": "Login Issues theme detected in Weekly Pulse",
  "tracking_doc": "<configured_tracking_doc_url>"
}
```

- Poll for updates every 5 seconds
- Handle empty state when no pending actions

## Session State (Frontend - LocalStorage/Redux)

```javascript
// Initialize state
const initState = () => {
  const defaultState = {
    active_bookings: [],
    pending_mcp_actions: [],
    booking_to_pulse_map: {}
  };
  
  localStorage.setItem('mcp_state', JSON.stringify(defaultState));
};

// Get state
const getState = () => {
  return JSON.parse(localStorage.getItem('mcp_state') || '{}');
};

// Update state
const updateState = (updates) => {
  const current = getState();
  const newState = { ...current, ...updates };
  localStorage.setItem('mcp_state', JSON.stringify(newState));
  return newState;
};

// React Hook version
const useMCPState = () => {
  const [state, setState] = useState(() => getState());
  
  const update = (updates) => {
    const newState = updateState(updates);
    setState(newState);
  };
  
  return [state, update];
};
```

## API Specification

```python
class MCPWorkflowAPI:
    def create_booking(self, context: CallContext) -> BookingResult:
        """Creates booking and adds to HITL queue.
        Returns booking code for cross-reference.
        """
    
    def approve_action(self, action_id: str) -> ExecutionResult:
        """Human approves pending MCP action."""
    
    def get_pending_actions(self) -> List[PendingAction]:
        """Retrieve all actions awaiting approval."""

class BookingResult:
    booking_code: str
    calendar_hold_id: str
    email_draft_id: str
    status: str  # pending_approval

class PendingAction:
    id: str
    type: str  # "calendar" | "email"
    booking_code: str
    details: dict
    market_context: str
```

## Project Structure

```
src/pillar_c/
├── __init__.py
├── mcp_servers/
│   ├── calendar_server.py
│   └── email_server.py
├── workflow.py           # HITL workflow orchestrator
├── action_queue.py       # Pending actions manager
└── context_enricher.py   # Market context injector
```

## Dependencies

```txt
# MCP (Model Context Protocol)
mcp>=1.0.0

# Workflow
langgraph>=0.2.0

# Templates
jinja2>=3.1.0

# Calendar/Email integrations
google-api-python-client>=2.0.0
```

## MCP Server Deployment

```bash
# Run calendar MCP server
uv run --with mcp src/pillar_c/mcp_servers/calendar_server.py

# Run email MCP server
uv run --with mcp src/pillar_c/mcp_servers/email_server.py

# Or with stdio transport for Claude Desktop integration
python src/pillar_c/mcp_servers/calendar_server.py
```

## Evaluation Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| **Booking code visibility** | 100% | Code appears in M2 notes |
| **Market context inclusion** | 100% | Email drafts include Weekly Pulse |
| **Approval latency** | < 5 min | Time from call end to human decision |

## References

1. [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
2. [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
3. [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp)
