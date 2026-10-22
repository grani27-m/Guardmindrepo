"""Protected demo: same impossible loop is caught by the LBA guardrail."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lba_guardrail.agents.mock_agent import ImpossibleTaskAgent
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import HALTED_BY_LBA, run_with_guardrail


if __name__ == "__main__":
    agent = ImpossibleTaskAgent()
    guardrail = LBAGuardrail(tape_length=4)
    result = run_with_guardrail(agent, guardrail, max_steps=20)
    print(f"result={result}")
    print(f"halted={guardrail.halted}")
    print(f"halt_reason={guardrail.halt_reason}")
    if result == HALTED_BY_LBA:
        print("repeated configuration detected by guardrail")
