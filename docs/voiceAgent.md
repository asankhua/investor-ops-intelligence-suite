# Voice Agent Architecture

## Overview

The Voice Agent powers the AI Voice Scheduler (M3), integrating with Pillar B's theme analysis to provide contextual, theme-aware greetings. It handles voice input (STT), generates responses, and produces voice output (TTS).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VOICE AGENT FLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  THEME-AWARE GREETING                                   ││
│  │  ┌──────────────┐  ┌──────────────────────────────────┐││
│  │  │  Theme Store │  │  Dynamic Greeting Generator        │││
│  │  │  (M2 Pulse)  │  │  "I see users asking about..."    │││
│  │  └──────────────┘  └──────────────────────────────────┘││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  VOICE PIPELINE                                         ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ││
│  │  │  VAD         │  │  Speech-to-  │  │  Text-to-    │  ││
│  │  │  (Silero)    │  │  Text        │  │  Speech      │  ││
│  │  │              │  │  (Sarvam)    │  │  (Sarvam)    │  ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  ││
│  │                          │                                  │
│  │                          ▼                                  │
│  │  ┌─────────────────────────────────────────────────────────┐│
│  │  │  INTENT PROCESSING (GPT-4o)                             ││
│  │  │  • Entity extraction (datetime, advisor)              ││
│  │  │  • Classification (book_call, reschedule, cancel)      ││
│  │  └─────────────────────────────────────────────────────────┘│
│  └─────────────────────────────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  SCHEDULING LOGIC                                       ││
│  │  • Extract datetime from voice input                    ││
│  │  • Validate availability                                ││
│  │  • Generate booking code (MTG-YYYY-XXX)                 ││
│  │  • Trigger MCP actions post-call                      ││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  CALL COMPLETION                                        ││
│  │  • Save transcript to backend state                     ││
│  │  • Queue Calendar Hold + Email Draft (MCP)            ││
│  │  • Cross-reference booking code to M2 notes           ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## User Interaction Flow

The Voice Agent UI supports both voice and text input modes. Users can toggle between 🎙️ Voice Mode and ⌨️ Text Mode in the Conversation Chatbot.

```
┌─────────────────────────────────────────────────────────────┐
│              USER INTERACTION SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT MODE: 🎙️ VOICE or ⌨️ TEXT (Toggle Available)         │
│                                                             │
│  STEP 1: INPUT (Voice Mode)                                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  [🎤 Hold to Record]                                  │ │
│  │  User presses and holds mic button, speaks          │ │
│  │  "I want to book a meeting tomorrow at 3 PM"         │ │
│  │  Releases button when done                            │ │
│  │  🎤 STT → "I want to book a meeting tomorrow at 3 PM"│ │
│  └────────────────────────┬──────────────────────────────┘ │
│                          │                                  │
│     OR TEXT MODE:          │                                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  [⌨️ Type Message...]                                 │ │
│  │  User types: "I want to book a meeting tomorrow"     │ │
│  │  [➤ Send]                                            │ │
│  └────────────────────────┬──────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  STEP 2: PROCESS (Background)                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  1. Silero VAD filters audio (if voice)           │ │
│  │  2. Sarvam STT converts to text (if voice)        │ │
│  │  3. GPT-4o processes intent                         │ │
│  │  4. Generate response text                          │ │
│  │  5. Sarvam TTS creates audio                        │ │
│  └────────────────────────┬──────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  STEP 3: DISPLAY IN CONVERSATION CHATBOT                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  💬 Conversation Chatbot                              │ │
│  │   [🎙️ Voice Mode]  [⌨️ Text Mode]                    │ │
│  │                                                      │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ 👤 User Input (Voice or Text)                 │  │ │
│  │  │ "I want to book a meeting tomorrow at 3 PM"   │  │ │
│  │  │ 🎤 STT → [transcribed text]                  │  │ │
│  │  │ [▶️ Play Voice] [📄 Transcript]               │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                          │                           │ │
│  │                          ▼                           │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ 🤖 Agent (Text Output + TTS)                │  │ │
│  │  │ "I've scheduled your meeting for tomorrow   │  │ │
│  │  │  at 3:00 PM. Your booking code is            │  │ │
│  │  │  MTG-2024-001."                              │  │ │
│  │  │ [▶️ Play Voice] � TTS                        │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                                                      │ │
│  │  💬 Type your message...   [🎤] [➤]                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                             │
│  │  • Continue conversation                              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### UI Components

📄 **Wireframes & Frontend Implementation**: See [wireframe.md](wireframe.md) for complete wireframe layouts and frontend implementations:
- Section 4: Pillar C - Voice Agent & Booking UI
- Section 6: Pipeline Status UI

**Key Components:**
- Voice recording interface (Hold-to-speak button)
- Chat display area (User/Agent messages with voice playback)
- Pipeline status (VAD › STT › LLM › TTS › Calendar › Doc › Email)
- Booking confirmation card

#### Voice Recording Interface

### User Interaction Flow

The UI supports **voice input (STT)** and **text input** modes for flexibility:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎙️ Voice Input Mode    │  ⌨️ Text Input Mode                       │
├─────────────────────────────────────────────────────────────────────┤
│  User holds 🎤 button       │  User types in 💬 text input             │
│  ↓                          │  ↓                                       │
│  Silero VAD detects speech  │  User clicks ➤ or presses Enter         │
│  ↓                          │  ↓                                       │
│  Sarvam STT (saarika-v2)    │  Text sent directly to LLM              │
│  English (Indian accent)    │  No STT processing                       │
│  ↓                          │  ↓                                       │
│  Text → LLM processing      │  LLM generates response                  │
│  ↓                          │  ↓                                       │
│  Agent response             │  Agent response shown                    │
│  ↓                          │  [▶️ Play Voice] button available       │
│  Sarvam TTS (meera voice)   │  🔊 Optional TTS playback               │
│  English (Indian accent)    │                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Voice Recording API

**Endpoints** (supports `wireframe.md` Pillar C - Voice Recording Interface):

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/pillar-c/voice/record/start` | POST | Start voice recording | `{session_id}` | `{recording_id, stream_url}` |
| `/api/pillar-c/voice/record/stop` | POST | Stop recording, get audio | `{recording_id}` | `{audio_url, duration}` |
| `/api/pillar-c/voice/record/cancel` | POST | Cancel recording | `{recording_id}` | `{status: "cancelled"}` |
| `/api/pillar-c/voice/play` | GET | Play recorded audio | `{audio_url}` | Audio stream |
| `/api/pillar-c/tts/play` | POST | Play TTS audio | `{text, voice}` | Audio stream |
| `/api/pillar-c/pipeline/status` | GET | Get pipeline step status | - | `{current_step, steps, status}` |

**Pipeline Status Steps**:
```python
steps = [
    {"id": "VAD", "name": "Voice Activity Detection", "status": "idle|active|done"},
    {"id": "STT", "name": "Speech-to-Text", "status": "idle|active|done"},
    {"id": "LLM", "name": "LLM Processing", "status": "idle|active|done"},
    {"id": "TTS", "name": "Text-to-Speech", "status": "idle|active|done"},
    {"id": "Calendar", "name": "Calendar Booking", "status": "idle|active|done"},
    {"id": "Doc", "name": "Document Logging", "status": "idle|active|done"},
    {"id": "Email", "name": "Email Notification", "status": "idle|active|done"}
]
```

**Example - Start Recording**:
```python
POST /api/pillar-c/voice/record/start
Request: {"session_id": "sess-123"}
Response: {
  "recording_id": "rec-456",
  "stream_url": "wss://api.investorsuite.com/voice/stream/rec-456",
  "status": "recording"
}
```

📄 **Implementation**: See [wireframe.md](wireframe.md) Section 6: Pipeline Status UI for complete React and Vanilla JS implementations.

#### Pipeline Status UI (Real-time Progress)

Visual pipeline showing 7 processing steps with color-coded status:

```
┌─────────────────────────────────────────────────────────────┐
│  PIPELINE STATUS                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VAD › STT › LLM › TTS › Calendar › Doc › Email          │
│   ●     ●     ●    ●      ●        ●      ●                │
│  gray  amber amber amber green   green  green              │
│ (idle)(active)(done)(done)(done) (done) (done)            │
│                                                             │
│  Legend:                                                    │
│  ● Gray  = Idle / Waiting                                   │
│  ● Amber = Active / Processing                              │
│  ● Green = Done Successfully                                │
│  ● Red   = Error / Failed                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

📄 **Implementation**: See [wireframe.md](wireframe.md) Section 6: Pipeline Status UI for complete React and Vanilla JS implementations.

#### Processing Pipeline

```python
def process_voice_input(audio_bytes: bytes) -> dict:
    """Process voice input through the complete pipeline."""
    
    # 1. VAD (Silero)
    vad_audio = apply_vad(audio_bytes)
    
    # 2. STT (Sarvam)
    transcript = sarvam_stt(vad_audio)
    
    # 3. Intent Processing (GPT-4o)
    intent = process_intent(transcript)
    
    # 4. Generate Response
    response_text = generate_response(intent)
    
    # 5. TTS (Sarvam)
    response_audio = sarvam_tts(response_text)
    
    return {
        "transcript": transcript,
        "response_text": response_text,
        "response_audio": response_audio,
        "intent": intent
    }
```

### Chat History Structure

```javascript
// LocalStorage or Redux State Structure
const appState = {
    "chat_history": [
        {
            "role": "user",           // "user" or "agent"
            "text": "User transcript", // STT output
            "audio": Blob,            // Original voice recording
            "timestamp": "2024-01-15T10:30:00"
        },
        {
            "role": "agent",
            "text": "Agent response",
            "audio": Blob,            // TTS generated audio
            "timestamp": "2024-01-15T10:30:05"
        }
    ],
    "voice_settings": {
        "stt_model": "saarika-v2",
        "tts_voice": "meera",
        "language": "en-IN"
    },
    "pipeline_status": {
        "VAD": "idle",
        "STT": "idle",
        "LLM": "idle",
        "TTS": "idle",
        "Calendar": "idle",
        "Doc": "idle",
        "Email": "idle"
    }
};
```

## Key Features

### Theme-Aware Greetings

```python
def generate_greeting() -> str:
    """Generate dynamic greeting based on Weekly Pulse themes."""
    pulse = appState.get('weekly_pulse', {})
    top_themes = pulse.get('top_themes', [])
    
    if top_themes and top_themes[0]['confidence'] >= 0.7:
        theme = top_themes[0]['theme']
        return f"Hello! I see many users are asking about {theme} today. I can help you book a call for that!"
    
    return "Hello! How can I help you schedule a meeting today?"
```

### Voice Pipeline

| Stage | Technology | Purpose |
|-------|------------|---------|
| **VAD** | Silero VAD | Detect voice activity, segment audio |
| **STT** | Sarvam API | Speech-to-text (English - Indian Accent) |
| **Processing** | GPT-4o | Intent classification, entity extraction |
| **TTS** | Sarvam API | Text-to-speech (English - Indian Accent) |

### Why Sarvam + Silero for Indian English?

| Feature | Sarvam API | Silero VAD |
|---------|------------|------------|
| **Language** | English (Indian Accent) | Language-agnostic |
| **Accents** | Trained on diverse Indian regional accents | - |
| **Cost** | Competitive pricing vs OpenAI Whisper | Free, open-source |
| **VAD** | Not included | Detects speech segments, filters noise |
| **Local Deployment** | Cloud API | Runs locally (PyTorch) |
| **Privacy** | Enterprise-grade | On-premise possible |
| **Use Case** | Indian fintech customers | Pre-processing audio |

### Scheduling Logic

```python
class SchedulingLogic:
    def extract_datetime(self, transcript: str) -> Optional[datetime]:
        """Extract proposed meeting time from voice transcript."""
        # Use GPT-4o with function calling
        response = self.llm.invoke(
            "Extract datetime from: " + transcript,
            tools=[extract_datetime_tool]
        )
        return response.get('datetime')
    
    def validate_availability(self, datetime: datetime) -> bool:
        """Check if slot is available."""
        # Check against advisor calendar
        pass
    
    def generate_booking_code(self) -> str:
        """Generate unique booking code: MTG-YYYY-XXX"""
        import uuid
        year = datetime.now().year
        suffix = str(uuid.uuid4().int % 1000).zfill(3)
        return f"MTG-{year}-{suffix}"
```

### Booking Flow (Interactive Conversation)

```python
class BookingFlow:
    """
    Multi-turn conversation flow for booking/scheduling.
    Triggered when user says: "book", "schedule", "call", "appointment"
    """
    
    BOOKING_TRIGGERS = ["book", "schedule", "call", "appointment", "meeting"]
    
    SLOT_OPTIONS = {
        "morning": "09:00 - 12:00",
        "afternoon": "12:00 - 15:00", 
        "evening": "15:00 - 18:00"
    }
    
    def detect_booking_intent(self, transcript: str) -> bool:
        """Detect if user wants to book a meeting."""
        transcript_lower = transcript.lower()
        return any(trigger in transcript_lower for trigger in self.BOOKING_TRIGGERS)
    
    def start_booking_flow(self) -> dict:
        """Step 1: Start booking flow and ask for slot preference."""
        return {
            "response_text": "I'd be happy to help you schedule a call. Would you prefer a morning slot (9 AM - 12 PM), afternoon (12 PM - 3 PM), or evening slot (3 PM - 6 PM)?",
            "response_audio": self.sarvam_tts("I'd be happy to help you schedule a call. Would you prefer a morning, afternoon, or evening slot?"),
            "state": "awaiting_slot_preference",
            "booking_context": {"step": 1}
        }
    
    def handle_slot_selection(self, transcript: str, context: dict) -> dict:
        """Step 2: Parse slot preference and show available times."""
        slot = self.parse_slot_preference(transcript)
        
        # Get available slots from Google Calendar
        available_slots = self.get_available_slots(slot)
        
        return {
            "response_text": f"Great! Here are available {slot} slots:\n" + "\n".join([f"• {s}" for s in available_slots[:3]]),
            "response_audio": self.sarvam_tts(f"Great! I found {len(available_slots)} available slots in the {slot}. Please choose one."),
            "state": "awaiting_time_selection",
            "booking_context": {
                "step": 2,
                "slot_preference": slot,
                "available_slots": available_slots
            }
        }
    
    def parse_slot_preference(self, transcript: str) -> str:
        """Extract slot preference from transcript."""
        transcript_lower = transcript.lower()
        if any(word in transcript_lower for word in ["morning", "am"]):
            return "morning"
        elif any(word in transcript_lower for word in ["afternoon", "noon"]):
            return "afternoon"
        elif any(word in transcript_lower for word in ["evening", "pm", "late"]):
            return "evening"
        return "morning"  # default
    
    def get_available_slots(self, slot: str) -> list:
        """Query Google Calendar for available slots."""
        # MCP call to check availability
        return ["10:00 AM", "11:00 AM", "11:30 AM"] if slot == "morning" else []
    
    def handle_time_confirmation(self, transcript: str, context: dict) -> dict:
        """Step 3: Confirm time and book slot."""
        selected_time = self.parse_time_selection(transcript, context["available_slots"])
        
        return {
            "response_text": f"Perfect! I'll book your call for {selected_time}. One moment please...",
            "response_audio": self.sarvam_tts(f"Perfect! I'll book your call for {selected_time}. One moment please..."),
            "state": "booking_in_progress",
            "booking_context": {
                "step": 3,
                "slot_preference": context["slot_preference"],
                "selected_time": selected_time,
                "datetime": self.parse_datetime(selected_time)
            }
        }
    
    def parse_time_selection(self, transcript: str, available_slots: list) -> str:
        """Parse which time slot user selected."""
        # Use GPT-4o to match user's choice to available slots
        for slot in available_slots:
            if slot.lower() in transcript.lower():
                return slot
        return available_slots[0]  # default to first
    
    def execute_booking(self, context: dict) -> dict:
        """Step 4: Execute booking via MCP - Calendar + Email + Google Doc."""
        booking_code = self.generate_booking_code()
        datetime = context["datetime"]
        
        # MCP Call 1: Book Google Calendar slot
        calendar_result = self.mcp_create_calendar_hold(
            booking_code=booking_code,
            datetime=datetime,
            duration_minutes=30
        )
        
        # MCP Call 2: Send Email to advisor
        email_result = self.mcp_send_email(
            booking_code=booking_code,
            datetime=datetime,
            calendar_link=calendar_result.get("meet_url")
        )
        
        # MCP Call 3: Append to Google Doc
        doc_result = self.mcp_append_to_doc(
            booking_code=booking_code,
            datetime=datetime,
            context=context
        )
        
        # Build final response with booking code and Meet URL
        meet_url = calendar_result.get("meet_url", "")
        
        response_text = f"""Your call has been successfully scheduled! 

**Booking Code:** {booking_code}
**Date & Time:** {datetime.strftime('%A, %B %d at %I:%M %p')}
**Google Meet:** {meet_url}

I've also sent a confirmation email to your advisor. You'll receive a calendar invite shortly. Is there anything else I can help you with?"""
        
        return {
            "response_text": response_text,
            "response_audio": self.sarvam_tts(f"Your call has been scheduled! Your booking code is {booking_code}. The Google Meet link has been shared. I've also sent a confirmation email to your advisor."),
            "state": "booking_complete",
            "booking_result": {
                "booking_code": booking_code,
                "datetime": datetime,
                "meet_url": meet_url,
                "calendar_event_id": calendar_result.get("event_id"),
                "email_sent": email_result.get("success"),
                "doc_updated": doc_result.get("success")
            }
        }
    
    def mcp_create_calendar_hold(self, booking_code: str, datetime, duration_minutes: int) -> dict:
        """MCP Call: Create Google Calendar event."""
        # Returns: {event_id, meet_url, success}
        return {
            "event_id": f"CAL-{booking_code}",
            "meet_url": f"https://meet.google.com/{booking_code.lower().replace('-', '')}",
            "success": True
        }
    
    def mcp_send_email(self, booking_code: str, datetime, calendar_link: str) -> dict:
        """MCP Call: Send email to advisor."""
        return {"success": True, "message_id": f"EMAIL-{booking_code}"}
    
    def mcp_append_to_doc(self, booking_code: str, datetime, context: dict) -> dict:
        """MCP Call: Append booking info to tracking Google Doc."""
        return {"success": True, "doc_id": "DOC-TRACKING"}
```

### Conversation State Machine

```python
BOOKING_STATES = {
    "idle": {
        "transitions": ["awaiting_slot_preference"],
        "trigger": "detect_booking_intent"
    },
    "awaiting_slot_preference": {
        "transitions": ["awaiting_time_selection"],
        "handler": "handle_slot_selection"
    },
    "awaiting_time_selection": {
        "transitions": ["booking_in_progress"],
        "handler": "handle_time_confirmation"
    },
    "booking_in_progress": {
        "transitions": ["booking_complete"],
        "handler": "execute_booking"
    },
    "booking_complete": {
        "transitions": ["idle"],
        "final": True
    }
}
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | React / Vanilla JS / HTML / CSS | Production-grade UI with full customization |
| **Voice Activity Detection** | Silero VAD | Open-source, local processing, noise filtering |
| **Speech-to-Text** | Sarvam API (saarika-v2) | Optimized for Indian English accent |
| **Text-to-Speech** | Sarvam API | Natural Indian English voices |
| **Intent Processing** | GPT-4o | Function calling for structured extraction |
| **Template Engine** | Jinja2 | Dynamic greeting templates |
| **Backend API** | FastAPI / Flask | REST API for frontend communication |
| **State Management** | LocalStorage / Redux / Context API | Standard browser storage and state management |

### Frontend Options

| Feature | React | Vanilla JS |
|---------|-------|------------|
| **Setup Time** | 30 min | 20 min |
| **Audio Recording** | MediaRecorder API | MediaRecorder API |
| **Pipeline Status UI** | Components + hooks | DOM manipulation |
| **Chat Interface** | Custom components | Dynamic DOM |
| **State Management** | useState / Redux | LocalStorage |
| **Production Ready** | Yes | Yes |

### Sarvam API Details

**STT Models (English - Indian Accent):**
- `saarika-v2` - **Recommended** - Optimized for Indian English, higher accuracy
- `saarika-v1` - Indian English with good speed/accuracy balance
- `sarvam-1` - General purpose (fallback)

**TTS Voices (English - Indian Accent):**
- `meera` - Professional female (Indian English)
- `arjun` - Professional male (Indian English)
- `pavithra` - Friendly female (Indian English)
- `vikram` - Authoritative male (Indian English)

**Supported Language:**
- **English (Indian Accent)** - Primary and only supported language

**Accent Optimization:**
- Sarvam API trained on diverse Indian English accents
- Handles regional pronunciation variations
- Optimized for common Indian financial terminology

## Implementation

### Voice Agent Class with Sarvam + Silero

```python
import torch
import requests
from typing import Tuple, Optional
import numpy as np

class VoiceAgent:
    def __init__(self, sarvam_api_key: str):
        self.sarvam_api_key = sarvam_api_key
        self.sarvam_base_url = "https://api.sarvam.ai"
        
        # Load Silero VAD model
        self.vad_model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.vad_model.eval()
        
        self.conversation_history = []
    
    def process_voice_input(self, audio_bytes: bytes) -> Tuple[bytes, str]:
        """Process voice input and return audio response + transcript."""
        # 1. Apply VAD to segment audio
        speech_segments = self.apply_vad(audio_bytes)
        
        # 2. Speech-to-Text via Sarvam
        transcript = self.sarvam_stt(speech_segments)
        
        # 3. Intent processing
        intent = self.process_intent(transcript)
        
        # 4. Generate response
        response_text = self.generate_response(intent)
        
        # 5. Text-to-Speech via Sarvam
        response_audio = self.sarvam_tts(response_text, voice="meera")
        
        return response_audio, response_text
    
    def apply_vad(self, audio_bytes: bytes) -> bytes:
        """Apply Silero VAD to filter non-speech segments."""
        # Convert bytes to tensor
        audio_tensor = torch.from_numpy(
            np.frombuffer(audio_bytes, dtype=np.float32)
        )
        
        # Get speech timestamps
        speech_timestamps = self.vad_model(audio_tensor)
        
        # Extract speech segments
        speech_segments = []
        for ts in speech_timestamps:
            start, end = int(ts['start']), int(ts['end'])
            speech_segments.append(audio_tensor[start:end])
        
        # Concatenate speech segments
        if speech_segments:
            clean_audio = torch.cat(speech_segments)
            return clean_audio.numpy().tobytes()
        
        return audio_bytes
    
    def sarvam_stt(self, audio_bytes: bytes) -> str:
        """Convert speech to text using Sarvam API (English - Indian Accent)."""
        url = f"{self.sarvam_base_url}/speech-to-text"
        
        headers = {
            "api-subscription-key": self.sarvam_api_key
        }
        
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        
        data = {
            "model": "saarika-v2",  # Optimized for Indian English
            "language_code": "en-IN",  # English (India)
            "with_timestamps": False
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        result = response.json()
        
        return result.get("transcript", "")
    
    def sarvam_tts(self, text: str, voice: str = "meera") -> bytes:
        """Convert text to speech using Sarvam API (English - Indian Accent)."""
        url = f"{self.sarvam_base_url}/text-to-speech"
        
        headers = {
            "api-subscription-key": self.sarvam_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": [text],
            "target_language_code": "en-IN",  # English (India)
            "speaker": voice,
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.0,
            "enable_preprocessing": True
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        # Response contains audio bytes
        return response.content
    
    def process_intent(self, text: str) -> Intent:
        """Classify intent and extract entities using GPT-4o."""
        # Use GPT-4o for intent classification
        pass
    
    def generate_response(self, intent: Intent) -> str:
        """Generate text response based on intent."""
        pass
```

### Silero VAD Standalone Usage

```python
import torch
import numpy as np

class SileroVADProcessor:
    """Standalone Silero VAD for voice activity detection."""
    
    def __init__(self):
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.get_speech_timestamps = utils[0]
        self.model.eval()
    
    def detect_speech(self, audio_bytes: bytes, sample_rate: int = 16000) -> list:
        """
        Detect speech segments in audio.
        
        Returns:
            List of dicts with 'start' and 'end' timestamps (in samples)
        """
        # Convert bytes to numpy array
        audio_tensor = torch.from_numpy(
            np.frombuffer(audio_bytes, dtype=np.float32)
        )
        
        # Get speech timestamps
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor,
            self.model,
            threshold=0.5,  # Speech probability threshold
            sampling_rate=sample_rate,
            min_speech_duration_ms=250,  # Min 250ms speech
            max_speech_duration_s=10,  # Max 10s speech
            min_silence_duration_ms=500  # Min 500ms silence
        )
        
        return speech_timestamps
    
    def filter_speech(self, audio_bytes: bytes, sample_rate: int = 16000) -> bytes:
        """Filter audio to keep only speech segments."""
        timestamps = self.detect_speech(audio_bytes, sample_rate)
        
        audio_tensor = torch.from_numpy(
            np.frombuffer(audio_bytes, dtype=np.float32)
        )
        
        speech_segments = []
        for ts in timestamps:
            start, end = int(ts['start']), int(ts['end'])
            speech_segments.append(audio_tensor[start:end])
        
        if speech_segments:
            clean_audio = torch.cat(speech_segments)
            return clean_audio.numpy().tobytes()
        
        return audio_bytes
```

### Theme Integration

```python
class VoiceOptimizer:
    def __init__(self, theme_store: ThemeStoreAPI):
        self.theme_store = theme_store
    
    def get_contextual_greeting(self) -> str:
        """Get greeting with theme context."""
        themes = self.theme_store.get_current_themes()
        
        template = jinja2.Template("""
        {% if themes and themes[0].confidence >= 0.7 %}
        Hello! I see many users are asking about {{ themes[0].theme }} today. 
        I can help you book a call to discuss this!
        {% else %}
        Hello! How can I help you schedule a meeting today?
        {% endif %}
        """)
        
        return template.render(themes=themes)
```

## Session State

### Frontend State (LocalStorage/Redux)

```javascript
const appState = {
    "call_transcripts": [],  // Voice call history with Sarvam transcripts
    "active_bookings": [],  // List of booking codes
    "voice_settings": {
        "stt_model": "saarika-v2",  // Sarvam STT model (Indian English optimized)
        "tts_voice": "meera",       // Sarvam TTS voice (Indian English)
        "tts_language": "en-IN",    // English (India) - Indian accent
        "vad_threshold": 0.5        // Silero VAD threshold
    },
    
    // Pipeline Status for real-time progress tracking
    "pipeline_status": {
        "VAD": "idle",      // Silero VAD
        "STT": "idle",      // Sarvam STT
        "LLM": "idle",      // GPT-4o Intent
        "TTS": "idle",      // Sarvam TTS
        "Calendar": "idle", // Google Calendar
        "Doc": "idle",      // Google Doc
        "Email": "idle"     // Email
    }
};

// State management helper
const StateManager = {
    get: (key) => JSON.parse(localStorage.getItem(key) || 'null'),
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    getPipelineStatus: () => appState.pipeline_status,
    updatePipelineStep: (step, status) => {
        appState.pipeline_status[step] = status;
        // Trigger UI update
        document.dispatchEvent(new CustomEvent('pipelineUpdate', { detail: { step, status } }));
    }
};
```

### Backend State (Python/FastAPI)

```python
# In-memory state for demo (use Redis for production)
backend_state = {
    "call_transcripts": [],
    "active_bookings": [],
    "vad_processor": None,  # Cached Silero VAD model
}

from enum import Enum

class PipelineStatus(Enum):
    IDLE = "idle"       # Gray
    ACTIVE = "active"   # Amber
    DONE = "done"       # Green
    ERROR = "error"     # Red
```

## API Specification

```python
class VoiceAgentAPI:
    def process_audio(self, audio: bytes) -> Tuple[bytes, str]:
        """Process voice input and return audio response + transcript"""
    
    def get_greeting(self) -> str:
        """Get theme-aware greeting text"""
    
    def generate_booking(self, datetime: datetime, advisor: str) -> BookingResult:
        """Generate booking and trigger MCP actions"""

class BookingResult:
    booking_code: str
    calendar_hold_id: str
    email_draft_id: str
    status: str  # pending_approval
```

## Project Structure

```
src/pillar_b/
├── voice_optimizer.py    # Greeting generator (uses theme store)

src/pillar_c/
├── voice_handler.py      # Voice interaction logic
└── scheduling.py         # Booking logic
```

## Dependencies

### Backend (Python)

```txt
# Voice - Sarvam API
requests>=2.32.0  # For Sarvam API calls

# Voice - Silero VAD
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.26.0

# Templates
jinja2>=3.1.0

# Backend API (for React/Vanilla JS frontend)
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6  # For audio file uploads
```

### Frontend

**Option A: React**
```bash
# Create React app
npx create-react-app voice-agent-ui

# Or with Vite (faster)
npm create vite@latest voice-agent-ui -- --template react

# Required packages
npm install axios  # For API calls
```

**Option B: Vanilla JS**
```html
<!-- No build step required -->
<!-- Just HTML + CSS + JS files -->
```

## Environment Variables

```bash
# Sarvam AI API - English (Indian Accent) Only
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saarika-v2  # Optimized for Indian English
SARVAM_TTS_VOICE=meera       # meera, arjun, pavithra, vikram (all Indian English)
SARVAM_LANGUAGE=en-IN        # English (India) - Fixed to Indian accent

# Silero VAD
VAD_THRESHOLD=0.5
VAD_MIN_SPEECH_DURATION_MS=250
VAD_MIN_SILENCE_DURATION_MS=500
```

## Evaluation Rubric

| Criteria | Target | Measurement |
|----------|--------|-------------|
| **Transcription accuracy** | >90% | Word error rate on Indian accent samples |
| **VAD precision** | >95% | Correct speech/non-speech detection |
| **Theme mention** | 100% | Greeting includes top theme (if confidence > 0.7) |
| **Booking code visibility** | 100% | Code appears in M2 notes |

## References

1. [Sarvam AI Documentation](https://docs.sarvam.ai/)
2. [Sarvam STT API](https://docs.sarvam.ai/speech-to-text)
3. [Sarvam TTS API](https://docs.sarvam.ai/text-to-speech)
4. [Silero VAD GitHub](https://github.com/snakers4/silero-vad)
5. [Silero VAD PyTorch Hub](https://pytorch.org/hub/snakers4_silero-vad/)
6. [Jinja2 Templates](https://jinja.palletsprojects.com/)
