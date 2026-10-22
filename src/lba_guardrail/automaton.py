"""LBAGuardrail detects repeated (state, bounded tape) configurations."""

from typing import Optional

from .config_hasher import make_configuration
from .tape import BoundedTape


class LBAGuardrail:
    def __init__(self, tape_length: int = 4):
        self.tape = BoundedTape(tape_length=tape_length)
        self.seen_configurations: set = set()
        self.halted: bool = False
        self.halt_reason: Optional[str] = None
        self.history: list = []

    def step(self, state: str, observation: str) -> bool:
        self.tape.append(observation)
        config = make_configuration(state, self.tape.snapshot())
        self.history.append({"state": state, "observation": observation, "config": config})

        if config in self.seen_configurations:
            self.halted = True
            self.halt_reason = "Repeated (state, tape) configuration detected; infinite loop proven."
            return False

        self.seen_configurations.add(config)
        return True

    def max_theoretical_configurations(self, num_states: int, alphabet_size: int) -> int:
        n = self.tape.tape_length
        return num_states * n * (alphabet_size ** n)
