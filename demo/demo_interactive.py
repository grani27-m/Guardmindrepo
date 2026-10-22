"""
Interactive LBA Guardrail Demo — terminal version.

Known queries succeed in 1 step.
Unknown queries get real Groq retry messages (displayed to you),
but the guardrail tracks only the canonical NOT_FOUND token on the tape,
so it reliably detects the repeated configuration and fires HALTED_BY_LBA.

Run:
    python demo/demo_interactive.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import (
    SUCCESS,
    HALTED_BY_LBA,
    RAN_OUT_OF_STEPS,
    run_with_guardrail,
)
from lba_guardrail.agents.interactive_agent import InteractiveLookupAgent, KNOWN_ITEMS


TAPE_LENGTH = 4
MAX_STEPS = 20


def _run_query(query: str) -> None:
    """Run one query through the guardrail and print a full step-by-step trace."""
    agent = InteractiveLookupAgent(query)
    guardrail = LBAGuardrail(tape_length=TAPE_LENGTH)

    print(f"\nRunning agent for query='{query}' ...")
    print(f"(tape_length={TAPE_LENGTH}, max_steps={MAX_STEPS})")
    print("-" * 60)

    # Drive the loop manually so we can print per-step output.
    result = RAN_OUT_OF_STEPS
    final_step = MAX_STEPS

    for step in range(1, MAX_STEPS + 1):
        state = agent.get_state()
        canonical_obs = agent.act()          # returns "FOUND" or "NOT_FOUND"
        display_text = agent.last_display_text  # Groq text or "FOUND: ..."

        print(f"  Step {step:02d} | display : {display_text}")
        print(f"         | tape obs: {canonical_obs!r}")

        if agent.is_done(canonical_obs):
            result = SUCCESS
            final_step = step
            break

        can_continue = guardrail.step(state, canonical_obs)
        print(f"         | tape    : {guardrail.tape.snapshot()}")
        print(f"         | configs : {len(guardrail.seen_configurations)}")

        if not can_continue:
            result = HALTED_BY_LBA
            final_step = step
            print(f"  -> GUARDRAIL FIRED: {guardrail.halt_reason}")
            break

    print("-" * 60)
    if result == SUCCESS:
        print(f"RESULT: SUCCESS in {final_step} step(s).")
    elif result == HALTED_BY_LBA:
        print(f"RESULT: HALTED_BY_LBA at step {final_step}. "
              f"Loop mathematically proven.")
    else:
        print(f"RESULT: RAN_OUT_OF_STEPS ({final_step}).")
    print()


def main() -> None:
    print("=" * 60)
    print("INTERACTIVE LBA GUARDRAIL DEMO")
    print("=" * 60)
    print("Known items:", ", ".join(KNOWN_ITEMS.keys()))
    print("Try an unknown one (e.g. 'product-999') to see the guardrail fire.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            query = input("Enter a query to look up: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        _run_query(query)


if __name__ == "__main__":
    main()
