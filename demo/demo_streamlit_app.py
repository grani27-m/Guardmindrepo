"""Optional visual demo for the LBA guardrail — three modes:
  1. Solvable task agent   -> SUCCESS
  2. Impossible task agent -> HALTED_BY_LBA (mock, deterministic)
  3. Interactive lookup    -> SUCCESS (known item) or HALTED_BY_LBA (unknown)
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

import streamlit as st

from lba_guardrail.agents.mock_agent import ImpossibleTaskAgent, SolvableTaskAgent
from lba_guardrail.agents.interactive_agent import InteractiveLookupAgent, KNOWN_ITEMS
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import HALTED_BY_LBA, SUCCESS, run_with_guardrail

st.set_page_config(page_title="LBA Agent Guardrail Demo", layout="centered")
st.title("LBA Agent Guardrail Demo")
st.caption("Deterministic Infinite Loop Prevention using Linear Bounded Automata")

# ── Mode selector ──────────────────────────────────────────────────────────────
mode = st.selectbox(
    "Choose demo mode",
    ["Solvable Task", "Impossible Task (Mock Loop)", "Interactive Lookup"],
)

# ── Interactive mode ───────────────────────────────────────────────────────────
if mode == "Interactive Lookup":
    st.markdown(
        "**Known items:** " + ", ".join(f"`{k}`" for k in KNOWN_ITEMS.keys())
    )
    st.markdown("Type a known item key to see instant success, or anything else to watch the guardrail halt the loop.")

    query = st.text_input("Enter a query to look up:", placeholder="e.g. product-101  or  product-999")

    if st.button("Run lookup") and query.strip():
        agent = InteractiveLookupAgent(query.strip())
        guardrail = LBAGuardrail(tape_length=4)

        log_lines = []
        result_value = "RAN_OUT_OF_STEPS"
        final_step = 20

        for step in range(1, 21):
            state = agent.get_state()
            canonical_obs = agent.act()
            display_text = agent.last_display_text

            log_lines.append(
                f"**Step {step:02d}** | LLM/lookup: *{display_text}* | tape obs: `{canonical_obs}`"
            )

            if agent.is_done(canonical_obs):
                result_value = SUCCESS
                final_step = step
                break

            can_continue = guardrail.step(state, canonical_obs)
            log_lines.append(
                f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; tape: `{guardrail.tape.snapshot()}` | configs_seen: {len(guardrail.seen_configurations)}"
            )

            if not can_continue:
                result_value = HALTED_BY_LBA
                final_step = step
                log_lines.append(f"**-> GUARDRAIL FIRED:** {guardrail.halt_reason}")
                break

        st.markdown("\n\n".join(log_lines), unsafe_allow_html=True)
        st.divider()

        if result_value == SUCCESS:
            st.success(f"SUCCESS in {final_step} step(s) — item found.")
        elif result_value == HALTED_BY_LBA:
            st.error(
                f"HALTED_BY_LBA at step {final_step} — repeated (state, tape) configuration proven. "
                f"Loop terminated before wasting further API calls."
            )
        else:
            st.warning(f"Ran out of steps ({final_step}) without resolving.")

# ── Mock agent modes ───────────────────────────────────────────────────────────
else:
    if st.button("Run demo"):
        if mode == "Solvable Task":
            agent = SolvableTaskAgent()
            result = run_with_guardrail(agent, LBAGuardrail(tape_length=4), max_steps=10)
            st.write(f"Result: `{result}`")
            st.success("Task completed successfully.")
        else:
            agent = ImpossibleTaskAgent()
            guardrail = LBAGuardrail(tape_length=4)
            result = run_with_guardrail(agent, guardrail, max_steps=20)
            st.write(f"Result: `{result}`")
            if result == HALTED_BY_LBA:
                st.error(f"Guardrail triggered: {guardrail.halt_reason}")
            else:
                st.warning("The agent did not halt within the step cap.")
