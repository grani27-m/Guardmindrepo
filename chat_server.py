"""
GuardMind Chat Server — Real AI assistant with LBA loop protection.

HOW IT WORKS:
- All messages go to Groq LLM for a natural, conversational response.
- A simple keyword+pattern router checks if the user is asking to
  LOOK UP a specific item. If yes, it ALSO runs the LBA guardrail.
- The guardrail only fires on genuine repeated-tool-call loops.
- "hi", "explain LBA", anything conversational → always answered naturally.
"""

from __future__ import annotations
import sys, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_groq import ChatGroq

from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS
from lba_guardrail.agents.interactive_agent import InteractiveLookupAgent, KNOWN_ITEMS

app = Flask(__name__, static_folder=str(ROOT / "demo" / "chat_ui"), static_url_path="")
CORS(app)

TAPE_LENGTH = 4
MAX_STEPS   = 20

_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

# ── System personality ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are GuardMind, a friendly and knowledgeable AI assistant.
You were built as a university Theory of Computation (TOC) project to demonstrate
how a Linear Bounded Automaton (LBA) can mathematically prevent AI agents from
getting stuck in infinite loops.

You can answer ANY question — greetings, explanations, coding help, general knowledge.
You also have a product/invoice lookup capability. However, the system handles lookups automatically. 
Do NOT output tool calls or JSON. Just respond conversationally and confirm you will look it up.

Known items in your database: product-101, product-202, invoice-555, employee-007, lba-paper.

Be warm, concise, and educational. When asked about TOC, LBA, Pigeonhole Principle,
or how your guardrail works, give clear and accurate explanations."""


# ── Intent detection (keyword-based, no extra LLM call) ────────────────────
LOOKUP_TRIGGERS = [
    "find", "search for", "search", "look up", "lookup", "get me",
    "retrieve", "fetch", "check", "show me", "what is", "what's",
]

# Matches actual item IDs like product-101, product 101, invoice-555, etc.
ITEM_PATTERN = re.compile(
    r'\b(product[-\s]\d+|invoice[-\s]\d+|employee[-\s]\d+|lba[-\s]paper)\b',
    re.IGNORECASE
)


def detect_lookup(message: str) -> tuple[bool, str | None]:
    """
    Returns (is_lookup, query_term).
    Uses simple keyword + pattern matching — no LLM, 100% reliable.
    """
    # 1. Does the message mention a known item ID pattern?
    match = ITEM_PATTERN.search(message)
    if match:
        # Normalize spaces to hyphens so dictionary lookups work
        query = match.group(0).lower().replace(" ", "-")
        return True, query

    # 2. Does it have a lookup keyword AND something to look up?
    msg_lower = message.lower()
    for trigger in LOOKUP_TRIGGERS:
        if trigger in msg_lower:
            idx = msg_lower.index(trigger)
            after = message[idx + len(trigger):].strip(" ?.,!")
            if after and len(after) > 1:
                return True, after
    
    return False, None


def chat_with_llm(user_message: str, history: list[dict]) -> str:
    """Plain Groq conversation — always works for any message."""
    messages = [("system", SYSTEM_PROMPT)]
    for turn in history[-8:]:
        messages.append(("human", turn.get("user", "")))
        messages.append(("ai",    turn.get("assistant", "")))
    messages.append(("human", user_message))
    try:
        resp = _llm.invoke(messages)
        return resp.content.strip()
    except Exception as e:
        return f"I'm having trouble right now. Please try again. (Error: {e})"


def run_lookup(query: str) -> dict:
    """Run lookup agent under LBA guardrail watch."""
    agent = InteractiveLookupAgent(query)
    guardrail = LBAGuardrail(tape_length=TAPE_LENGTH)
    steps_log = []
    result = RAN_OUT_OF_STEPS
    final_step = MAX_STEPS
    halt_reason = None

    for step in range(1, MAX_STEPS + 1):
        state = agent.get_state()
        obs   = agent.act()
        display = agent.last_display_text


        entry = {"step": step, "display": display, "observation": obs,
                 "tape": None, "configs_seen": None}

        if agent.is_done(obs):
            result = SUCCESS
            final_step = step
            steps_log.append(entry)
            break

        ok = guardrail.step(state, obs)
        entry["tape"]        = list(guardrail.tape.snapshot())
        entry["configs_seen"] = len(guardrail.seen_configurations)
        steps_log.append(entry)

        if not ok:
            result = HALTED_BY_LBA
            final_step = step
            halt_reason = guardrail.halt_reason
            break

    return {
        "steps": steps_log,
        "steps_taken": final_step,
        "halted_by_lba": result == HALTED_BY_LBA,
        "halt_reason": halt_reason,
        "result": result,
        "query": query,
        "found_value": agent.last_display_text if result == SUCCESS else None,
    }


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    message = data.get("query", "").strip()
    history = data.get("history", [])
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Step 1: always get a natural LLM reply
    ai_reply = chat_with_llm(message, history)

    # Step 2: also check if this is a lookup task
    is_lookup, query = detect_lookup(message)

    if is_lookup:
        lookup_result = run_lookup(query)
        if lookup_result["halted_by_lba"]:
            # LBA fired — the AI reply becomes context, guardrail card shown
            return jsonify({
                "type": "guardrail",
                "reply": ai_reply,
                "halted_by_lba": True,
                "halt_reason": lookup_result["halt_reason"],
                "steps": lookup_result["steps"],
                "steps_taken": lookup_result["steps_taken"],
                "query": query,
            })
        elif lookup_result["result"] == SUCCESS:
            val = lookup_result["found_value"].replace("FOUND: ", "")
            return jsonify({
                "type": "lookup_success",
                "reply": f"{ai_reply}\n\n✅ **Found:** {val}",
                "halted_by_lba": False,
                "query": query,
            })
        else:
            return jsonify({
                "type": "chat",
                "reply": ai_reply,
                "halted_by_lba": False,
            })

    # Pure conversation
    return jsonify({
        "type": "chat",
        "reply": ai_reply,
        "halted_by_lba": False,
    })


@app.route("/api/known_items")
def known_items():
    return jsonify({"items": list(KNOWN_ITEMS.keys())})


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  GuardMind Chat API  —  http://localhost:5050")
    print("=" * 55 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False)
