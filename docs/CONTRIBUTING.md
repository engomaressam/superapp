<![CDATA[# Contributing to ARIA

Thank you for your interest in contributing to ARIA! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/superapp.git
   cd superapp
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   python -m spacy download en_core_web_sm
   ```

3. **Mobile Setup**
   ```bash
   cd mobile
   npm install
   ```

4. **Start Services**
   ```bash
   docker-compose up -d postgres redis
   cd backend && uvicorn app.main:app --reload
   ```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(agents): add reminder agent with recurring support
fix(transport): handle Uber API rate limits
docs(readme): update installation instructions
```

### Pull Request Process

1. Create feature branch from `main`
2. Make changes and test locally
3. Update documentation if needed
4. Submit PR with description of changes
5. Address review feedback
6. Squash and merge when approved

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Format with Black (`black .`)
- Sort imports with isort (`isort .`)
- Lint with Ruff (`ruff check .`)

```python
# Good
async def get_ride_estimate(
    pickup: Location,
    dropoff: Location,
    ride_types: list[str] = None
) -> dict[str, Any]:
    """Get ride price estimates."""
    ...

# Bad
def get_ride_estimate(pickup, dropoff, ride_types=None):
    ...
```

### TypeScript (Mobile)

- Use TypeScript strict mode
- Follow ESLint rules
- Format with Prettier

```typescript
// Good
interface RideEstimate {
  rideType: string;
  price: number;
  eta: number;
}

async function getRideEstimate(
  pickup: Location,
  dropoff: Location
): Promise<RideEstimate[]> {
  // ...
}

// Bad
async function getRideEstimate(pickup, dropoff) {
  // ...
}
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Writing Tests

```python
import pytest
from app.agents.transport import TransportAgent

@pytest.mark.asyncio
async def test_transport_agent_can_handle_ride_task():
    agent = TransportAgent()
    task = Task(id="test", type="book_ride", parameters={})
    
    assert await agent.can_handle(task) == True

@pytest.mark.asyncio
async def test_transport_agent_get_estimate():
    agent = TransportAgent()
    result = await agent._get_estimate(
        pickup={"lat": 30.0, "lng": 31.0},
        dropoff="Destination",
        ride_types=["UberX"]
    )
    
    assert "estimates" in result
    assert len(result["estimates"]) > 0
```

## Adding New Agents

1. Create agent file in `backend/app/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods:
   - `_initialize_tools()`
   - `can_handle()`
   - `plan()`
4. Add to `__init__.py`
5. Register in orchestrator

Example:
```python
class NewAgent(BaseAgent):
    name = "NewAgent"
    description = "Handles new functionality"
    
    SUPPORTED_TASKS = ["task_type_1", "task_type_2"]
    
    def _initialize_tools(self):
        self.tools = [
            Tool(
                name="tool_name",
                description="What this tool does",
                parameters={"param": "type"},
                function=self._tool_function
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: dict) -> list[dict]:
        # Create execution plan
        return [{"tool": "tool_name", "parameters": {...}}]
    
    async def _tool_function(self, param: str) -> dict:
        # Tool implementation
        return {"result": "..."}
```

## Documentation

- Keep README up to date
- Document new features in `/docs`
- Add docstrings to all public functions
- Include examples in documentation

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing! 🙏
]]>
