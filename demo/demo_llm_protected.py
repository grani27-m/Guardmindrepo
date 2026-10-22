"""LLM-protected demo: runs LLMAgent (real Groq) through the LBA guardrail.

Each step prints exactly which path act() took:
  PATH=GROQ_API   → a real HTTP call was made to Groq
  PATH=FALLBACK   → no key / import failed / exception

Run:
    python demo/demo_llm_protected.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")  # make GROQ_API_KEY available

from lba_guardrail.agents.llm_agent import LLMAgent
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import HALTED_BY_LBA, RAN_OUT_OF_STEPS, SUCCESS, run_with_guardrail

TAPE_LENGTH = 4
MAX_STEPS = 20


def _step_hook(guardrail: LBAGuardrail, step_num: int, state: str, observation: str) -> None:
    """Print guardrail state after each step."""
    tape = guardrail.tape.snapshot()
    config_count = len(guardrail.seen_configurations)
    print(
        f"  [guardrail step={step_num}] "
        f"tape={tape}  configs_seen={config_count}  halted={guardrail.halted}"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("LBA GUARDRAIL — LLM AGENT DEMO (verbose)")
    print("=" * 70)

    import os
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key and api_key != "fake-key":
        print(f"GROQ_API_KEY loaded  OK  (last 6 chars: ...{api_key[-6:]})")
    else:
        print("GROQ_API_KEY not found - agent will use FALLBACK path for every step")

    print(f"tape_length={TAPE_LENGTH}  max_steps={MAX_STEPS}")
    print("-" * 70)

    agent = LLMAgent(goal="find_nonexistent_resource", api_key=api_key or None)
    guardrail = LBAGuardrail(tape_length=TAPE_LENGTH)

    # Run manually so we can print each step
    step_num = 0
    result = None
    for _ in range(MAX_STEPS):
        step_num += 1
        print(f"\nStep {step_num}:")
        state = agent.get_state()
        print(f"  state={state!r}")

        observation = agent.act()          # prints PATH=GROQ_API or PATH=FALLBACK
        print(f"  observation={observation!r}")

        if agent.is_done(observation):
            result = SUCCESS
            print(f"  -> agent.is_done=True  RESULT=SUCCESS")
            break

        safe = guardrail.step(state, observation)
        _step_hook(guardrail, step_num, state, observation)

        if not safe:
            result = HALTED_BY_LBA
            print(f"  -> guardrail fired!  RESULT=HALTED_BY_LBA")
            break
    else:
        result = RAN_OUT_OF_STEPS

    print("\n" + "=" * 70)
    print(f"FINAL RESULT  : {result}")
    print(f"halted        : {guardrail.halted}")
    print(f"halt_reason   : {guardrail.halt_reason}")
    print(f"steps_taken   : {step_num}")
    print(f"configs_seen  : {len(guardrail.seen_configurations)}")
    print("=" * 70)
