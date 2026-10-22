"""LLM-backed agent adapter for real Groq integration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .base_agent import Agent

# Load .env from the project root (two levels up from this file)
_env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

try:
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover - optional dependency fallback
    ChatGroq = None


GROQ_MODEL = "openai/gpt-oss-20b"


class LLMAgent(Agent):
    def __init__(self, goal: str, api_key: str | None = None):
        self.goal = goal
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.last_observation = "START"
        self._step = 0

    def get_state(self) -> str:
        return f"goal={self.goal}|last={self.last_observation}"

    def act(self) -> str:
        self._step += 1

        # --- Gate 1: api_key present and not the test sentinel ---
        if not self.api_key or self.api_key == "fake-key":
            print(
                f"  [step={self._step}] PATH=FALLBACK  reason=no_api_key_or_test_sentinel"
            )
            fallback_messages = [
                "ERROR: tool returned no results",
                "ERROR: retry loop detected",
                "ERROR: tool call is repeating",
            ]
            self.last_observation = fallback_messages[(self._step - 1) % len(fallback_messages)]
            return self.last_observation

        # --- Gate 2: langchain_groq imported successfully ---
        if ChatGroq is None:
            print(
                f"  [step={self._step}] PATH=FALLBACK  reason=langchain_groq_import_failed"
            )
            fallback_messages = [
                "ERROR: tool returned no results",
                "ERROR: retry loop detected",
                "ERROR: tool call is repeating",
            ]
            self.last_observation = fallback_messages[(self._step - 1) % len(fallback_messages)]
            return self.last_observation

        # --- Gate 3: actual Groq HTTP call ---
        print(
            f"  [step={self._step}] PATH=GROQ_API  model={GROQ_MODEL}  "
            f"key=...{self.api_key[-6:]}  -> calling API..."
        )
        try:
            llm = ChatGroq(
                model=GROQ_MODEL,
                temperature=0,
                groq_api_key=self.api_key,
            )
            prompt = "Return one short retry message for a failing tool call in a stuck agent loop."
            response = llm.invoke(prompt)
            self.last_observation = str(response.content).strip() or "ERROR: llm retry"
            print(f"  [step={self._step}] GROQ_RESPONSE -> {self.last_observation!r}")
            return self.last_observation
        except Exception as exc:
            print(f"  [step={self._step}] GROQ_ERROR    -> {exc}")
            self.last_observation = "ERROR: llm request failed"
            return self.last_observation

    def is_done(self, observation: str) -> bool:
        return "SUCCESS" in observation.upper()
