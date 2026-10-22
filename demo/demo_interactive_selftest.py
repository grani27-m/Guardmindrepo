"""Non-interactive self-test for the interactive demo — runs two queries
and prints full output automatically. Used for verification."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS
from lba_guardrail.agents.interactive_agent import InteractiveLookupAgent, KNOWN_ITEMS

TAPE_LENGTH = 4
MAX_STEPS = 20


def run_and_print(query: str) -> tuple[str, int]:
    agent = InteractiveLookupAgent(query)
    guardrail = LBAGuardrail(tape_length=TAPE_LENGTH)
    result = RAN_OUT_OF_STEPS
    final_step = MAX_STEPS

    print(f"\n{'='*60}")
    print(f"QUERY: '{query}'")
    print(f"{'='*60}")

    for step in range(1, MAX_STEPS + 1):
        state = agent.get_state()
        canonical_obs = agent.act()
        display_text = agent.last_display_text

        print(f"  Step {step:02d} | display (shown to human) : {display_text}")
        print(f"         | canonical obs (on tape) : {canonical_obs!r}")

        if agent.is_done(canonical_obs):
            result = SUCCESS
            final_step = step
            break

        can_continue = guardrail.step(state, canonical_obs)
        print(f"         | tape snapshot           : {guardrail.tape.snapshot()}")
        print(f"         | configs seen so far     : {len(guardrail.seen_configurations)}")

        if not can_continue:
            result = HALTED_BY_LBA
            final_step = step
            print(f"  -> GUARDRAIL FIRED: {guardrail.halt_reason}")
            break

    print(f"\nFINAL RESULT : {result}")
    print(f"steps taken  : {final_step}")
    return result, final_step


if __name__ == "__main__":
    # --- Test 1: known query ---
    r1, s1 = run_and_print("product-101")
    assert r1 == SUCCESS and s1 == 1, f"FAIL: expected SUCCESS at step 1, got {r1} at step {s1}"
    print("ASSERTION PASSED: known query -> SUCCESS in 1 step")

    # --- Test 2: unknown query ---
    r2, s2 = run_and_print("product-999")
    assert r2 == HALTED_BY_LBA, f"FAIL: expected HALTED_BY_LBA, got {r2}"
    assert s2 <= TAPE_LENGTH + 2, f"FAIL: expected halt within {TAPE_LENGTH+2} steps, took {s2}"
    print(f"ASSERTION PASSED: unknown query -> HALTED_BY_LBA at step {s2}")

    print("\n*** Both self-tests PASSED ***")
