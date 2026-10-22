"""
metrics: track steps, (simulated or real) cost, and halt outcome per run.

Used by scripts/run_benchmark.py to build experimental validation data.
"""

from dataclasses import dataclass


@dataclass
class RunMetrics:
    steps_taken: int
    halted_by_lba: bool
    wall_clock_seconds: float
    estimated_cost: float = 0.0
