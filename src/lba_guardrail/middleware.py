"""Wrap an agent loop with an optional LBA guardrail."""

from typing import Optional

from .agents.base_agent import Agent
from .automaton import LBAGuardrail

SUCCESS = "SUCCESS"
HALTED_BY_LBA = "HALTED_BY_LBA"
RAN_OUT_OF_STEPS = "RAN_OUT_OF_STEPS"


def run_with_guardrail(agent: Agent, guardrail: Optional[LBAGuardrail], max_steps: int = 30):
    for _ in range(max_steps):
        state = agent.get_state()
        observation = agent.act()

        if agent.is_done(observation):
            return SUCCESS

        if guardrail is not None and guardrail.step(state, observation) is False:
            return HALTED_BY_LBA

    return RAN_OUT_OF_STEPS
