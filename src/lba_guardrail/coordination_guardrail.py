"""
Multi-Agent Coordination Loop Detection

Motivation: your current guardrail watches ONE agent's execution. But
real "agentic" systems increasingly involve MULTIPLE agents handing
tasks to each other (e.g. a "router" agent delegates to a "specialist"
agent, which decides it can't help and delegates back). Each individual
agent's own state might look fine in isolation -- neither agent alone
repeats a configuration -- but the CONVERSATION between them can still
be an infinite ping-pong loop.

This requires a second automaton layer that watches the sequence of
HANDOFFS between agents, not just one agent's internal steps. This is
conceptually the multi-agent generalization we discussed earlier
(and is the natural bridge to Petri nets for modeling true concurrency --
noted at the bottom as future work, since two agents strictly
alternating turns can be modeled as an LBA over the handoff sequence,
but genuinely concurrent/parallel agents would need a richer model
like a Petri net to represent correctly).
"""

from collections import deque
from typing import Tuple, Optional, List
from abc import ABC, abstractmethod


class BoundedTape:
    def __init__(self, tape_length: int = 4):
        self._tape = deque(maxlen=tape_length)

    def append(self, x) -> None:
        self._tape.append(x)

    def snapshot(self) -> Tuple:
        return tuple(self._tape)


class SubAgent(ABC):
    """A single specialist agent that can either resolve a task or
    decide to hand it off to another named agent."""
    name: str

    @abstractmethod
    def handle(self, task: str, context: str) -> Tuple[str, Optional[str]]:
        """Returns (result_or_new_context, handoff_target_or_None).
        If handoff_target is None, the task is resolved (SUCCESS)."""
        ...


class RouterAgent(SubAgent):
    name = "Router"

    def handle(self, task: str, context: str):
        if "billing" in task:
            return "Routing to Billing", "Billing"
        if "technical" in task:
            return "Routing to Technical", "Technical"
        return f"RESOLVED: general answer for '{task}'", None


class BillingAgent(SubAgent):
    name = "Billing"

    def handle(self, task: str, context: str):
        # Deliberately can't actually resolve billing+technical mixed issues
        # -- bounces it back to the router, simulating a real coordination bug
        if "technical" in task:
            return "This is technical, not billing", "Router"
        return f"RESOLVED: billing answer for '{task}'", None


class TechnicalAgent(SubAgent):
    name = "Technical"

    def handle(self, task: str, context: str):
        if "billing" in task:
            return "This is billing, not technical", "Router"
        return f"RESOLVED: technical answer for '{task}'", None


class CoordinationGuardrail:
    """Watches the SEQUENCE of (current_agent, task) handoffs -- a second,
    higher-level LBA layered on top of individual agent execution."""

    def __init__(self, tape_length: int = 4):
        self.tape = BoundedTape(tape_length=tape_length)
        self.seen: set = set()
        self.halted = False
        self.halt_reason: Optional[str] = None
        self.handoff_log: List[str] = []

    def record_handoff(self, from_agent: str, to_agent: str, task: str) -> bool:
        if self.halted:
            return False
        hop = f"{from_agent}->{to_agent}"
        self.handoff_log.append(hop)
        self.tape.append(hop)
        config = (task, self.tape.snapshot())
        if config in self.seen:
            self.halted = True
            self.halt_reason = (
                f"Repeated handoff pattern for task '{task}': {self.tape.snapshot()} "
                f"has occurred before -- agents are ping-ponging this task "
                f"without ever resolving it."
            )
            return False
        self.seen.add(config)
        return True


def run_multi_agent_system(task: str, agents: dict, coordination_tape_length: int = 4,
                             max_hops: int = 20):
    guardrail = CoordinationGuardrail(tape_length=coordination_tape_length)
    current_agent_name = "Router"
    context = ""

    for hop_i in range(1, max_hops + 1):
        agent = agents[current_agent_name]
        result, next_agent_name = agent.handle(task, context)
        print(f"  Hop {hop_i}: [{current_agent_name}] -> {result}")

        if next_agent_name is None:
            return "SUCCESS", hop_i, result

        can_continue = guardrail.record_handoff(current_agent_name, next_agent_name, task)
        if not can_continue:
            print(f"  -> COORDINATION GUARDRAIL FIRED: {guardrail.halt_reason}")
            return "HALTED_BY_COORDINATION_LBA", hop_i, guardrail.halt_reason

        context = result
        current_agent_name = next_agent_name

    return "RAN_OUT_OF_HOPS", max_hops, None


if __name__ == "__main__":
    agents = {
        "Router": RouterAgent(),
        "Billing": BillingAgent(),
        "Technical": TechnicalAgent(),
    }

    print("### Scenario A: a normal, resolvable task ###")
    result, hops, info = run_multi_agent_system("billing question about my invoice", agents)
    print(f"RESULT: {result} in {hops} hop(s)\n")

    print("### Scenario B: a task that ping-pongs between two agents forever ###")
    print("(A task ambiguously tagged 'billing technical issue' -- Billing bounces")
    print(" it to Router as technical, Router sends it back to Billing, forever)")
    result, hops, info = run_multi_agent_system("billing technical issue", agents)
    print(f"RESULT: {result} in {hops} hop(s)")

    print("\nInterpretation for your report:")
    print("Neither Billing nor Technical individually 'loops' in the sense your")
    print("original single-agent guardrail checks -- each only sees ONE decision")
    print("per invocation. The loop is only visible at the coordination layer,")
    print("watching the SEQUENCE of handoffs. This is the natural multi-agent")
    print("generalization of your core theory: the same bounded-configuration,")
    print("pigeonhole-based argument, just applied to a different alphabet")
    print("(agent handoffs instead of raw observations).")
    print("")
    print("Future work note: this implementation assumes agents act one at a")
    print("time (sequential handoffs), which keeps it a straightforward LBA.")
    print("If agents ran concurrently and could interleave in complex ways, a")
    print("Petri net would be the more accurate formal model, since it natively")
    print("represents concurrent state and synchronization -- worth naming as")
    print("a future extension in your report's conclusion.")
