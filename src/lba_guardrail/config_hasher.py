"""Pure hashable configuration representation for an agent state and bounded tape."""

from typing import Tuple


def make_configuration(state: str, tape_snapshot: Tuple[str, ...]) -> Tuple[str, Tuple[str, ...]]:
    return (str(state), tuple(tape_snapshot))
