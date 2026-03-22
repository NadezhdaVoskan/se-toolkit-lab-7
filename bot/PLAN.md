# LMS Telegram Bot — Development Plan

## Architecture Overview

This bot is built with **separation of concerns**: handler logic is independent of Telegram. Commands are pure functions that accept input and return text. This design allows:

1. **Testability**: Handlers can be called directly from CLI (`--test` mode) without Telegram
2. **Reusability**: Same handler works from tests, CLI, and Telegram layer
3. **Maintainability**: Bot logic is independent of transport (Telegram, API, etc.)

### Layers

- **Handlers** (`bot/handlers/commands.py`): Pure functions, no side effects, return strings
- **Router** (`bot/bot.py`): Maps command strings to handlers
- **Transport** (`bot/bot.py` Telegram mode): Telegram bot startup (implemented in Task 2)
- **Services** (`bot/services/`): API clients for backend and LLM (Task 2+)
- **Config** (`bot/config.py`): Environment variable loading, no hardcoding

## Task-by-Task Implementation

### Task 1: Plan and Scaffold (this task)

Create the project skeleton with:

- Handler layer with placeholder commands (`/start`, `/help`, `/health`, `/labs`, `/scores`)
- CLI entry point with `--test` mode for offline testing
- Configuration system from environment variables
- No Telegram connection needed for testing

**Acceptance**: `uv run bot.py --test "/start"` prints welcome message, exits 0.

### Task 2: Backend Integration

Replace placeholders with real API calls:

- `/health` → queries `GET /status` (new endpoint or existing)
- `/labs` → queries `GET /items/` to list labs
- `/scores <lab>` → queries `GET /analytics/<lab>` for detailed scores
- Add error handling: if backend is down, show friendly message

Implement `bot/services/lms_client.py`:

- HTTP client using `httpx`
- Methods: `get_labs()`, `get_scores(lab_id)`, `get_status()`
- Bearer token auth: `Authorization: Bearer {LMS_API_KEY}`

**Acceptance**: All commands return real data from backend.

### Task 3: Intent-Based Natural Language Routing

Accept plain-text questions and route them to the right data fetch:

- "What labs do I have available?" → `/labs`
- "Show me my scores for lab-04" → `/scores lab-04`
- "Is the system up?" → `/health`

Implement `bot/services/llm_client.py`:

- Connect to Qwen Code API (or OpenRouter) at `LLM_API_BASE_URL`
- Define tools: `get_labs`, `get_scores`, `get_health`
- System prompt: explain what the bot can do and which tools are available
- LLM decides which tool to call based on user intent
- Execute the tool and return results

Implement `bot/handlers/intent_router.py`:

- Takes plain text input
- Calls LLM with tool descriptions
- LLM returns tool name + arguments
- Execute the tool and return result

**Acceptance**: `uv run bot.py --test "what labs are available"` routes to LLM, LLM calls `get_labs` tool, returns lab list.

### Task 4: Containerize and Deploy

Create `bot/Dockerfile`:

- Multi-stage build: dependencies in one layer, app in another
- Runs `uv run bot.py` (Telegram mode)
- Reads config from `.env.bot.secret` mounted at runtime

Update `docker-compose.yml`:

- Add `bot` service
- Mount `.env.bot.secret` with `env_file:`
- Depends on `backend` service
- Port 8000 for bot webhook (optional for polling)

Deploy on VM:

- Same setup as local — `docker compose up -d`
- Bot process picks up `.env.bot.secret` from VM host
- Bot connects to backend at `http://backend:42002` (Docker network DNS)

## Summary

| Task | Focus | Key Files |
|------|-------|-----------|
| 1 | Scaffold + test mode | bot.py, handlers/, config.py, PLAN.md |
| 2 | Backend integration | services/lms_client.py, real API calls |
| 3 | LLM + intent routing | services/llm_client.py, handlers/intent_router.py |
| 4 | Containerization | Dockerfile, docker-compose.yml, deploy |

Each task adds real functionality while keeping tests passing and handlers testable.
