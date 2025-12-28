<![CDATA[<div align="center">

# 🤖 ARIA - Autonomous Reasoning & Intelligent Agent

### Your Personal AI Operating System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React Native](https://img.shields.io/badge/React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactnative.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**ARIA** is a next-generation **Large Action Model (LAM)** that transforms your smartphone into an intelligent personal assistant capable of executing real-world tasks autonomously.

[📖 Architecture](#architecture) • [🚀 Quick Start](#quick-start) • [🔧 Configuration](#configuration) • [📱 Demo](#demo)

</div>

---

## 🎯 Vision

Imagine telling your phone:
> *"Find me a good sci-fi movie tonight, book an Uber to get there, and make sure I don't miss my dentist appointment tomorrow morning."*

ARIA doesn't just understand this request—it **executes** it:
1. ✅ Checks your calendar for conflicts
2. 🎬 Searches for sci-fi movies playing nearby
3. 🚗 Books an Uber timed perfectly for the showtime
4. ⏰ Sets smart reminders for everything

This is the future of **Agentic AI**—moving beyond chatbots to **autonomous digital assistants**.

---

## 🏗️ Architecture Overview

ARIA implements a sophisticated **"Brain-Hand" Architecture** that separates reasoning from execution:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ARIA SUPER AGENT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🧠 THE BRAIN (Reasoning Engine)                   │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │  Intent       │  │   Context     │  │   Task Planning &     │   │   │
│  │  │  Recognition  │──│   Memory      │──│   Decomposition       │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  │                              │                                       │   │
│  │                    ┌─────────▼─────────┐                            │   │
│  │                    │  ORCHESTRATOR     │                            │   │
│  │                    │  (LangGraph)      │                            │   │
│  │                    └─────────┬─────────┘                            │   │
│  └──────────────────────────────┼──────────────────────────────────────┘   │
│                                 │                                           │
│  ┌──────────────────────────────▼──────────────────────────────────────┐   │
│  │                    🖐️ THE HANDS (Execution Layer)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  Transport  │  │  Calendar   │  │   Medical   │  │  Reminder │  │   │
│  │  │   Agent     │  │   Agent     │  │    Agent    │  │   Agent   │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │   │
│  └─────────┼────────────────┼────────────────┼───────────────┼────────┘   │
│            │                │                │               │             │
├────────────▼────────────────▼────────────────▼───────────────▼─────────────┤
│                        🔌 INTEGRATION TIERS                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│  │   TIER 1: API   │  │ TIER 2: WEB     │  │   TIER 3: DEVICE        │    │
│  │   ─────────────  │  │ AUTOMATION      │  │   CONTROL               │    │
│  │   • Uber API    │  │ ─────────────── │  │   ────────────────────  │    │
│  │   • Google Cal  │  │ • Playwright    │  │   • Android A11y API   │    │
│  │   • TMDB        │  │ • Puppeteer     │  │   • iOS Shortcuts      │    │
│  │   • Twilio      │  │ • Selenium      │  │   • Screen Control     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Philosophy

| Component | Role | Technology |
|-----------|------|------------|
| **Brain** | Understands intent, plans multi-step actions, maintains context | LLM (GPT-4o/Claude/Llama) + LangGraph |
| **Hands** | Executes specific tasks via APIs, web automation, or device control | FastAPI + Playwright + Android A11y |
| **Memory** | Stores user preferences, history, and context | PostgreSQL + pgvector |
| **Guardian** | Ensures privacy, masks PII, manages permissions | On-device processing |

---

## 🧩 Multi-Agent Orchestration

ARIA uses **Multi-Agent Orchestration** because a single AI cannot reliably handle complex, multi-domain requests. Each agent specializes in its domain:

```
┌──────────────────────────────────────────────────────────────────┐
│                     🎯 DISPATCHER AGENT                          │
│            (Receives request, decomposes into tasks)             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 🚗 Transport  │    │ 📅 Calendar   │    │ 🏥 Medical    │
│    Agent      │    │    Agent      │    │    Agent      │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ • Uber API    │    │ • Google Cal  │    │ • Vezeeta     │
│ • Lyft API    │    │ • Outlook     │    │ • Web Scrape  │
│ • Location    │    │ • Scheduling  │    │ • Booking     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │ 📊 RESULT     │
                    │ AGGREGATOR    │
                    └───────────────┘
```

### Agent Communication Protocol

```python
# Example: How agents collaborate on a complex request
User: "Book a dermatologist for tomorrow afternoon, and schedule an Uber"

# Step 1: Dispatcher decomposes the request
dispatcher.decompose() → [
    Task(agent="calendar", action="check_availability", time="tomorrow afternoon"),
    Task(agent="medical", action="find_dermatologist", location="user_area"),
    Task(agent="transport", action="book_ride", depends_on=["medical.appointment_time"])
]

# Step 2: Calendar Agent checks conflicts
calendar_agent.execute() → {"available": True, "conflicts": []}

# Step 3: Medical Agent books appointment (parallel with calendar check)
medical_agent.execute() → {"doctor": "Dr. Ahmed", "time": "3:00 PM", "location": "..."}

# Step 4: Transport Agent books ride (after medical confirms)
transport_agent.execute() → {"pickup": "2:30 PM", "eta": "25 min", "price": "$12"}

# Step 5: Aggregator compiles final response
→ "Done! Dr. Ahmed at 3 PM, Uber picking you up at 2:30 PM ($12)"
```

---

## 📁 Project Structure

```
superapp/
├── 📄 README.md                    # You are here
├── 📄 LICENSE                      # MIT License
├── 📄 .env.example                 # Environment variables template
├── 📄 docker-compose.yml           # Container orchestration
│
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.md             # Detailed architecture docs
│   ├── API_REFERENCE.md            # API documentation
│   ├── AGENT_DESIGN.md             # Agent design patterns
│   ├── INTEGRATION_GUIDE.md        # Third-party integration guide
│   ├── SECURITY.md                 # Security & privacy considerations
│   └── diagrams/                   # Architecture diagrams
│
├── 📁 backend/                     # FastAPI Backend
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 Dockerfile               # Backend container
│   ├── 📁 app/
│   │   ├── 📄 main.py              # FastAPI entry point
│   │   ├── 📄 config.py            # Configuration management
│   │   ├── 📁 api/                 # API routes
│   │   │   ├── 📄 chat.py          # Chat endpoint
│   │   │   ├── 📄 tasks.py         # Task management
│   │   │   └── 📄 webhooks.py      # External webhooks
│   │   ├── 📁 agents/              # Multi-agent system
│   │   │   ├── 📄 orchestrator.py  # LangGraph orchestrator
│   │   │   ├── 📄 dispatcher.py    # Task dispatcher
│   │   │   ├── 📄 transport.py     # Uber/Lyft agent
│   │   │   ├── 📄 calendar.py      # Calendar agent
│   │   │   ├── 📄 medical.py       # Healthcare agent
│   │   │   ├── 📄 reminder.py      # Reminder agent
│   │   │   ├── 📄 movie.py         # Entertainment agent
│   │   │   └── 📄 base.py          # Base agent class
│   │   ├── 📁 tools/               # Agent tools
│   │   │   ├── 📄 uber_api.py      # Uber integration
│   │   │   ├── 📄 google_calendar.py
│   │   │   ├── 📄 tmdb_api.py      # Movie database
│   │   │   ├── 📄 twilio_sms.py    # SMS notifications
│   │   │   └── 📄 web_automation.py
│   │   ├── 📁 automation/          # Web automation
│   │   │   ├── 📄 browser.py       # Playwright wrapper
│   │   │   ├── 📄 vezeeta.py       # Vezeeta automation
│   │   │   └── 📄 generic.py       # Generic web agent
│   │   ├── 📁 memory/              # Context & memory
│   │   │   ├── 📄 vector_store.py  # pgvector integration
│   │   │   ├── 📄 conversation.py  # Chat history
│   │   │   └── 📄 user_preferences.py
│   │   ├── 📁 security/            # Privacy & security
│   │   │   ├── 📄 pii_sanitizer.py # PII detection/masking
│   │   │   ├── 📄 permissions.py   # Permission management
│   │   │   └── 📄 encryption.py    # Data encryption
│   │   └── 📁 models/              # Data models
│   │       ├── 📄 schemas.py       # Pydantic schemas
│   │       └── 📄 database.py      # SQLAlchemy models
│   └── 📁 tests/                   # Backend tests
│
├── 📁 mobile/                      # React Native App
│   ├── 📄 package.json
│   ├── 📄 app.json
│   ├── 📁 src/
│   │   ├── 📁 screens/             # App screens
│   │   │   ├── 📄 ChatScreen.tsx   # Main chat interface
│   │   │   ├── 📄 TasksScreen.tsx  # Active tasks view
│   │   │   ├── 📄 SettingsScreen.tsx
│   │   │   └── 📄 PermissionsScreen.tsx
│   │   ├── 📁 components/          # UI components
│   │   │   ├── 📄 ChatBubble.tsx
│   │   │   ├── 📄 TaskCard.tsx
│   │   │   ├── 📄 VoiceInput.tsx
│   │   │   └── 📄 ActionConfirmation.tsx
│   │   ├── 📁 services/            # API services
│   │   │   ├── 📄 api.ts           # Backend API client
│   │   │   ├── 📄 websocket.ts     # Real-time updates
│   │   │   └── 📄 permissions.ts   # Device permissions
│   │   ├── 📁 hooks/               # React hooks
│   │   └── 📁 utils/               # Utilities
│   └── 📁 android/                 # Android-specific
│       └── 📁 accessibility/       # A11y service for device control
│
├── 📁 automation/                  # Standalone automation scripts
│   ├── 📄 requirements.txt
│   ├── 📁 scripts/
│   │   ├── 📄 vezeeta_booking.py   # Vezeeta automation demo
│   │   └── 📄 generic_web_agent.py
│   └── 📁 recordings/              # Browser session recordings
│
└── 📁 examples/                    # Usage examples
    ├── 📄 simple_task.py           # Single task example
    ├── 📄 complex_workflow.py      # Multi-agent workflow
    └── 📄 demo_scenarios.py        # Demo scenarios
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/superapp.git
cd superapp

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (see Configuration section)
```

### 2. Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Start Mobile App

```bash
cd mobile

# Install dependencies
npm install

# Start Expo development server
npx expo start
```

### 4. Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

---

## 🔧 Configuration

### Environment Variables

```env
# .env file

# ===========================================
# AI MODEL CONFIGURATION
# ===========================================
# Choose your LLM provider (openai, anthropic, local)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here

# For local models (Ollama, vLLM)
LOCAL_LLM_ENDPOINT=http://localhost:11434

# ===========================================
# DATABASE
# ===========================================
DATABASE_URL=postgresql://user:pass@localhost:5432/aria
REDIS_URL=redis://localhost:6379

# ===========================================
# EXTERNAL APIS
# ===========================================
# Uber (https://developer.uber.com)
UBER_CLIENT_ID=your-client-id
UBER_CLIENT_SECRET=your-secret
UBER_SERVER_TOKEN=your-server-token

# Google Calendar (https://console.cloud.google.com)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret

# TMDB (https://www.themoviedb.org/settings/api)
TMDB_API_KEY=your-api-key

# Twilio (https://www.twilio.com)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

# ===========================================
# SECURITY
# ===========================================
SECRET_KEY=your-super-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key

# ===========================================
# WEB AUTOMATION
# ===========================================
BROWSER_HEADLESS=true
BROWSERLESS_API_KEY=your-browserless-key  # Optional cloud browser
```

---

## 📱 Demo Scenarios

### Scenario 1: Simple Ride Booking

```
User: "Book me an Uber to Cairo Festival City"

ARIA:
├─ 🔍 Detecting intent: TRANSPORT_REQUEST
├─ 📍 Getting your current location...
├─ 🚗 Searching for available rides...
├─ 💰 Found: UberX - $8.50 (12 min away)
└─ ✅ Ride confirmed! Driver Ahmed arriving in 12 min
```

### Scenario 2: Complex Multi-Agent Task

```
User: "I need to see a dermatologist tomorrow, book the appointment 
       and arrange transport to get there"

ARIA:
├─ 🧠 Breaking down your request...
│   ├─ Task 1: Find available dermatologist
│   ├─ Task 2: Check calendar conflicts
│   └─ Task 3: Book transportation
│
├─ 📅 Calendar Agent: Tomorrow 2-6 PM is free
├─ 🏥 Medical Agent: Found Dr. Sarah (Vezeeta) - 3:30 PM available
├─ 🚗 Transport Agent: Uber pickup at 3:00 PM - $12
│
├─ 📋 SUMMARY:
│   ├─ Appointment: Dr. Sarah, Dermatologist
│   ├─ Time: Tomorrow, 3:30 PM
│   ├─ Location: Medical Center, Nasr City
│   ├─ Transport: Uber at 3:00 PM ($12)
│   └─ Total estimated cost: $62 (appointment) + $12 (ride)
│
└─ ⏳ Waiting for your confirmation...
```

### Scenario 3: Entertainment Planning

```
User: "Find me a good sci-fi movie tonight and check if I'm free"

ARIA:
├─ 🎬 Movie Agent: Searching sci-fi movies...
│   ├─ "Dune: Part Two" - 8:00 PM @ IMAX City Stars (⭐ 8.5)
│   ├─ "Interstellar" (Re-release) - 7:30 PM @ VOX Cinemas
│   └─ "The Creator" - 9:00 PM @ Galaxy Cinema
│
├─ 📅 Calendar Agent: Checking tonight...
│   └─ ⚠️ Conflict: Dinner with Ahmed at 7:30 PM
│
├─ 🤔 Recommendation: "Dune: Part Two" at 8:00 PM works best!
│   └─ Your dinner ends ~8:30 PM, but the 9:00 PM showing 
│      at Galaxy Cinema would be perfect timing.
│
└─ Would you like me to book tickets for the 9:00 PM showing?
```

---

## 🔒 Security & Privacy

ARIA implements a **Privacy-First Architecture**:

### 1. PII Sanitization
```python
# Before sending to cloud LLM
original = "Book appointment for Ahmed Hassan, phone 01012345678"
sanitized = "Book appointment for [NAME_1], phone [PHONE_1]"

# After receiving response, restore original values
```

### 2. Local Processing
- Sensitive data stored locally using AES-256 encryption
- User preferences never leave the device unnecessarily
- On-device intent classification for common requests

### 3. Permission Model
```
┌─────────────────────────────────────────┐
│         ARIA Permission Levels          │
├─────────────────────────────────────────┤
│ Level 1: READ ONLY                      │
│   • View calendar                       │
│   • Check weather                       │
│   • Search information                  │
├─────────────────────────────────────────┤
│ Level 2: SUGGEST & CONFIRM              │
│   • Propose actions                     │
│   • Require user approval               │
│   • Draft messages (don't send)         │
├─────────────────────────────────────────┤
│ Level 3: ACT AUTONOMOUSLY               │
│   • Book rides (within budget)          │
│   • Schedule appointments               │
│   • Send notifications                  │
├─────────────────────────────────────────┤
│ Level 4: FULL AGENT MODE                │
│   • Device control                      │
│   • Financial transactions              │
│   • Multi-app orchestration             │
└─────────────────────────────────────────┘
```

---

## 🛠️ Technology Deep Dive

### Why LangGraph?

LangGraph provides **stateful, cyclic agent workflows** that are essential for:

1. **Memory Persistence**: Maintaining conversation context across turns
2. **Conditional Branching**: "If calendar is busy, suggest alternatives"
3. **Parallel Execution**: Running multiple agents simultaneously
4. **Human-in-the-Loop**: Pausing for user confirmation

```python
# LangGraph workflow example
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Define nodes (agents)
workflow.add_node("dispatcher", dispatcher_agent)
workflow.add_node("calendar", calendar_agent)
workflow.add_node("transport", transport_agent)
workflow.add_node("medical", medical_agent)

# Define edges (flow)
workflow.add_conditional_edges(
    "dispatcher",
    route_to_agent,
    {
        "calendar": "calendar",
        "transport": "transport",
        "medical": "medical",
        "end": END
    }
)
```

### Integration Tiers Explained

| Tier | Method | Speed | Reliability | Use Case |
|------|--------|-------|-------------|----------|
| **Tier 1** | Direct API | ⚡ Fast | ✅ High | Uber, Google Calendar, TMDB |
| **Tier 2** | Web Automation | 🐢 Slow | ⚠️ Medium | Vezeeta, booking sites |
| **Tier 3** | Device Control | 🐢 Slow | ⚠️ Low | Apps without API/web access |

---

## 📊 System Requirements

### Minimum (Development)
- 8GB RAM
- 4 CPU cores
- 10GB storage

### Recommended (Production)
- 16GB RAM
- 8 CPU cores
- GPU (for local LLM inference)
- 50GB SSD storage

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) for the incredible agent framework
- [Anthropic](https://anthropic.com) for Claude's computer use capabilities
- The AI Ideas Bootcamp instructors for the inspiring challenge

---

<div align="center">

**Built with ❤️ for the AI Ideas Bootcamp**

*"The future of AI is not just understanding—it's doing."*

</div>
]]>