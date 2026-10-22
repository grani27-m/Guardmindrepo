"""
Interactive knowledge-base lookup agent using the real project classes.

The CANONICAL observation ("FOUND" / "NOT_FOUND") is what the guardrail
sees on the tape — NEVER the raw LLM text. This is intentional:
raw Groq phrasing varies slightly per call which would make every
configuration unique and defeat the LBA detection (the exact bug fixed
earlier in llm_agent.py).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .base_agent import Agent

# Load .env from the project root (4 levels up: agents -> lba_guardrail -> src -> root)
_env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

try:
    from langchain_groq import ChatGroq
    _llm = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )
except Exception:  # pragma: no cover
    _llm = None


# Known items the agent can resolve immediately.
# Expand this list for demo purposes — any query NOT in here will loop.
KNOWN_ITEMS: dict[str, str] = {
    "product-101": "Wireless Mouse -- $19.99, in stock",
    "product-202": "Mechanical Keyboard -- $59.99, in stock",
    "invoice-555": "Invoice #555 -- Paid on 2026-03-01",
    "employee-007": "James Bond -- Security Dept, active",
    "lba-paper": "LBA Guardrail paper -- Phase 3 report, TRL 3",
}


def generate_retry_message(query: str) -> str:
    """Call Groq to produce a natural-language retry sentence.

    The return value is shown to the HUMAN but never enters the guardrail tape.
    The guardrail always receives the canonical 'NOT_FOUND' string.
    """
    if _llm is not None:
        try:
            response = _llm.invoke(
                f"A lookup for '{query}' failed. In one short sentence, "
                f"say you'll retry the search."
            )
            return str(response.content).strip()
        except Exception as exc:
            return f"Retrying lookup for {query}... (fallback: {exc})"
    return f"Retrying lookup for {query}... (no LLM available)"


class InteractiveLookupAgent(Agent):
    """
    Looks up `query` in KNOWN_ITEMS.

    - Found     -> observation = "FOUND"   -> is_done() True  -> SUCCESS in 1 step
    - Not found -> calls Groq for a retry message (display only),
                   observation = "NOT_FOUND" (canonical, tape-safe)
                -> guardrail detects repeated (state, tape) and fires HALTED_BY_LBA
    """

    def __init__(self, query: str) -> None:
        self.query = query.strip().lower()
        self.last_observation = "START"    # canonical — used by the guardrail
        self.last_display_text = "START"   # human-readable — shown in the demo

    def get_state(self) -> str:
        # NOTE: no step counter here — that was the bug fixed in llm_agent.py.
        return f"query={self.query}|last={self.last_observation}"

    def act(self) -> str:
        found = KNOWN_ITEMS.get(self.query)
        if found:
            self.last_display_text = f"FOUND: {found}"
            self.last_observation = "FOUND"
        else:
            # Real Groq call — generates natural retry text for the human.
            # The guardrail ONLY sees the canonical "NOT_FOUND" below.
            self.last_display_text = generate_retry_message(self.query)
            self.last_observation = "NOT_FOUND"

        return self.last_observation  # canonical value goes to the tape

    def is_done(self, observation: str) -> bool:
        return observation == "FOUND"
