# Plant Advisor — Agent Context

This document describes the codebase for AI coding agents. Everything below is derived directly from the files in this repository.

---

## Project Overview

Plant Advisor is a conversational agent that helps users care for houseplants. It is a small Python application built around a Groq LLM (`llama-3.3-70b-versatile`) using function calling. The UI is implemented with Gradio. The agent has two local data tools:

- `lookup_plant(plant_name)` — retrieves care information from `data/plants.json`.
- `get_seasonal_conditions(season)` — retrieves seasonal guidance from `data/seasons.json`.

The repository is a starter lab project. The Gradio UI, configuration, tool schemas, system prompt, and data files are complete, but the core tool logic and agent loop are intentionally left as TODOs for two milestones:

- **Milestone 1** — implement `lookup_plant()` and review `get_seasonal_conditions()` in `tools.py`.
- **Milestone 2** — implement `run_agent()` in `agent.py` to orchestrate the tool-calling loop.
- **Milestone 3** — graceful degradation and agent loop improvements.

---

## Agent Build Responsibilities (VEGA vs Hayden)

To align with development rules, tasks are divided between **VEGA** (the planning build) and **Hayden** (the coding build):

### VEGA (Planning Build)
VEGA is responsible for research, design, planning, and architectural decisions. Its tasks include:
- Analyzing the system specs (`specs/system-design.md`, `specs/tool-functions-spec.md`, and `specs/agent-loop-spec.md`).
- Designing implementation plans (`implementation_plan.md`) for each milestone.
- Reviewing system behavior, identifying edge cases, and proposing strategies for error handling / graceful degradation.
- Researching API dependencies, schemas, and configurations.

### Hayden (Coding Build)
Hayden is responsible for code execution, writing implementation files, and bug fixing. Its tasks include:
- Implementing the core data-retrieval functions (e.g., `lookup_plant()` in `tools.py` for **Milestone 1**).
- Reviewing and editing helper code (e.g., `get_seasonal_conditions()` in `tools.py` for **Milestone 1**).
- Implementing the tool-calling and agent orchestration loops (e.g., `run_agent()` in `agent.py` for **Milestone 2**).
- Writing code for graceful degradation and agent loop improvements (for **Milestone 3**).
- Writing and running tests or manual validation scripts, and diagnosing compiler/runtime errors.

---

High-level flow:

```
User ↔ app.py (Gradio UI) ↔ run_agent() in agent.py ↔ Groq LLM
                                  ↓
                    dispatch_tool() → tools.py → data/*.json
```

---

## Technology Stack

- **Language:** Python 3
- **UI:** Gradio ≥ 5.25.0
- **LLM API:** Groq (`groq` SDK ≥ 1.1.2), model `llama-3.3-70b-versatile`
- **Environment:** `python-dotenv` for loading `.env`
- **HTTP:** `requests` (available in environment, not directly used by the core app)
- **Data:** Local JSON files (`data/plants.json`, `data/seasons.json`)

---

## Project Structure

```
├── app.py              # Gradio UI (complete — do not modify)
├── agent.py            # Tool definitions, system prompt, dispatch_tool(), run_agent() (TODO)
├── tools.py            # lookup_plant() (TODO) and get_seasonal_conditions() (pre-implemented)
├── config.py           # Loads GROQ_API_KEY, LLM_MODEL, MAX_TOOL_ROUNDS, DATA_PATH
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file (copy to .env and add your Groq key)
├── .gitignore          # Excludes .env, .venv/, __pycache__/, *.pyc, .DS_Store
├── data/
│   ├── plants.json     # 15-plant database keyed by lowercase slugs
│   └── seasons.json    # Seasonal care guidance for spring/summer/fall/winter
└── specs/
    ├── system-design.md
    ├── tool-functions-spec.md
    └── agent-loop-spec.md
```

### Module Responsibilities

- **`config.py`** — Centralizes configuration. Loads `GROQ_API_KEY` from the environment, defines `LLM_MODEL`, caps agent loops with `MAX_TOOL_ROUNDS = 5`, and sets `DATA_PATH = "./data"`.
- **`tools.py`** — Pure data retrieval. Loads `_plant_db` and `_season_data` once at import time.
  - `get_seasonal_conditions(season)` auto-detects the current season from `datetime.now().month` when no season is provided, returning seasonal conditions and setting the `detected_season` flag.
  - `lookup_plant(plant_name)` must normalize the input (strip whitespace, convert to lowercase) and perform case-insensitive name matching against three attributes: the slug key, `display_name`, and the `aliases` list in `data/plants.json`. If found, it returns `{"found": True, "plant": {...}}`. If not found, it returns `{"found": False, "message": "..."}` with a helpful, descriptive message (not just "not found") to help the LLM form a response.
- **`agent.py`** — Defines `TOOL_DEFINITIONS` in the Groq/OpenAI tool-calling format, the `SYSTEM_PROMPT`, and `dispatch_tool()` which routes tool calls to `tools.py`. `run_agent()` is a stub that returns a placeholder message until Milestone 2 is completed.
- **`app.py`** — Builds the Gradio interface, loads the plant list for the sidebar, seeds example questions, and calls `run_agent(message, history)` on every turn. The history format is a list of `[user_message, assistant_message]` pairs.

---

## Build and Run Commands

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=<your key from console.groq.com>
```

4. Run the app:

```bash
python app.py
```

This launches the Gradio interface in your default browser.

There is no separate build step, no package manager config (e.g., no `pyproject.toml`, `package.json`, or `Cargo.toml`), and no CI/CD pipeline defined in the repo.

---

## Code Style and Conventions

- **Python style:** Standard Python with type hints in function signatures (e.g., `plant_name: str -> dict`). No explicit formatter or linter config is present.
- **Docstrings:** Functions use multi-line docstrings to describe contracts, inputs/outputs, and TODOs. Read them carefully before editing.
- **Constants:** Global configuration lives in `config.py` and is imported elsewhere. Data paths should be constructed with `os.path.join(config.DATA_PATH, ...)`, as shown in `app.py` and `tools.py`.
- **Data caching:** JSON data files are loaded once at module import time (`_plant_db`, `_season_data`). Avoid reloading them on every request.
- **Tool dispatch logging:** `dispatch_tool()` prints each tool call and a truncated result to stdout. Keep this behavior intact for visibility.
- **OpenAI-compatible tool schema:** Tool definitions live in `agent.py` as a list of `{"type": "function", "function": {...}}` dicts.
- **Do not modify `app.py`:** The README and spec mark it as complete. Any required behavior changes should be handled in `tools.py` or `agent.py`.

---

## Testing Instructions

There is no automated test suite in this repository. The intended way to verify the implementation is:

1. Run the app with `python app.py`.
2. Try example questions from the Gradio UI:
   - "How do I care for my pothos?"
   - "How often should I water my snake plant in winter?"
   - "How do I care for my string of pearls?" (not in the database — tests graceful degradation)
3. Inspect the terminal output for tool calls and results.
4. Validate `tools.py` manually in a Python REPL:

```python
from tools import lookup_plant, get_seasonal_conditions

lookup_plant("devil's ivy")
lookup_plant("SNAKE PLANT")
get_seasonal_conditions(None)
get_seasonal_conditions("winter")
```

The `specs/` files contain explicit test prompts and blank fields for students to fill in after implementation.

---

## Security Considerations

- **API key handling:** The Groq API key is loaded from `GROQ_API_KEY` in `.env`. `.env` is listed in `.gitignore` and must never be committed.
- **Loop safety:** `MAX_TOOL_ROUNDS = 5` in `config.py` caps the number of tool-calling iterations to prevent runaway loops.
- **Input handling:** User input flows through the Gradio UI to the LLM and then into tool arguments. Tool functions should defensively strip whitespace and normalize case (see `lookup_plant()` docstring), but there is no broader input sanitization framework in place.
- **Local-only data:** No user data is persisted; all plant and season data is static JSON bundled with the repo.
- **No authentication:** The Gradio app is local by default, but `launch()` is not configured with `share=False` explicitly; review Gradio defaults if exposing to a network.

---

## Useful Context for Agents

- The plant database keys are lowercase slugs (e.g., `pothos`, `snake_plant`, `fiddle_leaf_fig`). Each entry contains `display_name`, `scientific_name`, `aliases`, watering/light/humidity/temperature guidance, common issues, and seasonal notes.
- **Agent Loop and Message Ordering:** The agent loop must follow the Groq/OpenAI tool-calling protocol:
  1. Build messages: system prompt + history pairs + current user message.
  2. Call `client.chat.completions.create(model=LLM_MODEL, messages=messages, tools=TOOL_DEFINITIONS, tool_choice="auto")`.
  3. If the response contains `tool_calls` (assistant requesting tools):
     - **CRITICAL ORDER:** You must append the assistant message (containing the `tool_calls` request) to the messages list **BEFORE** appending any tool result messages. Appending in the wrong order will cause API errors.
     - For each tool call, execute the function via `dispatch_tool()`, and append a tool result message: `{"role": "tool", "tool_call_id": ..., "name": ..., "content": ...}` referencing the corresponding `tool_call_id`.
     - Go back to step 1 (re-call the LLM) up to `MAX_TOOL_ROUNDS` iterations.
  4. If the response contains `content` (final text response): Extract the final text content from `response.choices[0].message.content` and return it.
- **Graceful Degradation for Unknown Plants:** When a user asks about a plant not present in `plants.json`, the lookup tool returns `{"found": False, "message": "..."}`. The agent must:
  - Acknowledge that the plant is not in its database.
  - **NEVER** hallucinate or invent specific care instructions for that plant.
  - Offer general advice (e.g., general tropical plant care guidelines) or a helpful redirection. This behavior should be reinforced via instructions in the system prompt in `agent.py` and the not-found message structure.
- **Optional Challenges:**
  - **`get_plant_list()` Tool:** You can implement a third tool returning all plants and their difficulty levels, adding it to tool definitions and dispatch logic to support questions like "what plants do you know about?".
  - **Conversation Memory:** Maintain state across turns, identifying previously discussed plants to tailor recommendations.
- Always refer to `specs/system-design.md`, `specs/tool-functions-spec.md`, and `specs/agent-loop-spec.md` before changing `tools.py` or `agent.py`. They contain the authoritative design and milestone instructions.
