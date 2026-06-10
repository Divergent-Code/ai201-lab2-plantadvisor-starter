# Plant Advisor — AI201 Lab 2 Completed

A conversational agent that helps users care for their houseplants. Ask it anything about a plant in its database and it will look up the care requirements, check the current seasonal context, and give you specific, grounded advice.

The app is built and running. The agent has been fully implemented, including graceful fallback for unknown plants and a `get_plant_list` tool.

---

## Setup

**1. Fork and clone this repo.**

**2. Create and activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
# or: .venv\Scripts\activate   # Windows
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Add your Groq API key.** Copy `.env.example` to `.env` and paste in your key from [console.groq.com](https://console.groq.com).

**5. Run the app:**

```bash
python run.py
```

Plant Advisor will open in your browser and is fully functional.

---

## Project Structure

```
ai201-lab2-plantadvisor-starter/
├── app.py              ← Gradio UI (complete — do not modify)
├── run.py              ← Run this script to launch the app (fixes Gradio version issues)
├── config.py           ← API keys and settings (complete)
├── agent.py            ← Tool definitions + run_agent() (completed)
├── tools.py            ← lookup_plant(), get_seasonal_conditions(), get_plant_list() (completed)
├── data/
│   ├── plants.json     ← 15-plant database (complete)
│   └── seasons.json    ← Seasonal care data (complete)
├── specs/
│   ├── system-design.md        ← Start here
│   ├── tool-functions-spec.md  ← Complete before Milestone 1
│   └── agent-loop-spec.md      ← Complete before Milestone 2
└── requirements.txt
```

## Documentation

All specifications (`system-design.md`, `tool-functions-spec.md`, `agent-loop-spec.md`) have been completed and verified as part of the implementation process.
