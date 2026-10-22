"""Generate benchmark data for baseline vs protected runs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import csv
from lba_guardrail.agents.mock_agent import ImpossibleTaskAgent
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import HALTED_BY_LBA, RAN_OUT_OF_STEPS, run_with_guardrail

import time
from lba_guardrail.metrics import RunMetrics

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "report_assets" / "benchmark_results.csv"


def benchmark_for_tape_length(tape_length: int, trials: int = 5):
    rows = []
    for trial in range(1, trials + 1):
        # Baseline
        agent_baseline = ImpossibleTaskAgent()
        start_time = time.time()
        baseline_steps = 0
        while baseline_steps < 20:
            agent_baseline.get_state()
            agent_baseline.act()
            baseline_steps += 1
        baseline_duration = time.time() - start_time
        
        m_baseline = RunMetrics(
            steps_taken=baseline_steps,
            halted_by_lba=False,
            wall_clock_seconds=baseline_duration
        )

        # Protected
        agent_protected = ImpossibleTaskAgent()
        guardrail = LBAGuardrail(tape_length=tape_length)
        start_time = time.time()
        result = run_with_guardrail(agent_protected, guardrail, max_steps=20)
        protected_duration = time.time() - start_time
        
        m_protected = RunMetrics(
            steps_taken=20 if result == RAN_OUT_OF_STEPS else len(guardrail.history),
            halted_by_lba=(result == HALTED_BY_LBA),
            wall_clock_seconds=protected_duration
        )

        rows.append({
            "tape_length": tape_length,
            "guardrail_on": False,
            "trial_number": trial,
            "steps_taken": m_baseline.steps_taken,
            "halted_by_lba": m_baseline.halted_by_lba,
            "wall_clock_seconds": m_baseline.wall_clock_seconds,
        })
        rows.append({
            "tape_length": tape_length,
            "guardrail_on": True,
            "trial_number": trial,
            "steps_taken": m_protected.steps_taken,
            "halted_by_lba": m_protected.halted_by_lba,
            "wall_clock_seconds": m_protected.wall_clock_seconds,
        })
    return rows


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    rows = []
    for tape_length in [2, 4, 6, 8]:
        rows.extend(benchmark_for_tape_length(tape_length=tape_length, trials=5))

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tape_length", "guardrail_on", "trial_number", "steps_taken", "halted_by_lba", "wall_clock_seconds"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Benchmark saved to {OUTPUT_PATH}")
