from duckduckgo_search import DDGS
from langchain_groq import ChatGroq
import os
from .base_agent import Agent
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

try:
    _llm = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )
except Exception:
    _llm = None

def real_web_search(query: str) -> str:
    """A REAL search tool -- no scripted failure. It can genuinely
    return nothing useful for a sufficiently obscure/nonsensical query."""
    try:
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return "NO_RESULTS"
        return "RESULTS_FOUND"
    except Exception:
        return "SEARCH_ERROR"


class RealSearchAgent(Agent):
    def __init__(self, goal_query: str):
        self.goal_query = goal_query
        self.last_observation = "START"
        self.last_display_text = "START"
        self.attempts = 0

    def get_state(self) -> str:
        # No step counter -- same fix as before.
        return f"query={self.goal_query}|last={self.last_observation}"

    def act(self) -> str:
        self.attempts += 1
        # Ask the LLM to reformulate the query each time it fails --
        # this is what makes it a genuine AGENT rather than a static
        # retry loop: the LLM decides HOW to retry, we don't script it.
        if self.attempts == 1:
            search_query = self.goal_query
        else:
            if _llm:
                reformulated = _llm.invoke(
                    f"The web search for '{self.goal_query}' found nothing. "
                    f"Suggest a different, short search query to try instead. "
                    f"Reply with ONLY the new query text, nothing else."
                )
                search_query = reformulated.content.strip().strip("'\"")
            else:
                search_query = self.goal_query + " retry"

        result = real_web_search(search_query)
        self.last_display_text = f"searched '{search_query}' -> {result}"
        self.last_observation = result
        return result

    def is_done(self, observation: str) -> bool:
        return observation == "RESULTS_FOUND"
