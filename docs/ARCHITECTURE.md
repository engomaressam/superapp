<![CDATA[# 🏗️ ARIA Architecture Deep Dive

## Table of Contents
1. [System Overview](#system-overview)
2. [The Brain-Hand Architecture](#the-brain-hand-architecture)
3. [Multi-Agent Orchestration](#multi-agent-orchestration)
4. [Integration Tiers](#integration-tiers)
5. [Data Flow](#data-flow)
6. [State Management](#state-management)
7. [Security Architecture](#security-architecture)

---

## System Overview

ARIA (Autonomous Reasoning & Intelligent Agent) is built on the principle of **separation of concerns**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HIGH-LEVEL ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────┐                                                          │
│    │   Mobile    │◄──────────────┐                                          │
│    │    App      │               │                                          │
│    └──────┬──────┘               │                                          │
│           │                      │                                          │
│           │ WebSocket/REST       │ Push Notifications                       │
│           │                      │                                          │
│           ▼                      │                                          │
│    ┌─────────────────────────────┴──────────────────────────────────────┐  │
│    │                         BACKEND (FastAPI)                           │  │
│    │  ┌─────────────────────────────────────────────────────────────┐   │  │
│    │  │                    API Gateway Layer                         │   │  │
│    │  │  • Authentication  • Rate Limiting  • Request Validation     │   │  │
│    │  └─────────────────────────────┬───────────────────────────────┘   │  │
│    │                                │                                    │  │
│    │  ┌─────────────────────────────▼───────────────────────────────┐   │  │
│    │  │                    ORCHESTRATION LAYER                       │   │  │
│    │  │              (LangGraph State Machine)                       │   │  │
│    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │  │
│    │  │  │Dispatcher│  │ Planner  │  │ Executor │  │Aggregator│    │   │  │
│    │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │  │
│    │  └─────────────────────────────┬───────────────────────────────┘   │  │
│    │                                │                                    │  │
│    │  ┌─────────────────────────────▼───────────────────────────────┐   │  │
│    │  │                      AGENT LAYER                             │   │  │
│    │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌───────┐ │   │  │
│    │  │  │Calendar│  │Transprt│  │Medical │  │ Movie  │  │Remindr│ │   │  │
│    │  │  │ Agent  │  │ Agent  │  │ Agent  │  │ Agent  │  │ Agent │ │   │  │
│    │  │  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘  └───┬───┘ │   │  │
│    │  └──────┼───────────┼───────────┼───────────┼───────────┼─────┘   │  │
│    │         │           │           │           │           │          │  │
│    │  ┌──────▼───────────▼───────────▼───────────▼───────────▼─────┐   │  │
│    │  │                       TOOLS LAYER                           │   │  │
│    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │  │
│    │  │  │  TIER 1     │  │   TIER 2    │  │      TIER 3         │ │   │  │
│    │  │  │  APIs       │  │   Web Auto  │  │    Device Control   │ │   │  │
│    │  │  │ ─────────── │  │  ────────── │  │  ─────────────────  │ │   │  │
│    │  │  │ • Uber      │  │ • Playwright│  │  • Android A11y     │ │   │  │
│    │  │  │ • Google    │  │ • Puppeteer │  │  • iOS Shortcuts    │ │   │  │
│    │  │  │ • TMDB      │  │ • Selenium  │  │  • Screen Reader    │ │   │  │
│    │  │  │ • Twilio    │  │             │  │                     │ │   │  │
│    │  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │  │
│    │  └────────────────────────────────────────────────────────────┘   │  │
│    └────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│    ┌───────────────────────────────────────────────────────────────────┐  │
│    │                         DATA LAYER                                 │  │
│    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │  │
│    │  │  PostgreSQL  │  │    Redis     │  │      ChromaDB        │    │  │
│    │  │  (Primary)   │  │   (Cache)    │  │   (Vector Store)     │    │  │
│    │  └──────────────┘  └──────────────┘  └──────────────────────┘    │  │
│    └───────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Brain-Hand Architecture

### The Brain: Reasoning Engine

The "Brain" is responsible for:
1. **Understanding** - Parsing natural language into structured intents
2. **Planning** - Breaking complex requests into actionable steps
3. **Reasoning** - Making decisions based on context and constraints
4. **Learning** - Adapting to user preferences over time

```python
class ReasoningEngine:
    """
    The Brain of ARIA - handles all cognitive tasks.
    """
    
    def __init__(self, llm: BaseLLM, memory: MemoryStore):
        self.llm = llm
        self.memory = memory
        self.intent_classifier = IntentClassifier()
        self.task_planner = TaskPlanner()
    
    async def process(self, user_input: str, context: Context) -> Plan:
        # Step 1: Understand the intent
        intent = await self.intent_classifier.classify(user_input)
        
        # Step 2: Retrieve relevant context
        relevant_memory = await self.memory.retrieve(user_input, k=5)
        
        # Step 3: Plan the execution
        plan = await self.task_planner.create_plan(
            intent=intent,
            context=context,
            memory=relevant_memory,
            user_preferences=context.user.preferences
        )
        
        return plan
```

### The Hands: Execution Layer

The "Hands" are specialized agents that execute specific tasks:

```python
class BaseAgent(ABC):
    """
    Abstract base class for all execution agents.
    """
    
    name: str
    description: str
    tools: List[Tool]
    
    @abstractmethod
    async def execute(self, task: Task, context: Context) -> AgentResult:
        """Execute the assigned task."""
        pass
    
    @abstractmethod
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the given task."""
        pass
```

---

## Multi-Agent Orchestration

### Why Multi-Agent?

Single-agent systems fail on complex tasks because:
1. **Context Overflow** - Too much information for one prompt
2. **Specialization** - Different tasks need different expertise
3. **Parallelization** - Independent tasks should run concurrently
4. **Fault Isolation** - One failure shouldn't crash everything

### Agent Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENT HIERARCHY                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATOR                              │   │
│  │              (LangGraph State Machine)                       │   │
│  │                                                              │   │
│  │  • Manages overall workflow state                            │   │
│  │  • Routes tasks to appropriate agents                        │   │
│  │  • Handles failures and retries                              │   │
│  │  • Coordinates parallel execution                            │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────▼───────────────────────────────┐   │
│  │                    DISPATCHER AGENT                          │   │
│  │                                                              │   │
│  │  • Analyzes user request                                     │   │
│  │  • Identifies required capabilities                          │   │
│  │  • Decomposes into subtasks                                  │   │
│  │  • Assigns priorities and dependencies                       │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                    │
│         ┌──────────────────────┼──────────────────────┐            │
│         │                      │                      │            │
│         ▼                      ▼                      ▼            │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐      │
│  │  CALENDAR   │       │  TRANSPORT  │       │   MEDICAL   │      │
│  │   AGENT     │       │    AGENT    │       │    AGENT    │      │
│  ├─────────────┤       ├─────────────┤       ├─────────────┤      │
│  │ Tools:      │       │ Tools:      │       │ Tools:      │      │
│  │ • Google Cal│       │ • Uber API  │       │ • Vezeeta   │      │
│  │ • Outlook   │       │ • Lyft API  │       │ • Web Auto  │      │
│  │ • iCal      │       │ • Maps API  │       │ • Scraping  │      │
│  └─────────────┘       └─────────────┘       └─────────────┘      │
│                                                                     │
│         ┌──────────────────────┬──────────────────────┐            │
│         │                      │                      │            │
│         ▼                      ▼                      ▼            │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐      │
│  │   MOVIE     │       │  REMINDER   │       │  WEB AUTO   │      │
│  │   AGENT     │       │    AGENT    │       │   AGENT     │      │
│  ├─────────────┤       ├─────────────┤       ├─────────────┤      │
│  │ Tools:      │       │ Tools:      │       │ Tools:      │      │
│  │ • TMDB API  │       │ • Push Notif│       │ • Playwright│      │
│  │ • Showtimes │       │ • SMS       │       │ • Browser   │      │
│  │ • Reviews   │       │ • Email     │       │ • Scraping  │      │
│  └─────────────┘       └─────────────┘       └─────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Communication

Agents communicate through a **message passing** system:

```python
@dataclass
class AgentMessage:
    sender: str
    recipient: str
    type: MessageType  # REQUEST, RESPONSE, ERROR, STATUS
    content: dict
    correlation_id: str
    timestamp: datetime

# Example message flow
messages = [
    AgentMessage(
        sender="dispatcher",
        recipient="calendar",
        type=MessageType.REQUEST,
        content={"action": "check_availability", "date": "2024-01-15"},
        correlation_id="task-123"
    ),
    AgentMessage(
        sender="calendar",
        recipient="dispatcher",
        type=MessageType.RESPONSE,
        content={"available": True, "slots": ["10:00", "14:00", "16:00"]},
        correlation_id="task-123"
    )
]
```

---

## Integration Tiers

### Tier 1: Direct API Integration

**Best for**: Services with official APIs (Uber, Google, etc.)

```python
class UberTool(BaseTool):
    """
    Direct integration with Uber API.
    """
    
    name = "uber_ride"
    description = "Book an Uber ride from point A to point B"
    
    async def execute(
        self, 
        pickup_location: Location,
        dropoff_location: Location,
        ride_type: str = "UberX"
    ) -> RideResult:
        async with UberClient(self.config) as client:
            # Get price estimate
            estimate = await client.get_estimate(
                pickup=pickup_location,
                dropoff=dropoff_location,
                ride_type=ride_type
            )
            
            # Request ride
            ride = await client.request_ride(
                pickup=pickup_location,
                dropoff=dropoff_location,
                ride_type=ride_type
            )
            
            return RideResult(
                ride_id=ride.id,
                driver=ride.driver,
                eta=ride.eta,
                price=estimate.price
            )
```

### Tier 2: Web Automation

**Best for**: Services without APIs but with web interfaces (Vezeeta, etc.)

```python
class VezeetaAutomation:
    """
    Web automation for Vezeeta booking.
    Uses Playwright for browser control.
    """
    
    async def book_appointment(
        self,
        specialty: str,
        preferred_date: date,
        location: str
    ) -> AppointmentResult:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to Vezeeta
            await page.goto("https://www.vezeeta.com")
            
            # Search for specialty
            await page.fill('[data-testid="specialty-search"]', specialty)
            await page.click('[data-testid="search-button"]')
            
            # Filter by location
            await page.select_option('[data-testid="location-filter"]', location)
            
            # Find available slots
            doctors = await page.query_selector_all('.doctor-card')
            
            for doctor in doctors:
                slots = await self._get_available_slots(doctor, preferred_date)
                if slots:
                    # Book first available slot
                    await self._book_slot(page, slots[0])
                    return AppointmentResult(
                        doctor=await doctor.text_content(),
                        time=slots[0],
                        confirmation_id=await self._get_confirmation(page)
                    )
            
            raise NoAvailableSlotError("No appointments available")
```

### Tier 3: Device Control

**Best for**: Native apps without web/API access

```kotlin
// Android Accessibility Service for device control
class ARIAAccessibilityService : AccessibilityService() {
    
    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                handleWindowChange(event)
            }
            AccessibilityEvent.TYPE_VIEW_CLICKED -> {
                handleClick(event)
            }
        }
    }
    
    fun performAction(action: AgentAction) {
        when (action) {
            is ClickAction -> {
                val node = findNodeByDescription(action.target)
                node?.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            }
            is TypeAction -> {
                val node = findNodeByDescription(action.target)
                val args = Bundle().apply {
                    putCharSequence(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        action.text
                    )
                }
                node?.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
            }
            is ScrollAction -> {
                performGlobalAction(GLOBAL_ACTION_SCROLL_FORWARD)
            }
        }
    }
}
```

---

## Data Flow

### Request Processing Pipeline

```
User Request
     │
     ▼
┌─────────────────┐
│  API Gateway    │ ─── Authentication, Rate Limiting
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PII Sanitizer  │ ─── Mask sensitive data before LLM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Intent Parser  │ ─── Classify request type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Task Planner   │ ─── Create execution plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ ─── Coordinate agent execution
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Agent 1│ │Agent 2│ │Agent 3│ │Agent N│
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │
    └────┬────┴─────────┴─────────┘
         │
         ▼
┌─────────────────┐
│   Aggregator    │ ─── Combine results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PII Restorer   │ ─── Restore masked values
└────────┬────────┘
         │
         ▼
    User Response
```

---

## State Management

### LangGraph State Machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    # User input
    user_message: str
    
    # Parsed intent
    intent: Optional[Intent]
    
    # Execution plan
    plan: Optional[ExecutionPlan]
    
    # Results from each agent
    agent_results: Annotated[dict, operator.or_]
    
    # Final response
    response: Optional[str]
    
    # Error tracking
    errors: List[Error]
    
    # Conversation history
    messages: List[Message]

def create_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("plan_tasks", plan_tasks_node)
    workflow.add_node("execute_calendar", calendar_agent_node)
    workflow.add_node("execute_transport", transport_agent_node)
    workflow.add_node("execute_medical", medical_agent_node)
    workflow.add_node("aggregate_results", aggregate_node)
    workflow.add_node("generate_response", response_node)
    
    # Define edges
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "plan_tasks")
    
    # Conditional routing based on plan
    workflow.add_conditional_edges(
        "plan_tasks",
        route_to_agents,
        {
            "calendar": "execute_calendar",
            "transport": "execute_transport",
            "medical": "execute_medical",
            "direct_response": "generate_response"
        }
    )
    
    # All agents lead to aggregation
    for agent in ["execute_calendar", "execute_transport", "execute_medical"]:
        workflow.add_edge(agent, "aggregate_results")
    
    workflow.add_edge("aggregate_results", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()
```

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: NETWORK SECURITY                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ • TLS 1.3 encryption                                      │ │
│  │ • API key authentication                                   │ │
│  │ • Rate limiting (100 req/min)                             │ │
│  │ • DDoS protection                                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Layer 2: APPLICATION SECURITY                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ • JWT token authentication                                 │ │
│  │ • Request validation & sanitization                        │ │
│  │ • CORS policy enforcement                                  │ │
│  │ • SQL injection prevention (parameterized queries)         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Layer 3: DATA SECURITY                                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ • PII detection & masking before LLM calls                 │ │
│  │ • AES-256 encryption at rest                               │ │
│  │ • Field-level encryption for sensitive data                │ │
│  │ • Secure credential storage (HashiCorp Vault)              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Layer 4: AGENT SECURITY                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ • Sandboxed execution environment                          │ │
│  │ • Action allowlisting                                      │ │
│  │ • Budget limits for financial actions                      │ │
│  │ • Human-in-the-loop for high-risk actions                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### PII Handling

```python
class PIISanitizer:
    """
    Detects and masks PII before sending to external LLMs.
    """
    
    PATTERNS = {
        "PHONE": r"\+?[\d\s\-()]{10,}",
        "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
        "SSN": r"\d{3}-\d{2}-\d{4}",
        "CREDIT_CARD": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
        "NAME": None  # Uses NER model
    }
    
    def sanitize(self, text: str) -> tuple[str, dict]:
        """
        Returns (sanitized_text, mapping_for_restoration)
        """
        mapping = {}
        sanitized = text
        
        for pii_type, pattern in self.PATTERNS.items():
            if pattern:
                matches = re.findall(pattern, text)
                for i, match in enumerate(matches):
                    placeholder = f"[{pii_type}_{i}]"
                    mapping[placeholder] = match
                    sanitized = sanitized.replace(match, placeholder)
        
        # NER for names
        entities = self.ner_model.extract(sanitized)
        for entity in entities:
            if entity.type == "PERSON":
                placeholder = f"[NAME_{len(mapping)}]"
                mapping[placeholder] = entity.text
                sanitized = sanitized.replace(entity.text, placeholder)
        
        return sanitized, mapping
    
    def restore(self, text: str, mapping: dict) -> str:
        """
        Restores original PII values.
        """
        restored = text
        for placeholder, original in mapping.items():
            restored = restored.replace(placeholder, original)
        return restored
```

---

## Next Steps

For implementation details, see:
- [API Reference](API_REFERENCE.md)
- [Agent Design Patterns](AGENT_DESIGN.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Security Best Practices](SECURITY.md)
]]>
