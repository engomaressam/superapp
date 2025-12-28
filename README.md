# 🤖 ARIA - Autonomous Reasoning & Intelligent Agent

<p align="center">
  <strong>Your Personal AI Operating System</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React Native">
  <img src="https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangGraph">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT">
</p>

<p align="center">
  <b>ARIA</b> is a next-generation <b>Large Action Model (LAM)</b> that transforms your smartphone into an intelligent personal assistant capable of executing real-world tasks autonomously.
</p>

<p align="center">
  <a href="#-architecture">📖 Architecture</a> •
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-demo-scenarios">📱 Demo</a> •
  <a href="#-agents">🤖 Agents</a> •
  <a href="presentation/index.html">🎯 Presentation</a>
</p>

---

## 🎯 Vision

Imagine telling your phone:

> *"Find me a good sci-fi movie tonight, book an Uber to get there, and make sure I don't miss my dentist appointment tomorrow morning."*

ARIA doesn't just understand this request—it **executes** it:

| Step | Action | Agent |
|------|--------|-------|
| 1 | ✅ Checks your calendar for conflicts | Calendar Agent |
| 2 | 🎬 Searches for sci-fi movies playing nearby | Movie Agent |
| 3 | 🚗 Books an Uber timed perfectly | Transport Agent |
| 4 | ⏰ Sets smart reminders | Reminder Agent |

This is the future of **Agentic AI**—moving beyond chatbots to **autonomous digital assistants**.

---

## 📱 App Preview

<p align="center">
  <img src="docs/images/ui-mockup-chat.png" alt="Chat Screen" width="250">
  <img src="docs/images/ui-mockup-action.png" alt="Action Card" width="250">
  <img src="docs/images/ui-mockup-tasks.png" alt="Tasks Screen" width="250">
</p>

> **Note:** See the full interactive UI mockup at [docs/ui-mockup.html](docs/ui-mockup.html)

---

## 🏗️ Architecture

ARIA implements a sophisticated **"Brain-Hand" Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                     ARIA SUPER AGENT                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   🧠 BRAIN (Reasoning Engine)                               │
│   ├── Intent Recognition                                     │
│   ├── Context Memory                                         │
│   └── Task Planning                                          │
│              │                                               │
│              ▼                                               │
│   🎯 ORCHESTRATOR (LangGraph)                               │
│   ├── State Machine                                          │
│   ├── Agent Routing                                          │
│   └── Result Aggregation                                     │
│              │                                               │
│              ▼                                               │
│   🖐️ HANDS (12 Specialized Agents)                          │
│   ├── Transport │ Calendar │ Medical │ Movie │ Reminder     │
│   └── Weather │ Food │ Finance │ Shopping │ Smart Home      │
│       │ Email │ Travel                                       │
│              │                                               │
│              ▼                                               │
│   🔌 INTEGRATION TIERS                                       │
│   ├── Tier 1: Direct APIs (Uber, Google, TMDB)              │
│   ├── Tier 2: Web Automation (Playwright)                   │
│   └── Tier 3: Device Control (Android A11y)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Role | Technology |
|-----------|------|------------|
| **Brain** | Understands intent, plans multi-step actions | LLM + LangGraph |
| **Hands** | Executes tasks via APIs/automation | FastAPI + Playwright |
| **Memory** | Stores preferences and context | PostgreSQL + pgvector |
| **Guardian** | Privacy protection, PII masking | On-device processing |

---

## 🤖 Agents

ARIA includes **12 specialized agents**, each handling specific domains:

### Core Agents (Instructor Examples)

| Agent | Description | Integration |
|-------|-------------|-------------|
| 🚗 **Transport** | Book rides, track drivers, estimate fares | Uber/Lyft API |
| 📅 **Calendar** | Manage events, check availability, detect conflicts | Google Calendar |
| 🏥 **Medical** | Find doctors, book appointments | Vezeeta (Playwright) |
| 🎬 **Movie** | Search films, find showtimes, get recommendations | TMDB API |
| ⏰ **Reminder** | Smart notifications, recurring alerts | Push Notifications |

### Extended Agents (Additional Capabilities)

| Agent | Description | Integration |
|-------|-------------|-------------|
| 🌤️ **Weather** | Forecasts, alerts, activity recommendations | OpenWeatherMap |
| 🍕 **Food** | Restaurant search, food delivery, reservations | Talabat/UberEats |
| 💰 **Finance** | Check balances, pay bills, track spending | Banking APIs |
| 🛒 **Shopping** | Product search, price comparison, order tracking | Amazon/Noon |
| 🏠 **Smart Home** | Control lights, AC, locks, scenes | Google Home/Alexa |
| 📧 **Email** | Inbox management, AI summaries, draft replies | Gmail/Outlook |
| ✈️ **Travel** | Flight search, hotel booking, trip planning | Booking APIs |

---

## 🔄 Multi-Agent Workflow

Here's how agents collaborate on complex requests:

```
User: "Book a dermatologist for tomorrow and arrange an Uber"
                    │
                    ▼
         ┌─────────────────┐
         │   DISPATCHER    │ ← Parses intent, creates plan
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐
│Calendar│  │Medical │  │  Uber  │
│ Agent  │  │ Agent  │  │ Agent  │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    ▼           ▼           ▼
 "Free at    "Dr.Sara    "Pickup
  2-6PM"     3:30PM"     3:00PM"
    │           │           │
    └─────────────┼─────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   AGGREGATOR    │
         └────────┬────────┘
                  │
                  ▼
    "✅ Dr. Sara at 3:30 PM
     🚗 Uber pickup 3:00 PM ($12)
     Confirm?"
```

---

## 📁 Project Structure

```
superapp/
├── 📄 README.md              
├── 📄 docker-compose.yml     
│
├── 📁 backend/               # FastAPI Backend
│   ├── app/
│   │   ├── agents/           # 12 Specialized Agents
│   │   │   ├── transport.py  # 🚗 Uber integration
│   │   │   ├── calendar.py   # 📅 Google Calendar
│   │   │   ├── medical.py    # 🏥 Vezeeta automation
│   │   │   ├── movie.py      # 🎬 TMDB integration
│   │   │   ├── reminder.py   # ⏰ Notifications
│   │   │   ├── weather.py    # 🌤️ Weather forecasts
│   │   │   ├── food.py       # 🍕 Food delivery
│   │   │   ├── finance.py    # 💰 Banking
│   │   │   ├── shopping.py   # 🛒 E-commerce
│   │   │   ├── smart_home.py # 🏠 IoT control
│   │   │   ├── email.py      # 📧 Email management
│   │   │   └── travel.py     # ✈️ Travel booking
│   │   ├── api/              # REST endpoints
│   │   ├── automation/       # Playwright scripts
│   │   └── orchestrator.py   # LangGraph workflow
│   └── requirements.txt
│
├── 📁 mobile/                # React Native App
│   ├── src/
│   │   ├── screens/          # App screens
│   │   ├── components/       # UI components
│   │   └── services/         # API client
│   └── package.json
│
├── 📁 presentation/          # Interactive Slides
│   └── index.html            # Open in browser
│
└── 📁 docs/                  # Documentation
    ├── ARCHITECTURE.md
    ├── AGENT_DESIGN.md
    ├── API_REFERENCE.md
    ├── SECURITY.md
    └── images/               # UI mockups
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### 1. Clone & Setup

```bash
git clone https://github.com/engomaressam/superapp.git
cd superapp
cp env.example.txt .env
```

### 2. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start Mobile App

```bash
cd mobile
npm install
npx expo start
```

### 4. Using Docker

```bash
docker-compose up -d
```

---

## 📱 Demo Scenarios

### Scenario 1: Simple Ride Booking

```
👤 User: "Book me an Uber to Cairo Festival City"

🤖 ARIA:
   ├─ 🔍 Detecting intent: TRANSPORT_REQUEST
   ├─ 📍 Getting your current location...
   ├─ 🚗 Searching for available rides...
   └─ ✅ Ride confirmed! Driver Ahmed, 12 min away ($8.50)
```

### Scenario 2: Complex Multi-Agent Task

```
👤 User: "Find a dermatologist for tomorrow and arrange transport"

🤖 ARIA:
   ├─ 🧠 Breaking down request...
   │   ├─ Task 1: Check calendar
   │   ├─ Task 2: Find dermatologist  
   │   └─ Task 3: Book transport
   │
   ├─ 📅 Calendar: Tomorrow 2-6 PM free
   ├─ 🏥 Medical: Dr. Sarah at 3:30 PM (Vezeeta)
   ├─ 🚗 Transport: Uber at 3:00 PM - $12
   │
   └─ 📋 SUMMARY:
       ├─ Doctor: Dr. Sarah, Dermatologist
       ├─ Time: Tomorrow, 3:30 PM
       ├─ Transport: Uber at 3:00 PM
       └─ Total: $62 + $12 = $74
       
   ⏳ Waiting for confirmation...
```

---

## 🔒 Security & Privacy

| Feature | Description |
|---------|-------------|
| **PII Sanitization** | Names, phones, cards masked before LLM processing |
| **Permission Levels** | 4-tier model from read-only to full autonomy |
| **Human-in-Loop** | Critical actions require user confirmation |
| **Audit Logging** | Full traceability of all agent actions |
| **Local Storage** | Sensitive data encrypted on-device |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **AI/LLM** | GPT-4 / Claude / Open-source LLMs |
| **Orchestration** | LangGraph, LangChain |
| **Backend** | FastAPI, Python 3.11+ |
| **Mobile** | React Native, Expo, TypeScript |
| **Web Automation** | Playwright |
| **Database** | PostgreSQL + pgvector |
| **Cache** | Redis |
| **Containers** | Docker, Docker Compose |

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Specialized Agents | 12 |
| Integration Tiers | 3 |
| Source Files | 50+ |
| Lines of Code | 15,000+ |
| Documentation Pages | 6 |

---

## 🎯 Interactive Presentation

View the full presentation for instructors:

1. **Option A:** Open `presentation/index.html` directly in browser
2. **Option B:** Serve locally:
   ```bash
   cd presentation
   python -m http.server 8080
   # Open http://localhost:8080
   ```

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with ❤️ for the AI Ideas Bootcamp</b>
  <br>
  <i>"The future of AI is not just understanding—it's doing."</i>
</p>
