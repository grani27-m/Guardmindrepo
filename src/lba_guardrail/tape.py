"""BoundedTape: a fixed-length memory window for the LBA configuration."""

from collections import deque
from typing import Tuple


class BoundedTape:
    def __init__(self, tape_length: int = 4):
        if tape_length <= 0:
            raise ValueError("tape_length must be positive")
        self.tape_length = tape_length
        self._tape = deque(maxlen=tape_length)

    def append(self, observation: str) -> None:
        self._tape.append(str(observation))

    def snapshot(self) -> Tuple[str, ...]:
        return tuple(self._tape)
