import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS
from lba_guardrail.agents.real_search_agent import RealSearchAgent

TAPE_LENGTH = 4
MAX_STEPS = 20

def run_real_search(query: str):
    agent = RealSearchAgent(query)
    guardrail = LBAGuardrail(tape_length=TAPE_LENGTH)
    result = RAN_OUT_OF_STEPS
    final_step = MAX_STEPS

    print(f"\n{'='*60}")
    print(f"REAL WEB SEARCH QUERY: '{query}'")
    print(f"{'='*60}")

    for step in range(1, MAX_STEPS + 1):
        state = agent.get_state()
        canonical_obs = agent.act()
        display_text = agent.last_display_text

        print(f"  Step {step:02d} | action: {display_text}")
        
        if agent.is_done(canonical_obs):
            result = SUCCESS
            final_step = step
            break

        can_continue = guardrail.step(state, canonical_obs)
        if not can_continue:
            result = HALTED_BY_LBA
            final_step = step
            print(f"  -> GUARDRAIL FIRED: {guardrail.halt_reason}")
            break

    print(f"\nFINAL RESULT : {result}")
    print(f"steps taken  : {final_step}")
    return result

if __name__ == "__main__":
    run_real_search("asdfqwerzxcv998877665544332211 this is a totally fake string for duckduckgo to fail on")
