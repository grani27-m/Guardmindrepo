"""
Adaptive Tape Length

Motivation: a fixed tape_length is a blunt instrument. Too short, and
loops with a longer period take longer to detect (or in pathological
cases, detection is delayed unnecessarily). Too long, and you waste
memory/comparison cost on simple loops that would have been caught fast
with a small tape.

This variant starts SMALL and grows the tape only if the agent has gone
`patience` steps without either succeeding or being caught -- capped at
`max_tape_length` so it remains a valid, bounded LBA (still decidable,
just adaptively so). This is still fundamentally an LBA: the bound is
just chosen dynamically instead of fixed up front.

IMPORTANT theoretical note for your report: growing the tape does NOT
violate the LBA model. An LBA's defining property is that its tape is
bounded by SOME linear function of the input -- not that the bound is
static across all runs. As long as max_tape_length is finite and fixed
in advance, decidability still holds.
"""

from collections import deque
from typing import Tuple, Optional


class AdaptiveBoundedTape:
    def __init__(self, initial_length: int = 2, max_length: int = 10):
        self.max_length = max_length
        self.length = initial_length
        self._tape = deque(maxlen=initial_length)

    def append(self, observation: str) -> None:
        self._tape.append(observation)

    def snapshot(self) -> Tuple[str, ...]:
        return tuple(self._tape)

    def grow(self, growth: int = 2) -> bool:
        """Grow the tape, preserving existing contents. Returns False if
        already at max_length (cannot grow further -- still bounded)."""
        if self.length >= self.max_length:
            return False
        new_length = min(self.length + growth, self.max_length)
        old_contents = list(self._tape)
        self._tape = deque(old_contents, maxlen=new_length)
        self.length = new_length
        return True


class AdaptiveLBAGuardrail:
    def __init__(self, initial_tape_length: int = 2, max_tape_length: int = 10,
                 growth_step: int = 2, patience: int = 8):
        self.tape = AdaptiveBoundedTape(initial_tape_length, max_tape_length)
        self.patience = patience
        self.growth_step = growth_step
        self.seen_configurations: set = set()
        self.steps_since_growth = 0
        self.halted = False
        self.halt_reason: Optional[str] = None
        self.growth_events: list = []  # for reporting: when did we grow, and to what

    def step(self, state: str, observation: str) -> bool:
        if self.halted:
            return False

        self.tape.append(observation)
        config = (state, self.tape.snapshot())

        if config in self.seen_configurations:
            self.halted = True
            self.halt_reason = (
                f"Repeated configuration at tape_length={self.tape.length}: {config}"
            )
            return False

        self.seen_configurations.add(config)
        self.steps_since_growth += 1

        # No repeat found in `patience` steps at the current tape length --
        # the loop period (if any) may be longer than what we can currently
        # see. Grow the tape (still bounded by max_tape_length) and reset
        # the patience counter. Note: growing invalidates old configurations
        # for comparison purposes (different tape length = different key
        # space), so we clear seen_configurations on grow.
        if self.steps_since_growth >= self.patience:
            grew = self.tape.grow(self.growth_step)
            if grew:
                self.growth_events.append({
                    "new_length": self.tape.length,
                    "at_config_count": len(self.seen_configurations),
                })
                self.seen_configurations.clear()
            self.steps_since_growth = 0

        return True


# ---------------------------------------------------------------------
# Demonstration: a loop whose period is LONGER than a small fixed tape
# ---------------------------------------------------------------------

class LongPeriodStuckAgent:
    """A stuck agent whose repeating cycle has period 6 -- longer than a
    small initial tape_length=2 could ever capture directly."""
    def __init__(self, period: int = 6):
        self.period = period
        self.i = 0
        self.cycle = [f"STATE_{k}" for k in range(period)]

    def get_state(self) -> str:
        return "long_period_task"

    def act(self) -> str:
        obs = self.cycle[self.i % self.period]
        self.i += 1
        return obs

    def is_done(self, observation: str) -> bool:
        return False


def run_fixed_small_tape(agent, tape_length=2, max_steps=60):
    from collections import deque as dq
    tape = dq(maxlen=tape_length)
    seen = set()
    for i in range(1, max_steps + 1):
        state = agent.get_state()
        obs = agent.act()
        tape.append(obs)
        config = (state, tuple(tape))
        if config in seen:
            return "LBA_HALT", i
        seen.add(config)
    return "RAN_OUT_OF_STEPS", max_steps


def run_adaptive(agent, initial_tape_length=2, max_tape_length=10,
                  growth_step=2, patience=8, max_steps=60):
    guardrail = AdaptiveLBAGuardrail(initial_tape_length, max_tape_length, growth_step, patience)
    for i in range(1, max_steps + 1):
        state = agent.get_state()
        obs = agent.act()
        can_continue = guardrail.step(state, obs)
        if not can_continue:
            return "LBA_HALT", i, guardrail.growth_events
    return "RAN_OUT_OF_STEPS", max_steps, guardrail.growth_events


if __name__ == "__main__":
    print("=" * 78)
    print("RESULT 1: Empirical validation of steps_to_detect = tape_length + period")
    print("=" * 78)
    from collections import deque as _dq

    def _detect(period, tape_length, max_steps=60):
        tape = _dq(maxlen=tape_length)
        seen = set()
        for i in range(1, max_steps + 1):
            obs = f"S{i % period}"
            tape.append(obs)
            config = ("const_state", tuple(tape))
            if config in seen:
                return i
            seen.add(config)
        return None

    for p in [1, 3, 5, 9]:
        for n in [2, 4, 10]:
            actual = _detect(p, n)
            predicted = n + p
            print(f"  period={p:<3} tape_length={n:<3} -> detected step {actual:<3} "
                  f"(formula predicts {predicted}, match={'YES' if actual == predicted else 'NO'})")

    print("\nInterpretation: for a purely periodic stuck agent, a SMALLER tape")
    print("detects the loop FASTER, not slower -- this is the opposite of the")
    print("naive assumption that 'more memory finds problems faster'. A bigger")
    print("tape is more selective (less prone to false alarms) but costs more")
    print("steps before its first full window, so genuine detection latency")
    print("is HIGHER, not lower. This is a real, useful empirical result for")
    print("your report, and it's why adaptive growth should NOT be framed as")
    print("'grow the tape to catch harder loops faster' -- that's false. See")
    print("RESULT 2 below for what adaptive growth is actually good for.\n")

    print("=" * 78)
    print("RESULT 2: The REAL justification for adaptive tape -- avoiding")
    print("          false positives on legitimate repeated-but-progressing work")
    print("=" * 78)

    class PollingAgent:
        """Simulates a common, entirely legitimate pattern: submitting a job
        and polling its status. It's normal for two consecutive polls to
        return the exact same 'still processing' observation before the
        job genuinely completes. A too-small tape can mistake this for a
        loop and halt a perfectly healthy agent."""
        def __init__(self, polls_before_done: int = 3):
            self.polls_before_done = polls_before_done
            self.i = 0

        def get_state(self) -> str:
            return "job_status_check"  # legitimately constant while polling

        def act(self) -> str:
            self.i += 1
            if self.i >= self.polls_before_done:
                return "DONE"
            return "STILL_PROCESSING"  # legitimately repeats each poll

        def is_done(self, observation: str) -> bool:
            return observation == "DONE"

    def run_with_tape_length(agent, tape_length, max_steps=20):
        tape = _dq(maxlen=tape_length)
        seen = set()
        for i in range(1, max_steps + 1):
            state = agent.get_state()
            obs = agent.act()
            if agent.is_done(obs):
                return "SUCCESS", i
            tape.append(obs)
            config = (state, tuple(tape))
            if config in seen:
                return "FALSE_POSITIVE_HALT", i
            seen.add(config)
        return "RAN_OUT_OF_STEPS", max_steps

    for tl in [1, 2, 3]:
        agent = PollingAgent(polls_before_done=3)
        result, steps = run_with_tape_length(agent, tape_length=tl)
        verdict = "CORRECT" if result == "SUCCESS" else "FALSE POSITIVE -- killed a healthy agent!"
        print(f"  tape_length={tl} -> {result} at step {steps}   [{verdict}]")

    print("\nInterpretation: tape_length=1 cannot distinguish 'still processing'")
    print("(poll #1) from 'still processing' (poll #2) -- both produce the same")
    print("single-element tape, so the guardrail falsely concludes a loop and")
    print("kills a perfectly healthy, legitimately-polling agent. tape_length=2+")
    print("correctly avoids this because it sees enough context to tell the")
    print("difference. THIS is the real argument for not under-sizing the tape,")
    print("and for adaptive growth as a safety margin when you're not sure what")
    print("tape length is safe to pick up front for a new, unfamiliar agent.")

