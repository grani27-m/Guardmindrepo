"""Create benchmark charts for the report."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


CSV_PATH = Path(__file__).resolve().parents[1] / "report_assets" / "benchmark_results.csv"
FIGURE_DIR = Path(__file__).resolve().parents[1] / "report_assets" / "figures"


if __name__ == "__main__":
    FIGURE_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    summary = df.groupby(["tape_length", "guardrail_on"], as_index=False)["steps_taken"].mean()

    baseline = summary[summary["guardrail_on"] == False]
    protected = summary[summary["guardrail_on"] == True]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(["Baseline", "Protected"], [baseline["steps_taken"].mean(), protected["steps_taken"].mean()], color=["#d62728", "#2ca02c"])
    ax.set_title("Average steps to halt")
    ax.set_ylabel("Steps")
    plt.tight_layout()
    fig.savefig(FIGURE_DIR / "avg_steps_to_halt.png")

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    protected_by_length = protected.groupby("tape_length")["steps_taken"].mean()
    ax2.plot(protected_by_length.index, protected_by_length.values, marker="o")
    ax2.set_title("Average steps to detect loop by tape length")
    ax2.set_xlabel("Tape length")
    ax2.set_ylabel("Detected steps")
    plt.tight_layout()
    fig2.savefig(FIGURE_DIR / "steps_vs_tape_length.png")

    print(f"Charts saved to {FIGURE_DIR}")
