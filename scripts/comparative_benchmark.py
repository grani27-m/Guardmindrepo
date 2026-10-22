"""
Comparative Benchmark: LBA Guardrail vs. Two Naive Baselines
"""

import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lba_guardrail.agents.base_agent import Agent
from lba_guardrail.tape import BoundedTape


# ---------------------------------------------------------------------
# Test agents
# ---------------------------------------------------------------------

class GenuineProgressAgent(Agent):
    """Takes exactly `total_steps` DISTINCT actions, then succeeds.
    Represents a legitimate, long-but-not-stuck agent."""
    def __init__(self, total_steps: int = 15):
        self.total_steps = total_steps
        self.i = 0

    def get_state(self) -> str:
        return f"progress_task|i={self.i}"

    def act(self) -> str:
        self.i += 1
        if self.i >= self.total_steps:
            return "SUCCESS"
        return f"working_on_subtask_{self.i}"

    def is_done(self, observation: str) -> bool:
        return observation == "SUCCESS"

    def reset(self):
        self.i = 0


class StuckAgent(Agent):
    """Cycles through a fixed period-p sequence of distinct observations
    forever, never succeeding."""
    def __init__(self, period: int = 3):
        self.period = period
        self.i = 0
        self.cycle = [f"ERROR_TYPE_{chr(65+k)}" for k in range(period)]

    def get_state(self) -> str:
        return "stuck_task"

    def act(self) -> str:
        obs = self.cycle[self.i % self.period]
        self.i += 1
        return obs

    def is_done(self, observation: str) -> bool:
        return False

    def reset(self):
        self.i = 0


# ---------------------------------------------------------------------
# The three halting strategies
# ---------------------------------------------------------------------

def run_timeout(agent: Agent, cutoff: int, max_steps: int = 50):
    agent.reset()
    for i in range(1, max_steps + 1):
        obs = agent.act()
        if agent.is_done(obs):
            return "SUCCESS", i
        if i >= cutoff:
            return "TIMEOUT_HALT", i
    return "RAN_OUT_OF_STEPS", max_steps


def run_repeat_counter(agent: Agent, max_steps: int = 50):
    agent.reset()
    last_obs = None
    for i in range(1, max_steps + 1):
        obs = agent.act()
        if agent.is_done(obs):
            return "SUCCESS", i
        if obs == last_obs:
            return "REPEAT_COUNTER_HALT", i
        last_obs = obs
    return "RAN_OUT_OF_STEPS", max_steps


def run_lba_guardrail(agent: Agent, tape_length: int = 4, max_steps: int = 50):
    agent.reset()
    tape = BoundedTape(tape_length=tape_length)
    seen = set()
    for i in range(1, max_steps + 1):
        state = agent.get_state()
        obs = agent.act()
        if agent.is_done(obs):
            return "SUCCESS", i
        tape.append(obs)
        config = (state, tape.snapshot())
        if config in seen:
            return "LBA_HALT", i
        seen.add(config)
    return "RAN_OUT_OF_STEPS", max_steps


# ---------------------------------------------------------------------
# Run the comparison
# ---------------------------------------------------------------------

def main():
    scenarios = [
        ("GenuineProgress(15 steps)", GenuineProgressAgent(total_steps=15)),
        ("StuckAgent(period=1)", StuckAgent(period=1)),
        ("StuckAgent(period=3)", StuckAgent(period=3)),
        ("StuckAgent(period=5)", StuckAgent(period=5)),
    ]

    rows = []
    print(f"{'Scenario':<28} {'Method':<20} {'Result':<22} {'Steps':<6} {'Verdict'}")
    print("-" * 95)

    ACTIVE_HALT = {"TIMEOUT_HALT", "REPEAT_COUNTER_HALT", "LBA_HALT"}

    for name, agent in scenarios:
        is_genuine = "GenuineProgress" in name

        # Timeout baseline
        result, steps = run_timeout(agent, cutoff=10)
        if is_genuine:
            verdict = "CORRECT" if result == "SUCCESS" else "WRONG (killed legitimate work early)"
        else:
            verdict = "Halts eventually, but blind to real vs fake progress"
        rows.append([name, "TIMEOUT(cutoff=10)", result, steps, verdict])

        # Repeat-counter baseline
        result, steps = run_repeat_counter(agent)
        if is_genuine:
            verdict = "CORRECT" if result == "SUCCESS" else "WRONG"
        else:
            verdict = "CORRECT (detected)" if result in ACTIVE_HALT else "FAILED -- never detected the loop at all"
        rows.append([name, "REPEAT_COUNTER", result, steps, verdict])

        # Your LBA guardrail
        result, steps = run_lba_guardrail(agent, tape_length=4)
        if is_genuine:
            verdict = "CORRECT" if result == "SUCCESS" else "WRONG"
        else:
            verdict = "CORRECT (proven, not guessed)" if result in ACTIVE_HALT else "FAILED"
        rows.append([name, "LBA_GUARDRAIL", result, steps, verdict])

    for r in rows:
        print(f"{r[0]:<28} {r[1]:<20} {r[2]:<22} {r[3]:<6} {r[4]}")

    out_path = ROOT / "report_assets" / "comparative_benchmark_results.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario", "method", "result", "steps", "verdict"])
        writer.writerows(rows)
    print(f"\nSaved: {out_path}")

    print("\n--- Did the method itself actually detect the loop? (stuck scenarios only) ---")
    for method in ["TIMEOUT(cutoff=10)", "REPEAT_COUNTER", "LBA_GUARDRAIL"]:
        stuck_rows = [r for r in rows if r[1] == method and "Stuck" in r[0]]
        n_detected = sum(1 for r in stuck_rows if r[2] in ACTIVE_HALT)
        avg_steps = sum(r[3] for r in stuck_rows if r[2] in ACTIVE_HALT) / max(n_detected, 1)
        print(f"{method:<20}: detected {n_detected}/{len(stuck_rows)} stuck scenarios"
              f"{f', avg {avg_steps:.1f} steps to detect' if n_detected else ''}")

if __name__ == "__main__":
    main()
