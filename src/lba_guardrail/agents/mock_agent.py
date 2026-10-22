"""Deterministic offline agents for scheduled demos and tests."""

from .base_agent import Agent


class SolvableTaskAgent(Agent):
    def __init__(self, goal: str = "fetch_and_validate_report"):
        self.goal = goal
        self._steps = 0
        self.last_observation = "START"

    def get_state(self) -> str:
        return f"goal={self.goal}|step={self._steps}|last={self.last_observation}"

    def act(self) -> str:
        self._steps += 1
        if self._steps == 1:
            self.last_observation = "Querying source"
            return "Querying source"
        if self._steps == 2:
            self.last_observation = "Data retrieved"
            return "Data retrieved"
        self.last_observation = "SUCCESS: report validated"
        return "SUCCESS: report validated"

    def is_done(self, observation: str) -> bool:
        return "SUCCESS" in observation.upper()


class ImpossibleTaskAgent(Agent):
    def __init__(self, goal: str = "find_password_on_nonexistent_site"):
        self.goal = goal
        self._cycle = [
            "ERROR: DNS_RESOLUTION_FAILED",
            "RETRY: GOOGLE_SEARCH_NO_RESULTS",
            "RETRY: SCRAPER_TIMEOUT",
            "RETRY: GOOGLE_SEARCH_NO_RESULTS",
        ]
        self._step = 0
        self.last_observation = "START"

    def get_state(self) -> str:
        return "state=retry_loop"

    def act(self) -> str:
        observation = self._cycle[self._step % len(self._cycle)]
        self._step += 1
        self.last_observation = observation
        return observation

    def is_done(self, observation: str) -> bool:
        return False
