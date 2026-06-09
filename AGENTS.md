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
- **`tools.py`** — Pure data retrieval. Loads `_plant_db` and `_season_data` once at import time. `get_seasonal_conditions()` auto-detects the current season from `datetime.now().month` when no season is provided. `lookup_plant()` is a stub returning a not-found response.
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
- The agent loop must follow the Groq/OpenAI tool-calling protocol:
  1. Build messages: system prompt + history pairs + current user message.
  2. Call `client.chat.completions.create(model=LLM_MODEL, messages=messages, tools=TOOL_DEFINITIONS, tool_choice="auto")`.
  3. If `assistant_message.tool_calls` is truthy, append the assistant message, then append one `{"role": "tool", "tool_call_id": ..., "content": ...}` message per tool call after executing via `dispatch_tool()`.
  4. Re-call the LLM and repeat until there are no tool calls or `MAX_TOOL_ROUNDS` is reached.
- Always refer to `specs/system-design.md`, `specs/tool-functions-spec.md`, and `specs/agent-loop-spec.md` before changing `tools.py` or `agent.py`. They contain the authoritative design and milestone instructions.
