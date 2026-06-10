import json
from groq import Groq, BadRequestError
from config import GROQ_API_KEY, LLM_MODEL, MAX_TOOL_ROUNDS
from tools import lookup_plant, get_seasonal_conditions, get_plant_list

_client = Groq(api_key=GROQ_API_KEY)

# ──────────────────────────────────────────────
# Tool definitions
#
# These are the schemas that tell the LLM what tools are available and how to
# call them. The LLM reads these descriptions and decides when (and how) to use
# each tool. They're already complete — your job is to implement the tool
# functions in tools.py and the agent loop below.
# ──────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_plant",
            "description": (
                "Look up care information for a specific houseplant by name. "
                "Returns detailed watering, light, humidity, and temperature requirements. "
                "Use this whenever the user asks about a specific plant."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plant_name": {
                        "type": "string",
                        "description": "The plant name to look up. Can be a common name, scientific name, or nickname (e.g., 'pothos', 'devil's ivy', 'Monstera deliciosa').",
                    }
                },
                "required": ["plant_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_seasonal_conditions",
            "description": (
                "Get seasonal care adjustments for houseplants. "
                "Returns guidance on watering, fertilizing, light, and pests for the current or specified season. "
                "Use this when a user asks a season-specific question, or to complement plant care advice with seasonal context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "season": {
                        "type": "string",
                        "description": "The season to get care conditions for. If omitted, the current season is detected automatically.",
                        "enum": ["spring", "summer", "fall", "winter"],
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_plant_list",
            "description": (
                "Get a list of all houseplants currently supported in the database, including their difficulty level. "
                "Use this when the user asks what plants you know about, what plants are supported, or wants a list of options."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# ──────────────────────────────────────────────
# System prompt
# ──────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a Master Botanist and Houseplant Care Specialist. Your mission is to provide highly accurate, practical, and structured plant care advice by leveraging your specialized local database.\n\n"
    "When a user asks a question, follow this reasoning process:\n"
    "Step 1: Analyze. Identify the specific plant(s) and any environmental context (like season, light issues).\n"
    "Step 2: Retrieve. Use your available tools to look up the plant's profile and seasonal conditions before answering.\n"
    "Step 3: Synthesize. Combine the retrieved tool results into a cohesive, actionable plan.\n\n"
    "Format your final response beautifully:\n"
    "- Use Markdown headings (###) to separate different care aspects (e.g., Watering, Light).\n"
    "- Use bullet points for easy scanning.\n"
    "- **Bold** key terms and measurements.\n"
    "- Maintain a warm, encouraging, and professional tone.\n\n"
    "CRITICAL CONSTRAINTS (Self-Correction):\n"
    "1. If a lookup tool returns found: false, you MUST explicitly state the plant is not in your database.\n"
    "2. NEVER guess, invent, or hallucinate specific care parameters for unsupported plants. Instead, offer general advice based on the plant family.\n"
    "3. Always cite your data implicitly (e.g., 'According to your plant\\'s profile...')."
)

# ──────────────────────────────────────────────
# Tool dispatch
#
# This is already complete. It routes tool calls from the LLM to the actual
# Python functions in tools.py, and returns results as JSON strings (which is
# what the Groq API expects for tool results).
# ──────────────────────────────────────────────

def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    """Route a tool call to the correct function and return the result as a JSON string."""
    print(f"  → Tool call: {tool_name}({tool_args})")
    if tool_name == "lookup_plant":
        result = lookup_plant(tool_args["plant_name"])
    elif tool_name == "get_seasonal_conditions":
        result = get_seasonal_conditions(tool_args.get("season"))
    elif tool_name == "get_plant_list":
        result = get_plant_list()
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    print(f"  ← Result: {json.dumps(result)[:120]}{'...' if len(json.dumps(result)) > 120 else ''}")
    return json.dumps(result)


# ──────────────────────────────────────────────
# Agent loop
# ──────────────────────────────────────────────

def run_agent(user_message: str, history: list) -> str:
    """
    Run the plant care agent for one user turn and return its response.
    """
    # Handle both Gradio history formats:
    #   Old format: list of [user_msg, assistant_msg] pairs
    #   Gradio 5.x type="messages" format: list of {"role": ..., "content": ...} dicts
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history:
        if isinstance(item, dict):
            # Gradio 5.x messages format — pass through directly, skipping tool/system roles
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        else:
            # Old pair format: [user_msg, assistant_msg]
            user_msg, assistant_msg = item
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
                
    messages.append({"role": "user", "content": user_message})

    rounds = 0
    while rounds < MAX_TOOL_ROUNDS:
        try:
            response = _client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
        except BadRequestError as e:
            print(f"  ✗ Groq BadRequestError: {e}")
            return (
                "I had trouble processing that request — the model generated an "
                "invalid function call. Could you try rephrasing your question?"
            )
        
        assistant_message = response.choices[0].message
        
        if not assistant_message.tool_calls:
            return assistant_message.content
            
        messages.append(assistant_message)
        
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_result = dispatch_tool(tool_name, tool_args)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_result,
            })
            
        rounds += 1
        
    return "I'm sorry, I needed to look up too much information to answer that completely. Could you try asking a more specific question?"
