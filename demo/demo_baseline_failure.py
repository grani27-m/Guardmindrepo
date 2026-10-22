"""Baseline loop: impossible task never halts on its own."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lba_guardrail.agents.mock_agent import ImpossibleTaskAgent


if __name__ == "__main__":
    agent = ImpossibleTaskAgent()
    max_steps = 12
    for step in range(1, max_steps + 1):
        state = agent.get_state()
        observation = agent.act()
        print(f"step={step:02d} state={state} observation={observation}")
