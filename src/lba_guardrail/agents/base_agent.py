"""
Agent — the interface every agent (mock or real) must implement so the
middleware can wrap it generically.

TODO (Week 2): implement this ABC exactly as specified.
"""

from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def get_state(self) -> str:
        """Return a string identifying the agent's current state
        (e.g. f"goal={self.goal}|last={self.last_observation}")."""
        ...

    @abstractmethod
    def act(self) -> str:
        """Take one action (e.g. call a tool) and return the observation
        (string) that resulted from it."""
        ...

    @abstractmethod
    def is_done(self, observation: str) -> bool:
        """Return True if `observation` indicates the task succeeded."""
        ...
